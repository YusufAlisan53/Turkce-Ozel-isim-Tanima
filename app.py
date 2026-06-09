"""
Turkce Ozel Isim Tanima (NER) - Flask Backend
Ders: Dogal Dil Isleme
Öğrenci: Yusuf Talha Alişan - 210260027

Kullanılan Model: girayyagmur/bert-base-turkish-ner-cased
  Eğitim Verisi : turkish-nlp-suite/turkish-wikiNER (19 ince etiket)
  Desteklenen etiketler:
    PERSON, LOC, GPE, ORG, FAC,
    NORP, LANGUAGE, EVENT, DATE, TIME,
    LAW, WORK_OF_ART, PRODUCT, TITLE,
    CARDINAL, ORDINAL, QUANTITY, MONEY, PERCENT

TDK Büyük Harf Kurallarına göre post-processing katmanı uygulanır.
"""

import re
import sys
import io
import threading
import webbrowser
import time

# Konsol çıktısını UTF-8 yap (zaten sarmalanmışsa atla)
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

app = Flask(__name__)

# Model yükleme
MODEL_NAME = "girayyagmur/bert-base-turkish-ner-cased"

print(f"[*] Model yukleniyor: {MODEL_NAME}")
print("    Ilk calistirmada model internetten indirilecek (~400 MB), lutfen bekleyin...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
)

print("[OK] Model hazir!\n")

# Etiket haritası  (19 ince etiket → Türkçe karşılık + renk)
# TDK kural referansları yorum satırında belirtilmiştir.
LABEL_MAP = {
    "PERSON":    {"tr": "Kişi",          "color": "#a78bfa"},  # C.1-2
    "TITLE":     {"tr": "Unvan",         "color": "#c084fc"},  # C.2-4
    "NORP":      {"tr": "Millet/Topluluk","color": "#f472b6"}, # C.6, C.9 (millet, din mensupları)

    "LOC":       {"tr": "Yer",           "color": "#34d399"},  # C.13-17
    "GPE":       {"tr": "Ülke/Şehir",   "color": "#2dd4bf"},  # C.8, C.13

    "ORG":       {"tr": "Kurum",         "color": "#fb923c"},  # C.18
    "FAC":       {"tr": "Yapı/Tesis",   "color": "#f97316"},  # C.16

    "LANGUAGE":  {"tr": "Dil Adı",      "color": "#22d3ee"},  # C.7

    "EVENT":     {"tr": "Olay/Dönem",   "color": "#facc15"},  # C.22, C.24
    "LAW":       {"tr": "Kanun/Tüzük", "color": "#a3e635"},  # C.19

    "WORK_OF_ART":{"tr": "Eser Adı",   "color": "#38bdf8"},  # C.21

    "PRODUCT":   {"tr": "Ürün",         "color": "#94a3b8"},
    "DATE":      {"tr": "Tarih",        "color": "#e879f9"},
    "TIME":      {"tr": "Zaman",        "color": "#c026d3"},
    "CARDINAL":  {"tr": "Sayı",         "color": "#64748b"},
    "ORDINAL":   {"tr": "Sıra Sayısı", "color": "#64748b"},
    "QUANTITY":  {"tr": "Miktar",       "color": "#64748b"},
    "MONEY":     {"tr": "Para Miktarı","color": "#64748b"},
    "PERCENT":   {"tr": "Yüzde",       "color": "#64748b"},
}

TDK_MUZIK_TUR_MAKAM = {
    # Makamlar
    "acem aşiran", "acembuşelik", "bayati", "hicazkâr", "hicaz",
    "nihavent", "uşşak", "rast", "segah", "saba", "karcığar",
    "mahur", "buşelik", "çargah", "neva", "pençgah", "şehnaz",
    "acem", "nihavend",
    # Türler / formlar
    "semai", "gazel", "kaside", "arabesk",
}

