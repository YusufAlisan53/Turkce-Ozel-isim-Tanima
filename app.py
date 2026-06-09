# -*- coding: utf-8 -*-
"""
Turkce Ozel Isim Tanima (NER) - Flask Backend
Ders: Dogal Dil Isleme
Öğrenci: Yusuf Talha Alişan - 210260027

Kullanılan Model: savasy/bert-base-turkish-ner-cased
  - PER  → Kişi adları
  - LOC  → Yer adları (şehir, ülke, bölge vb.)
  - ORG  → Kurum / organizasyon adları
"""

import sys
import io
import os
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

# ---------------------------------------------------------------------------
# Model yükleme
# ---------------------------------------------------------------------------
MODEL_NAME = "savasy/bert-base-turkish-ner-cased"

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

# ---------------------------------------------------------------------------
# Etiket eşleşmeleri  (modelin çıktısı → Türkçe kategori)
# ---------------------------------------------------------------------------
LABEL_MAP = {
    "PER": {"tr": "Kişi",   "en": "PER", "color": "#a78bfa"},   # mor
    "LOC": {"tr": "Yer",    "en": "LOC", "color": "#34d399"},   # yeşil
    "ORG": {"tr": "Kurum",  "en": "ORG", "color": "#fb923c"},   # turuncu
    "MISC":{"tr": "Diğer",  "en": "MISC","color": "#60a5fa"},   # mavi
}

def get_label_info(raw_label: str) -> dict:
    """'B-PER', 'I-LOC' gibi etiketleri normalize eder."""
    clean = raw_label.replace("B-", "").replace("I-", "").upper()
    return LABEL_MAP.get(clean, {"tr": clean, "en": clean, "color": "#94a3b8"})


# ---------------------------------------------------------------------------
# Çakışan / tekrar eden varlıkları temizle
# ---------------------------------------------------------------------------
def merge_entities(raw_entities: list, text: str) -> list:
    """
    Aggregation sonrası hâlâ çakışan span'leri temizler ve
    her varlığa orijinal metinden gerçek 'word' değerini atar.
    """
    # Skora göre büyükten küçüğe sırala, çakışanları at
    sorted_ents = sorted(raw_entities, key=lambda e: e["score"], reverse=True)
    accepted = []
    used_ranges = []

    for ent in sorted_ents:
        start, end = ent["start"], ent["end"]
        overlap = any(s < end and start < e for s, e in used_ranges)
        if not overlap:
            accepted.append(ent)
            used_ranges.append((start, end))

    # Metindeki konuma göre sırala
    accepted.sort(key=lambda e: e["start"])

    result = []
    for ent in accepted:
        word = text[ent["start"]:ent["end"]].strip()
        if not word:
            continue
        label_info = get_label_info(ent["entity_group"])
        result.append({
            "word":    word,
            "label":   label_info["en"],
            "label_tr":label_info["tr"],
            "color":   label_info["color"],
            "score":   round(float(ent["score"]), 4),
            "start":   ent["start"],
            "end":     ent["end"],
        })
    return result


# ---------------------------------------------------------------------------
# Rotalar
# ---------------------------------------------------------------------------
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

    # NER
    raw = ner_pipeline(text)
    entities = merge_entities(raw, text)

    # İstatistik
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
