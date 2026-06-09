<div align="center">

# 🇹🇷 Türkçe Özel İsim Tanıma (NER)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3%2B-000000?style=flat-square&logo=flask&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗-BERT_Turkish_NER-FFD21E?style=flat-square)

> 🎓 Doğal Dil İşleme Dersi — Yusuf Talha Alişan (210260027)

</div>

Türkçe metinlerdeki **kişi (PER)**, **yer (LOC)** ve **kurum (ORG)** adlarını [`savasy/bert-base-turkish-ner-cased`](https://huggingface.co/savasy/bert-base-turkish-ner-cased) BERT modeliyle otomatik tanıyan Flask web uygulaması.

## 🚀 Çalıştırma

**Windows:** `calistir.bat` dosyasına çift tıklayın — bağımlılıklar otomatik kurulur, tarayıcı açılır.

**Manuel:**
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

> İlk çalıştırmada model HuggingFace'den otomatik indirilir (~400 MB).

## 📁 Yapı

```
├── app.py              ← Flask backend + NER pipeline
├── requirements.txt
├── calistir.bat        ← Çift tıkla başlatıcı (Windows)
└── templates/
    └── index.html      ← Web arayüzü
```

## 🛠️ Teknolojiler

- **Model:** BERT fine-tuned (Türkçe NER)
- **Backend:** Python · Flask
- **Frontend:** HTML · CSS · Vanilla JS