TDK_MUZIK_ALETI_ROL = {
    "vokal", "gitar", "bas", "davul", "klavye", "keman", "viyola",
    "çello", "flut", "obua", "trompet", "trombon", "saksofon",
    "perkuşyon", "bateri", "org", "piyano", "bazar", "ney", "ud",
    "saz", "bağlama", "kanun", "zurna", "davul", "def", "kudüm",
    "geri vokal", "bas gitar", "ritim gitar", "elektro gitar",
    "vokal ve gitar", "geri vokal ve gitar", "geri vokal ve bas gitar",
}

TDK_PARA_BIRIMLERI = {
    "avro", "dinar", "dolar", "lira", "kuruş", "liret",
    "frank", "sterlin", "yen", "ruble", "won", "yuan",
}

# TDK Kural C.25 UYARI: Özel ad kendi anlamı dışında yeni anlam kazanmış kelimeler
TDK_ANLAM_KAYMASI = {
    "allahlık", "donkişotluk", "jul", "amper", "volt", "watt",
    "newton", "hertz", "pascal", "ohm", "tesla",
}

APOSTROPHE_CHARS = frozenset({"'", "\u2019", "\u2018", "`"})

MUSIC_GENRES = {
    "rock", "grunge", "alternatif", "alternatif rock", "arabesk", "halk", "halk müziği",
    "pop", "caz", "blues", "klasik", "klasik müzik", "rap", "hip hop", "metal",
    "heavy metal", "indie", "punk", "reggae", "sanat müziği", "türkü"
}

LABEL_MAP["TÜR"] = {"tr": "Sanat/Müzik Türü", "color": "#f43f5e"}

def _is_standalone_word(text: str, start: int, end: int, word: str) -> bool:
    prev_char = text[start - 1] if start > 0 else ""
    next_char = text[end] if end < len(text) else ""

    if prev_char.isalpha() or prev_char in APOSTROPHE_CHARS:
        return False

    if next_char.isalpha():
        w = word.strip()
        if len(w) <= 4:
            return False
        if w and w[0].islower():
            return False

    return True

def _word_lower_nocase(word: str) -> str:
    """Türkçe büyük/küçük harf dönüşümü (İ→i, I→ı vb.)"""
    return (word
            .replace("İ", "i")
            .replace("I", "ı")
            .replace("Ğ", "ğ")
            .replace("Ü", "ü")
            .replace("Ş", "ş")
            .replace("Ö", "ö")
            .replace("Ç", "ç")
            .lower())


def tdk_postprocess(entities: list, text: str) -> list:
    result = []
    for ent in entities:
        word = ent["word"]
        word_lower = _word_lower_nocase(word)
        label = ent["label"]

        if word_lower in TDK_MUZIK_TUR_MAKAM:
            # Bağlam kontrolü: ardından organizasyon sözcüğü var mı?
            end_pos = ent["end"]
            following = text[end_pos:end_pos + 30].lower()
            org_keywords = ("festivali", "derneği", "vakfı", "müzik",
                            "konseri", "topluluğu", "ekibi", "yarışması")
            if any(kw in following for kw in org_keywords):
                # → Bu durumda ORG/EVENT olarak tut
                result.append(ent)
            else:
                # → Özel isim değil, çıkar
                continue

        elif word_lower in TDK_MUZIK_ALETI_ROL:
            continue

        elif word_lower in TDK_PARA_BIRIMLERI:
            if label == "MONEY":
                result.append(ent)
            # else: ORG/MISC vs. etiketlenmişse çıkar
            continue

        elif word_lower in TDK_ANLAM_KAYMASI:
            continue

        elif word_lower in ("güneş", "dünya", "ay") and label in ("LOC", "PRODUCT", "ORG"):
            # Büyük harfle başlamıyorsa gezegen anlamında değil
            if not word[0].isupper():
                continue
            # Büyük harfle başlıyorsa → bağlam kontrolü
            start_pos = ent["start"]
            preceding = text[max(0, start_pos - 20):start_pos].lower()
            geo_keywords = ("merkez", "uzay", "nasa", "ay'a", "güneş'e",
                            "güneşin", "dünya'nın", "gezegenimiz")
            if not any(kw in preceding for kw in geo_keywords):
                continue
            result.append(ent)

        else:
            result.append(ent)

    for ent in result:
        if ent["label"] in ("PERSON", "PER"):
            end_pos = ent["end"]
            following = text[end_pos:end_pos + 60].lower()
            if "grubu" in following or "rock" in following or "band" in following:
                ent["label"] = "ORG"
                ent["label_tr"] = LABEL_MAP["ORG"]["tr"]
                ent["color"] = LABEL_MAP["ORG"]["color"]

    return result


