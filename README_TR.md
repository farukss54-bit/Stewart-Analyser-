# 🩸 Stewart Asit-Baz Analizi

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stewart-analyzer.streamlit.app)
[![Tests](https://github.com/farukss54-bit/Stewart-Analyser-/actions/workflows/tests.yml/badge.svg)](https://github.com/farukss54-bit/Stewart-Analyser-/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

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
- 📚 **Hazır Vakalar** — Eğitim amaçlı vakalar

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

## 🖥️ React/Next.js arayüzü (deneysel)

Streamlit uygulamasının yanında ikinci bir ön yüz bulunur. Hesaplama çekirdeği (`core.py`) ortaktır ve değiştirilmemiştir: web arayüzü yalnızca çekirdeğin döndürdüğünü gösterir, klinik değer hesaplamaz.

- `api/` — durumsuz FastAPI katmanı (`/api/analyze`, `/api/batch`, `/api/cases`, `/api/references`, …); `core.py`, `validation.py` ve `services.py`'yi çağırır
- `web/` — Next.js (App Router, TypeScript) arayüzü: hızlı ve gelişmiş mod, hazır vakalar, klasik karşılaştırma, tekli ve toplu CSV, grafikler, referanslar, açık/koyu tema, telefon/tablet düzeni

```bash
pip install -r requirements.txt -r api/requirements.txt
cd web && npm install && cd ..

# Windows: API (8000) ve web (3000) birlikte başlar
.\scripts\dev.ps1

# Her sistemde: iki terminal
uvicorn api.main:app --port 8000
cd web && npm run dev          # http://localhost:3000
```

Testler: `pytest` API'yi de kapsar; web testleri `cd web && npm test`, ayrıca `npm run lint` ve `npm run build`. CI ikisini de çalıştırır (`.github/workflows/tests.yml`). TypeScript tipleri API şemasından üretilir (`python scripts/export_openapi.py`, ardından `cd web && npm run api:tipleri`); güncel değilse CI hata verir.

Streamlit uygulaması referans uygulama ve çevrimiçi demo olarak kalır. React arayüzü henüz herkese açık olarak yayınlanmamıştır.

---

## 🧪 Test

```bash
# Tüm testler
pytest -v

# Belirli test dosyaları
pytest tests/test_core.py -v
pytest tests/test_validation.py -v
pytest tests/test_regression.py -v
pytest tests/test_cds_differential.py -v
pytest tests/test_ui_imports.py -v
pytest tests/test_api.py tests/test_api_batch.py tests/test_services.py tests/test_app_bd.py -v

# Web arayüzü
cd web && npm test

# Coverage
pytest --cov=. --cov-report=html
```

---

## 📁 Dosya Yapısı

```
.
├── app.py              # Streamlit UI orchestrator
├── core.py             # Hesaplama motoru
├── constants.py        # Klinik sabitler, eşikler, hazır vakalar
├── services.py         # Streamlit ve API'nin ortak, çerçevesiz yardımcıları
├── ui_components.py    # UI render fonksiyonları
├── visualization.py    # Plotly grafikleri
├── validation.py       # 3-katmanlı validasyon, Na/Cl swap tespiti
├── logger.py           # Yapılandırılmış loglama (PHI içermez)
├── api/                # React arayüzü için FastAPI katmanı
├── web/                # Next.js (React) arayüzü
├── scripts/            # dev.ps1 (API + web birlikte), export_openapi.py
├── tests/
│   ├── test_api.py, test_api_batch.py  # HTTP API testleri (çekirdekle altın testler)
│   ├── test_app_bd.py            # Streamlit BD kutusu davranışı (AppTest)
│   ├── test_cds_differential.py  # CDS diferansiyel modül testleri
│   ├── test_core.py              # Birim testleri
│   ├── test_regression.py        # Regresyon testleri
│   ├── test_services.py          # Ortak servis fonksiyonları
│   ├── test_ui_imports.py        # UI import duman testleri
│   └── test_validation.py        # Edge case testleri
├── requirements.txt    # Bağımlılıklar (Streamlit uygulaması)
├── Dockerfile          # Üretim konteyneri (Streamlit)
├── docs/
│   ├── AGENTS.md       # Ajan rehberi (AI geliştiriciler için)
│   └── BE_FORMUL_RAPORU.txt  # BE formül doğrulama raporu
├── README.md           # İngilizce sürüm
└── README_TR.md        # Bu dosya
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

- **Stewart PA.** Modern quantitative acid-base chemistry. *Can J Physiol Pharmacol.* 1983;61(12):1444-61. PMID 6423247
- **Figge J, Mydosh T, Fencl V.** Serum proteins and acid-base equilibria: a follow-up. *J Lab Clin Med.* 1992;120(5):713-9. PMID 1431499
- **Fencl V, Jabor A, Kazda A, Figge J.** Diagnosis of metabolic acid-base disturbances in critically ill patients. *Am J Respir Crit Care Med.* 2000;162(6):2246-51. PMID 11112147
- **Morgan TJ.** The Stewart approach: one clinician's perspective. *Clin Biochem Rev.* 2009;30(2):41-54. PMID 19565024
- **Kellum JA.** Disorders of acid-base balance. *Crit Care Med.* 2007;35(11):2630-6. PMID 17893626
- **Berend K, de Vries APJ, Gans ROB.** Physiological approach to assessment of acid-base disturbances. *N Engl J Med.* 2014;371(15):1434-45. PMID 25295502
- **Story DA.** Stewart acid-base: a simplified bedside approach. *Anesth Analg.* 2016;123(2):511-5. PMID 27140683

---

## 🤝 Katkıda Bulunma

1. Repoyu fork'la
2. Feature branch oluştur: `git checkout -b feature/yeni-ozellik`
3. Testleri çalıştır: `pytest -v` (tüm testler yeşil olmalı)
4. Pull request gönder

AGENTS.md dosyasını okuyarak proje kurallarını, mimarisini ve sık karşılaşılan tuzakları öğrenebilirsiniz.

---

## ⚕️ Yasal Uyarı

Bu uygulama **eğitim amaçlıdır** ve fizyolojik mekanizmaları tanımlar. Tanı koymaz, tedavi önerisi vermez. Tüm klinik kararlar uzman hekim değerlendirmesi gerektirir.

---

## 📜 Lisans

MIT License

---

*🇬🇧 [English version → README.md](README.md)*
