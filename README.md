# 🩸 Stewart Asit-Baz Analizi

Fizikokimyasal yaklaşımla kan gazı değerlendirmesi için Streamlit uygulaması.

## Özellikler

### Hesaplama Modları

**Hızlı (Klinik) Mod:**
- Fencl-derived Residual yaklaşımı
- BE tabanlı bileşen analizi
- Acil serviste pratik kullanım için optimize edilmiş

**Gelişmiş Mod:**
- SIDapparent ve SIDeffective hesabı
- SIG = SIDa - SIDe (pozitif → ölçülmemiş anyonlar)
- SIG güvenilirlik değerlendirmesi
- Atot hesabı

### 3 Katmanlı SID Gösterimi

- **SID_simple:** Na - Cl
- **SID_basic:** Na - Cl - Laktat
- **SID_full (SIDa):** (Na + K + Ca + Mg) - (Cl + Laktat)

### Ek Özellikler

- ✅ BE/HCO₃ otomatik hesaplama ve tutarlılık kontrolü
- ✅ CSV export/import (batch analiz)
- ✅ Eksik parametre uyarıları (varsayım yapılmaz!)
- ✅ Birim dönüşümü (g/L ↔ g/dL)
- ✅ Genişletilmiş kompanzasyon (akut/kronik respiratuvar dahil)
- ✅ Kural tabanlı dominant disorder belirleme
- ✅ Kapsamlı validasyon (tüm parametreler için)

## Kurulum

```bash
# Gerekli paketleri kur
pip install -r requirements.txt

# Uygulamayı çalıştır
python -m streamlit run app.py

# veya
streamlit run app.py
```

## Proje Yapısı

```
stewart_analyzer/
├── app.py          # Streamlit UI
├── core.py         # Hesaplama motoru
├── constants.py    # Sabitler ve normal aralıklar
├── test_core.py    # Pytest testleri
├── requirements.txt
└── README.md
```

## Testler

```bash
# Tüm testleri çalıştır
pytest test_core.py -v

# Coverage ile
pytest test_core.py --cov=core --cov-report=html
```

## Formüller

### SID Hesabı
- **Basit:** SID = Na - Cl (Normal: ~38 mEq/L)
- **Tam:** SIDa = (Na + K + Ca + Mg) - (Cl + Laktat)

### SIG Hesabı
```
SIG = SIDapparent - SIDeffective
```
- Pozitif SIG → Ölçülmemiş anyonlar (HAGMA)
- Negatif SIG → Ölçülmemiş katyonlar (nadir)

### BE Hesabı
```
BE ≈ 0.93 × (HCO₃ − 24.4) + 14.8 × (pH − 7.40)
```

### Kompanzasyon (Winter's)
```
Beklenen pCO₂ = 1.5 × HCO₃ + 8 (± 2)
```

## Referanslar

- Stewart PA. Modern quantitative acid-base chemistry. Can J Physiol Pharmacol. 1983
- Morgan TJ. The Stewart approach. Clinica Chimica Acta. 2019
- Story DA. Stewart acid–base. Anaesthesia and Intensive Care. 2016
- Akoğlu H. Olgularla Kan Gazı Değerlendirmesi

## Uyarı

⚠️ **Bu araç eğitim amaçlıdır.** Klinik karar için mutlaka uzman değerlendirmesi gereklidir.

## Lisans

MIT License

## Versiyon

2.0.0 - Core-UI ayrımı, batch modu, gelişmiş validasyon