def merge_entities(raw_entities: list, text: str) -> list:
    raw_entities.sort(key=lambda e: e["start"])
    merged_raw = []
    for e in raw_entities:
        if merged_raw and merged_raw[-1]["end"] == e["start"] and merged_raw[-1]["entity_group"] == e["entity_group"]:
            # Bitişik ve aynı etiketli -> birleştir
            merged_raw[-1]["end"] = e["end"]
            merged_raw[-1]["word"] = text[merged_raw[-1]["start"]:e["end"]]
            merged_raw[-1]["score"] = max(merged_raw[-1]["score"], float(e["score"]))
        else:
            merged_raw.append(e)

    sorted_ents = sorted(merged_raw, key=lambda e: e["score"], reverse=True)
    accepted = []
    used_ranges = []

    for ent in sorted_ents:
        start, end = ent["start"], ent["end"]
        overlap = any(s < end and start < e for s, e in used_ranges)
        if not overlap:
            accepted.append(ent)
            used_ranges.append((start, end))

    accepted.sort(key=lambda e: e["start"])

    normalized = []
    for ent in accepted:
        start = ent["start"]
        end   = ent["end"]
        word  = text[start:end].strip()
        if not word:
            continue

        for ap in APOSTROPHE_CHARS:
            ap_idx = word.find(ap)
            if ap_idx > 0:
                word = word[:ap_idx]
                end  = start + ap_idx
                break

        if word and word[0] in APOSTROPHE_CHARS:
            continue

        if not _is_standalone_word(text, start, end, word):
            continue


        raw_label = ent["entity_group"].replace("B-", "").replace("I-", "").upper()
        info = LABEL_MAP.get(raw_label, {"tr": raw_label, "color": "#94a3b8"})
        normalized.append({
            "word":     word,
            "label":    raw_label,
            "label_tr": info["tr"],
            "color":    info["color"],
            "score":    round(float(ent["score"]), 4),
            "start":    start,
            "end":      end,
        })

    normalized = tdk_postprocess(normalized, text)
    return normalized

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Metin boş olamaz."}), 400
    if len(text) > 5000:
        return jsonify({"error": "Metin 5000 karakterden uzun olamaz."}), 400

    raw = ner_pipeline(text)
    entities = merge_entities(raw, text)

    import re
    existing_spans = [(e["start"], e["end"]) for e in entities]
    
    for genre in MUSIC_GENRES:
        # Metinde kelime sınırlarıyla ara (büyük/küçük harf duyarsız arayıp, orijinalin büyük harfle başladığını kontrol edeceğiz)
        pattern = r'\b' + re.escape(genre) + r'\b'
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = match.span()
            matched_text = text[start:end]
            
            if matched_text[0].isupper():
                overlap = any(s < end and start < e for s, e in existing_spans)
                if not overlap:
                    entities.append({
                        "word": matched_text,
                        "label": "TÜR",
                        "label_tr": LABEL_MAP["TÜR"]["tr"],
                        "color": LABEL_MAP["TÜR"]["color"],
                        "score": 1.0,
                        "start": start,
                        "end": end
                    })
                    existing_spans.append((start, end))

    entities.sort(key=lambda e: e["start"])

    stats = {}
    for ent in entities:
        key = ent["label_tr"]
        stats[key] = stats.get(key, 0) + 1

    return jsonify({
        "text":     text,
        "entities": entities,
        "stats":    stats,
        "total":    len(entities),
    })


if __name__ == "__main__":
    # Sunucu hazır olunca tarayıcıyı otomatik aç
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(debug=False, port=5000, use_reloader=False)
