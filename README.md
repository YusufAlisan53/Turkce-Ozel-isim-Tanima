# Türkçe Özel İsim Tanıma (NER) - Web Uygulaması

Bu proje, doğal dil işleme alanında geliştirilmiş, Türkçe metinler üzerindeki özel isimleri (Named Entity Recognition - NER) yüksek isabet oranıyla tespit eden Flask tabanlı bir web uygulamasıdır. 

Derin öğrenme destekli güçlü bir dil modeli ve **Türk Dil Kurumu (TDK) yazım kurallarını** temel alan gelişmiş bir filtreleme altyapısı sayesinde, makine öğrenmesinin kaçırdığı veya yanlış etiketlediği kelimeler mantıksal kurallarla düzeltilir.

## 🚀 Son Güncellemeler ve Yenilikler (V2)

1. **Genişletilmiş Etiket Sistemi (19 Kategori)**
   - Sadece Kişi, Kurum, Yer değil; Millet, Unvan, Dil, Para Birimi, Kanun/Tüzük, Eser Adı gibi 19 farklı ince etiket eklendi.
   - `girayyagmur/bert-base-turkish-ner-cased` (Turkish WikiNER) modeli kullanıldı.
2. **Akıllı Subword Birleştirme**
   - Yapay zekanın "Kâzım" ("Kâ" + "##zım") veya "Hopa" ("Hop" + "##a") gibi kelimeleri parçalaması sonucu oluşan hatalar giderildi.
3. **TDK Kurallarıyla Gelişmiş Post-Processing**
   - **Gezegenler:** Güneş, Dünya, Ay kelimeleri bağlam (uzay, yörünge vb.) analiz edilerek doğru sınıflandırılır.
   - **Müzikal Roller:** "Vokal", "gitar", "bas gitar" gibi unvan sanılan kelimeler TDK kuralları gereği elenir.
   - **Anlam Kayması:** Amper, jul, allahlık, donkişotluk gibi anlam kaymasına uğramış özel kelimelerin etiketleri kaldırılır.
4. **Müzik Grupları ve Müzik Türleri Algoritması**
   - Modelin eğitim verisinde bulunmayan Rock, Grunge, Arabesk, Halk müziği gibi akım ve türler büyük harfle başladıklarında özel isim sayılarak **Sanat/Müzik Türü (TÜR)** olarak tespit edilir.
   - Modelin "Kişi" sandığı müzik grupları (Örn: Duman), devamında "grubu, rock, müzik" geçiyorsa otomatik olarak **Kurum (ORG)** olarak düzeltilir.
5. **Kapsamlı Skor Optimizasyonu**
   - Az bilinen isimlerin "Düşük Güven Skoru" nedeniyle yok sayılmasını önlemek için filtreler kaldırıldı; yanlış etiketlemeler sadece TDK dil bilgisi algoritmasıyla yönetildi.

## 🛠️ Kurulum ve Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install flask transformers torch numpy
   ```
2. Uygulamayı başlatın:
   ```bash
   python app.py
   ```
3. Tarayıcınızda otomatik olarak açılacaktır (veya `http://127.0.0.1:5000` adresine gidebilirsiniz).
   *İlk çalıştırmada yapay zeka modeli (yaklaşık 400 MB) otomatik olarak indirilecektir.*

## 💻 Kullanılan Teknolojiler
- **Backend:** Python, Flask, HuggingFace Transformers
- **Model:** BERT (BertForTokenClassification)
- **Frontend:** HTML5, CSS3 (Modern, karanlık tema, cam efekti), Vanilla JS

## 📝 Yazar
- **Öğrenci:** Yusuf Talha Alişan (210260027)
- **Ders:** Doğal Dil İşleme
