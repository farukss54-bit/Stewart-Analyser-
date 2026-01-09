# 🩸 Stewart Asit-Baz Analizi

Fizikokimyasal yaklaşımla kan gazı değerlendirmesi için Streamlit uygulaması.

## v3.2 - Architecture Refactor & Visualization

### 🏗️ Mimari Değişiklikler

**1. Modüler Yapı**
```
stewart_analyzer/
├── app.py              # Ana orchestrator (minimal)
├── core.py             # Hesaplama motoru
├── constants.py        # Sabitler ve konfigürasyon
├── ui_components.py    # UI bileşenleri (yeni)
├── visualization.py    # Plotly grafikleri (yeni)
├── validation.py       # Input validation (yeni)
├── logger.py           # Logging module (yeni)
├── test_core.py        # Core testleri
├── test_validation.py  # Edge case testleri (yeni)
├── Dockerfile          # Container (yeni)
└── requirements.txt
```

**2. Centralized Validation (`validation.py`)**
- `sanitize_numeric()`: Dirty input temizleme (virgül decimal, whitespace, NaN)
- `validate_input_dict()`: Dictionary validation
- `validate_csv_row()`: CSV satır validation (swapped columns detection)
- `detect_albumin_unit()`: Otomatik birim algılama (g/dL vs g/L)

**3. Logging (`logger.py`)**
- `log_user_action()`: INFO - kullanıcı aksiyonları
- `log_calculation_warning()`: WARNING - yaklaşık hesaplamalar
- `log_analysis_error()`: ERROR - başarısız analizler (sanitized)

### 📊 Görselleştirme (Yeni!)

**Gamblegram**
- Plazma elektrolit dengesi görselleştirmesi
- Katyonlar (Na⁺, K⁺, Ca²⁺, Mg²⁺) vs Anyonlar (Cl⁻, HCO₃⁻, Laktat, A⁻, SIG)
- Plotly interactive chart

**Contribution Bar Chart**
- Mekanizma katkılarının yatay bar grafiği
- Asidoz (kırmızı) vs Alkaloz (mavi)

**SID Waterfall**
- SID hesaplama adımları waterfall chart
- SID_simple → SID_basic → SID_full

### 🔬 v3.1 Özellikleri (Korundu)

**Contribution-Based Primary Disorder Detection**
- Dominant mekanizma mutlak mEq/L katkısına göre belirlenir
- Sadece varlığa değil, katkı oranına bakılır

**Lactate Contribution Classification**
- <25% katkı → "contributing"
- 25-50% katkı → "significant"
- >50% katkı → "dominant"

**Non-Diagnostic, Mechanism-Based Language**
- ❌ "Ketoasidoz" → ✅ "Ölçülmemiş anyon aracılı metabolik asidoz"
- ❌ "Laktik asidoz" → ✅ "Laktat aracılı metabolik asidoz"

**SID Table Interpretation Column**
- Low SID → "Güçlü iyon aracılı metabolik asidoz yönünde"
- High SID → "Güçlü iyon aracılı metabolik alkaloz yönünde"

## Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker

```bash
docker build -t stewart-analyzer .
docker run -p 8501:8501 stewart-analyzer
```

## Test

```bash
# Tüm testler
pytest -v

# Sadece validation testleri
pytest test_validation.py -v

# Coverage ile
pytest --cov=. --cov-report=html
```

## Kullanım

### Hızlı Mod
- Minimum parametrelerle analiz
- BE tabanlı bileşen ayrıştırması

### Gelişmiş Mod
- SIG hesabı (SIDa - SIDe)
- Atot hesabı
- Tam mekanizma analizi

### Batch Modu
- CSV upload
- Toplu analiz
- Sonuç export

## Dosya Yapısı

| Dosya | Açıklama |
|-------|----------|
| `app.py` | Streamlit UI orchestrator |
| `core.py` | Hesaplama motoru, dataclass'lar |
| `constants.py` | Sabitler, eşikler, mesajlar |
| `ui_components.py` | UI render fonksiyonları |
| `visualization.py` | Plotly grafikleri |
| `validation.py` | Input validation |
| `logger.py` | Logging utilities |

## Katkıda Bulunma

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest -v`
4. Submit a pull request

## Lisans

MIT License

## Referanslar

- Stewart PA. Modern quantitative acid-base chemistry. Can J Physiol Pharmacol. 1983
- Fencl V, Leith DE. Stewart's quantitative acid-base chemistry. Respir Physiol. 1993
- Morgan TJ. The Stewart approach. Clinica Chimica Acta. 2019

---

*Bu araç fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir.*
