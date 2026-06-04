# 🩸 Stewart Asit-Baz Analizi

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stewart-analyzer.streamlit.app)
[![Tests](https://img.shields.io/badge/tests-156%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

**Stewart-Fencl fizikokimyasal yaklaşımı** ile kan gazı değerlendirmesi yapan, eğitim odaklı web uygulaması.

> ⚕️ **Bu araç fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir.** Eğitim amaçlıdır. Tüm klinik kararlar uzman hekim değerlendirmesi gerektirir.

---

## 🎯 Proje Nedir?

Klasik asit-baz analizinin (Henderson-Hasselbalch, anyon gap) ötesinde, **güçlü iyon farkı (SID)** ve **zayıf asitler (Atot)** kavramlarına dayalı fizikokimyasal bir yaklaşım sunar.

### Kimler İçin?
- 🏥 **Acil tıp / yoğun bakım hekimleri** — karmaşık asit-baz bozukluklarını hızlıca analiz etme
- 📚 **Tıp öğrencileri ve asistanlar** — hazır vakalar ve literatür referanslarıyla öğrenme
- 🔬 **Araştırmacılar** — batch CSV analizi ve literatür tabanlı eşik değerler

### Neden Stewart?
- Klasik yaklaşımın göremediği **maskelenmiş asidozları** (örn. hipoalbüminemi + asidoz) ortaya çıkarır
- **Karışık (mikst) bozuklukları** ayırt eder
- Her bileşenin **mEq/L katkısını** kantifiye eder
- **Ölçülmemiş anyon (SIG)** etkisini hesaplar

---

## 🚀 Özellikler

### Analiz Modları
| Mod | Açıklama |
|-----|----------|
| **Hızlı** | Minimum parametreler (pH, pCO₂, Na, Cl). BE tabanlı bileşen ayrıştırması. |
| **Gelişmiş** | Tam Stewart analizi: SIDa, SIDe, SIG, Atot. Tam mekanizma analizi. |

### Girdi Yöntemleri
- ✏️ **Manuel giriş** — Hızlı veya gelişmiş form
- 📂 **Batch CSV** — Toplu analiz, satır satır validasyon
- 📚 **Hazır Vakalar** — Eğitim amaçlı vakalar (Akoğlu vakaları dahil)

### Çıktılar
- 📋 **Headline** — Tek cümlelik klinik özet
- 📊 **Temel Değerler** — pH, pCO₂, HCO₃, BE (emoji + ok + renk kodlaması)
- 📈 **SID Tablosu** — 3 katmanlı SID (simple / basic / full)
- 🧮 **Katkı Ayrıştırma** — Her mekanizmanın BE'ye mEq/L ve % katkısı
- 📉 **Grafikler** — Gamblegram, katkı bar grafiği, SID waterfall, pH gauge
- 💡 **CDS Notları** — Kategorili (A/B/C) klinik karar destek ipuçları
- ⚖️ **Klasik Karşılaştırma** — Stewart vs. klasik yaklaşım farkları

---

## 🛠️ Kurulum

### Yerel Geliştirme
```bash
# Repoyu klonla
git clone https://github.com/farukss54-bit/Stewart-Analyser-.git
cd Stewart-Analyser-

# Bağımlılıkları kur
pip install -r requirements.txt

# Uygulamayı başlat
streamlit run app.py
```
Uygulama varsayılan olarak `http://localhost:8501` adresinde açılır.

### Docker
```bash
docker build -t stewart-analyzer .
docker run -p 8501:8501 stewart-analyzer
```

### VS Code / GitHub Codespaces
`.devcontainer/devcontainer.json` mevcuttur. Açıldığında bağımlılıklar otomatik yüklenir.

---

## 🧪 Test

```bash
# Tüm testler
pytest -v

# Belirli test dosyaları
pytest test_core.py -v
pytest test_validation.py -v
pytest test_regression.py -v

# Coverage
pytest --cov=. --cov-report=html
```

---

## 📁 Dosya Yapısı

```
.
├── app.py              # Streamlit UI orchestrator
├── core.py             # Hesaplama motoru (~1700 satır)
├── constants.py        # Klinik sabitler, eşikler, hazır vakalar (~1100 satır)
├── ui_components.py    # UI render fonksiyonları
├── visualization.py    # Plotly grafikleri
├── validation.py       # 3-katmanlı validasyon, Na/Cl swap tespiti
├── logger.py           # Yapılandırılmış loglama (PHI içermez)
├── test_core.py        # Birim testleri
├── test_validation.py  # Edge case testleri
├── test_regression.py  # Regresyon testleri
├── test_regression_fixed.py
├── test_simple.py      # Smoke testleri
├── test_sprint4.py     # Sprint 4 testleri
├── requirements.txt    # Bağımlılıklar
├── Dockerfile          # Üretim konteyneri
├── docs/
│   ├── AGENTS.md       # Ajan rehberi (AI geliştiriciler için)
│   └── BE_FORMUL_RAPORU.txt  # BE formül doğrulama raporu
└── README.md           # Bu dosya
```

---

## 📖 Kullanım

### Hızlı Mod
1. Sidebar'dan "Hızlı (Klinik)" seç
2. pH, pCO₂, Na, Cl gir
3. İsteğe bağlı: K, laktat, albümin
4. "Analiz Et" butonuna tıkla

### Gelişmiş Mod
1. Sidebar'dan "Gelişmiş" seç
2. Tüm parametreleri gir (Ca, Mg, fosfat dahil)
3. SIG hesaplaması ve tam mekanizma analizi gör

### Hazır Vakalar
1. Sidebar'dan "📚 Hazır Vakalar" bölümünden vaka seç
2. "🔄 Değerleri Yükle" butonuna tıkla
3. Eğitim notunu ve klasik karşılaştırmayı incele

### Batch Analiz
1. CSV dosyası yükle (her satır bir hasta)
2. Otomatik validasyon ve analiz
3. Sonuçları indir

---

## 🔬 Literatür Referansları

Proje aşağıdaki literatüre dayanmaktadır:

- **Stewart PA.** Modern quantitative acid-base chemistry. *Can J Physiol Pharmacol.* 1983
- **Figge J, Mydosh T, Fencl V.** Serum proteins and acid-base equilibria. *J Lab Clin Med.* 1991
- **Fencl V, Jabor A, Kazda A, Figge J.** Diagnosis of metabolic acid-base disturbances. *Am J Respir Crit Care.* 2000
- **Morgan TJ.** The Stewart approach. *Crit Care Clin.* 2009
- **Kellum JA.** Disorders of acid-base balance. *Crit Care Med.* 2009
- **Berend K, et al.** Physiological approach to assessment of acid-base disturbances. *NEJM.* 2014
- **Story DA.** Stewart acid-base: A simplified bedside approach. *Anesth Analg.* 2016

**Klinik vaka katkıları:** Doç. Dr. Haldun Akoğlu — Marmara Üniversitesi Acil Tıp AD.

---

## 🤝 Katkıda Bulunma

1. Repoyu fork'la
2. Feature branch oluştur: `git checkout -b feature/yeni-ozellik`
3. Testleri çalıştır: `pytest -v` (156 test yeşil olmalı)
4. Pull request gönder

AGENTS.md dosyasını okuyarak proje kurallarını, mimarisini ve sık karşılaşılan tuzakları öğrenebilirsiniz.

---

## ⚕️ Yasal Uyarı

Bu uygulama **eğitim amaçlıdır** ve fizyolojik mekanizmaları tanımlar. Tanı koymaz, tedavi önerisi vermez. Tüm klinik kararlar uzman hekim değerlendirmesi gerektirir.

---

## 📜 Lisans

MIT License

---

*🇬🇧 [English version → README_EN.md](README_EN.md)*
