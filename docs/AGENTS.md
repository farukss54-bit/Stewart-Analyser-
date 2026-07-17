# AGENTS.md — Stewart Asit-Baz Analizi

> Bu dosya, AI kodlama ajanlarının projeyi hızlıca anlaması ve doğru değişiklikler yapması için yazılmıştır. Proje hakkında ön bilgisi olmayan bir ajanın ihtiyaç duyacağı tüm kritik bilgiler burada toplanmıştır.

---

## 1. Proje Özeti

**Ad:** Stewart Asit-Baz Analizi  
**Versiyon:** v3.5.0 (`__init__.py`'de 3.4.0 olarak görünebilir)  
**Tür:** Streamlit tabanlı web uygulaması  
**Amaç:** Kan gazı sonuçlarını Stewart-Fencl fizikokimyasal yaklaşımı ile analiz eden eğitim ve klinik karar destek aracı.  
**Dil:** Türkçe (kod yorumları, docstring'ler, UI metinleri, dokümantasyon tamamen Türkçedir).  
**Kritik Uyarı:** Bu araç tanı koymaz ve tedavi önerisi vermez. Eğitim amaçlıdır. Tüm çıktılarda "fizyolojik mekanizma tanımlar; tanı veya tedavi önerisi değildir" anlayışı hakimdir.

---

## 2. Teknoloji Yığını (Technology Stack)

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| Dil | Python | 3.11+ |
| Web UI | Streamlit | >=1.28.0 |
| Veri İşleme | Pandas, NumPy | >=2.0.0, >=1.24.0 |
| Görselleştirme | Plotly | >=5.18.0 |
| Test | pytest, pytest-cov | >=7.4.0, >=4.1.0 |
| Konteyner | Docker | python:3.11-slim |
| IDE | VS Code / GitHub Codespaces | devcontainer.json mevcut |

**Not:** `pyproject.toml`, `setup.py` veya `package.json` yoktur. Proje düz `requirements.txt` ile yönetilir.

---

## 3. Proje Yapısı

Tüm kaynak dosyalar proje kökündedir (flat yapı). Alt dizin yoktur.

```
.
├── app.py              # Ana UI orchestrator — Streamlit sayfa yapısı, batch mod, sidebar
├── core.py             # Hesaplama motoru — ~1700 satır, tüm dataclass'lar ve analiz mantığı
├── constants.py        # Sabitler — ~1100 satır, eşik değerler, literatür referansları, hazır vakalar, UI metinleri
├── ui_components.py    # UI bileşenleri — Streamlit render fonksiyonları, değer göstergeleri
├── visualization.py    # Görselleştirme — Plotly grafikleri (Gamblegram, SID waterfall, katkı grafiği, pH gauge)
├── validation.py       # Validasyon — Girdi temizleme, 3-katmanlı validasyon, CSV satır validasyonu, Na/Cl swap tespiti
├── logger.py           # Loglama — Yapılandırılmış log fonksiyonları, klinik bağlam desteği
├── test_core.py        # Birim testleri — Temel hesaplama, SID, SIG, katkı analizi, headline
├── test_validation.py  # Edge case testleri — Kirli girdi, CSV işleme, birim algılama
├── test_regression.py  # Regresyon testleri — Kritik düzeltmelerin doğrulanması
├── test_regression_fixed.py  # Düzeltilmiş regresyon testleri
├── test_simple.py      # Smoke testleri
├── test_sprint4.py     # Sprint 4'e özel testler
├── requirements.txt    # Bağımlılıklar
├── Dockerfile          # Üretim konteyneri
└── .devcontainer/devcontainer.json  # VS Code / Codespaces yapılandırması
```

### Modül Sorumlulukları

- **`app.py`**: Streamlit sayfa konfigürasyonu, sidebar (mod seçimi, hazır vakalar, batch mod), hızlı/gelişmiş analiz formları, batch CSV işleme, türetilmiş değerler (HCO3/BE) doğrulama bölümü. `core.py`'den `analyze_stewart()`'ı çağırır, `ui_components.py`'den render fonksiyonlarını kullanır.
- **`core.py`**: Projenin en büyük ve en kritik dosyası. `StewartInput`, `StewartOutput`, `SIDValues`, `MechanismAnalysis`, `Headline`, `CDSNote` gibi tüm dataclass'ları içerir. `analyze_stewart()` ana fonksiyonu buradadır. SIG hesaplama, kompanzasyon değerlendirmesi, dominant bozukluk tespiti, mekanizma analizi, headline oluşturma tamamen bu dosyadadır.
- **`constants.py`**: Tüm klinik eşik değerler (pH, pCO2, elektrolitler, SID, SIG, BE), literatür referansları (Stewart-1983, Figge-1991, Fencl-2000, Berend-2014, Kellum-2009, Morgan-2009, Story-2016), validasyon mesajları, 3-katmanlı validasyon modeli (`PHYSIOLOGIC_LIMITS`, `EXTREME_THRESHOLDS`, `REFERENCE_RANGES`), hazır vakalar (`SAMPLE_CASES`), UI metinleri (`UI_TEXTS`), CDS not şablonları (`CDS_NOTES`), klasik karşılaştırma mesajları (`CLASSIC_COMPARISON`).
- **`ui_components.py`**: `render_headline()`, `render_basic_values()`, `render_contribution_breakdown()`, `render_sid_table()`, `render_stewart_params()`, `render_anion_gap()`, `render_compensation()`, `render_classic_comparison()`, `render_cds_notes()`, `render_soft_warnings()`, `render_warnings()`, `render_footer()` fonksiyonları. Emoji ve renk kodlamalı değer göstergeleri (`get_value_indicator()`).
- **`visualization.py`**: `create_gamblegram()`, `create_contribution_chart()`, `create_sid_waterfall()`, `create_ph_gauge()` Plotly figürleri ve bunların Streamlit'te render edilmesi.
- **`validation.py`**: `sanitize_numeric()` (virgül ondalık ayırıcı, boşluk temizleme, NaN/inf kontrolü), `validate_input_dict()` (sözlük validasyonu), `validate_csv_row()` (CSV satır validasyonu), `detect_albumin_unit()` (g/dL vs g/L otomatik algılama), `analyze_na_cl_swap_suspicion()` (Na/Cl kolon yer değiştirme şüphesi — ASLA otomatik düzeltme yapmaz, sadece raporlar).
- **`logger.py`**: `log_user_action()`, `log_calculation_warning()`, `log_analysis_error()`, `log_batch_progress()`, `log_analysis_start()`, `log_analysis_complete()`, `log_extreme_value()`, `log_mechanism_result()`, `log_sid_calculation()`, `log_compensation_assessment()`, `log_debug()`. Tüm loglar JSON yapısında detay içerir. Hasta kimlik bilgisi (PHI) loglanmaz.

---

## 4. Derleme ve Çalıştırma Komutları

### Yerel Geliştirme
```bash
pip install -r requirements.txt
streamlit run app.py
```
Uygulama varsayılan olarak `http://localhost:8501` adresinde açılır.

### Docker
```bash
docker build -t stewart-analyzer .
docker run -p 8501:8501 stewart-analyzer
```
- `Dockerfile`: `python:3.11-slim` tabanlı, root olmayan kullanıcı (`appuser`), healthcheck `/_stcore/health` endpoint'ine ping atar.
- Streamlit ortam değişkenleri: `STREAMLIT_SERVER_PORT=8501`, `STREAMLIT_SERVER_ADDRESS=0.0.0.0`, `STREAMLIT_SERVER_HEADLESS=true`.

### Devcontainer (VS Code / GitHub Codespaces)
`.devcontainer/devcontainer.json` yapılandırması mevcuttur. Açıldığında otomatik olarak bağımlılıklar yüklenir ve `streamlit run app.py` çalıştırılır.

---

## 5. Test Talimatları

### Tüm Testler
```bash
pytest -v
```

### Belirli Test Dosyaları
```bash
pytest test_core.py -v              # Hesaplama motoru birim testleri
pytest test_validation.py -v        # Edge case ve kirli girdi testleri
pytest test_regression.py -v        # Kritik düzeltme regresyon testleri
pytest test_regression_fixed.py -v  # Düzeltilmiş regresyon testleri
pytest test_simple.py -v            # Smoke testleri
pytest test_sprint4.py -v           # Sprint 4 testleri
```

### Coverage
```bash
pytest --cov=. --cov-report=html
```

### Test Dosyalarının Amaçları
- **`test_core.py`**: `calculate_hco3()`, `calculate_be()`, SID hesaplamaları, SIG yorumlama, katkı ayrıştırma (`generate_contribution_breakdown`), headline oluşturma, mekanizma analizi.
- **`test_validation.py`**: `sanitize_numeric()`'ın virgül ondalık, boşluk, NaN, boş string gibi kirli girdilerle başa çıkması; `validate_input_dict()`; `validate_csv_row()`; `detect_albumin_unit()`; batch validasyon.
- **`test_regression.py` / `test_regression_fixed.py`**: Primer respiratuvar bozukluk tanıma, SIG yanlış flaglenme, çelişkili çıktı, kronik respiratuvar bozukluklar, mikst bozukluklar gibi kritik fonksiyonelliğin regresyonunu önler.

---

## 6. Kod Stili ve Geliştirme Kuralları

### Dil Kuralı (Kritik)
**Tüm kod yorumları, docstring'ler, değişken açıklamaları ve UI metinleri Türkçe olmalıdır.** İngilizce katkılar yapılacaksa bile mevcut Türkçe dokümantasyonun üzerine yazılmamalı, Türkçe korunmalıdır.

### Tanı Dışı Dil Kuralı (Kritik)
Uygulama bilerek tanısal terimlerden kaçınır. Örnekler:
- ❌ "Ketoasidoz" → ✅ "Ölçülmemiş anyon aracılı metabolik asidoz"
- ❌ "Laktik asidoz" → ✅ "Laktat aracılı metabolik asidoz"
- ❌ "HAGMA / NAGMA" → ✅ "Yüksek anyon gap metabolik asidoz" / "Normal anyon gap metabolik asidoz" (sadece klasik karşılaştırma bölümünde)

Yeni özellikler eklerken bu felsefeye sadık kalınmalıdır.

### Sabitler ve Eşik Değerler
- Tüm klinik eşik değerler `constants.py`'de tanımlanır.
- Her eşik değerin üzerinde literatür referansı yorum satırı bulunur (örn. `# Referans: [BEREND-2014]`).
- Yeni bir eşik değeri eklerken mutlaka fizyolojik gerekçe ve varsa literatür kaynağı eklenmelidir.
- Sabit isimleri `SCREAMING_SNAKE_CASE` ile yazılır.

### Dataclass Kullanımı
Proje yoğun şekilde `@dataclass` kullanır:
- `StewartInput` — analiz girdisi
- `StewartOutput` — analiz çıktısı
- `ValidationResult` — validasyon sonucu
- `SIDValues` — 3 katmanlı SID değerleri
- `MechanismAnalysis` — mekanizma analizi
- `Headline` — özet sonuç satırı
- `CDSNote` — klinik karar destek notu
- `ClassicComparison` — klasik yaklaşım karşılaştırması

Yeni bir veri yapısı eklerken `typing` modülünden `Optional`, `List`, `Dict`, `Tuple` kullanın. Alanlar için Türkçe docstring yazın.

### Fonksiyon İmzaları
- Analiz fonksiyonları `Tuple[StewartOutput, ValidationResult]` döner.
- `Optional[float]` kullanımı yaygındır; eksik parametreler `None` ile temsil edilir.
- Yuvarlama: Hesaplama sonuçları genellikle `round(value, 1)` ile 1 ondalığa yuvarlanır.

---

## 7. Mimari ve Analiz Modelleri

### Üç Katmanlı Validasyon Modeli
`constants.py` ve `validation.py`'de uygulanır:

1. **Fizyolojik Limitler (`PHYSIOLOGIC_LIMITS`)**: Hard reject. Bu sınırların dışındaki değerler fizyolojik olarak imkansız kabul edilir ve analiz reddedilir. Örnek: pH < 6.50 veya > 7.90.
2. **Ekstrem Eşikler (`EXTREME_THRESHOLDS`)**: Fizyolojik olarak mümkün ama nadir ve kritik. Uyarı verilir ama analiz devam eder. Örnek: pH < 7.0 (şiddetli asidemi), pCO2 > 120 (şiddetli hiperkapni), laktat > 10 (şok düzeyi).
3. **Referans Aralıkları (`REFERENCE_RANGES`)**: Sağlıklı bireylerdeki tipik değerler. Bilgilendirme amaçlı, kısıtlayıcı değil.

### Katkı Tabanlı Mekanizma Analizi (Contribution-Based Analysis)
`core.py`'deki `analyze_mechanisms()` ve `determine_metabolic_dominance()` fonksiyonlarında uygulanır:

- Mekanizmalar sadece varlıklarına göre değil, **mutlak mEq/L katkılarına** göre sıralanır.
- Dominant: ≥50% katkı
- Anlamlı (significant): 25-50% katkı
- Katkıda bulunan (contributing): 10-25% katkı
- Minimal: <10% katkı
- Laktat için özel eşikler vardır: ≥50% dominant, ≥25% anlamlı, >0% katkıda bulunan.

### Koşullu SIG Yorumlaması (Kritik)
`core.py`'deki `analyze_mechanisms()` ve `generate_cds_notes()`'ta uygulanır:

SIG (Strong Ion Gap) **SADECE** şu koşullarda yorumlanır:
- BE ≤ -3 (metabolik asidoz mevcut)
- Laktat normal veya açıklayıcı değil (`abs(lactate_effect) < 2.0`)
- Primer bozukluk metabolik asidoz
- Primer respiratuvar bozukluk yok

Aksi halde SIG yüksek olsa bile "ölçülmemiş anyon" olarak raporlanmaz. Bu, en sık yapılan mantık hatalarından biridir; değişiklik yaparken bu koşulları korumak zorunludur.

### Dominant Bozukluk Tespiti Karar Sırası
`determine_dominant_disorder()`'da değiştirilemez bir karar sırası vardır:

1. Önce primer respiratuvar bozukluklar kontrol edilir (pH + pCO2 uyumu + BE normal/hafif).
2. Sonra primer metabolik bozukluklar kontrol edilir (pH + BE uyumu).
3. Ardından mikst bozukluklar.
4. Son olarak normal veya belirsiz durumlar.

### Hazır Vakalar (Sample Cases)
`constants.py`'deki `SAMPLE_CASES` sözlüğü eğitim amaçlı vakalar içerir. Her vaka:
- `name`, `description`, `values`, `teaching_point` alanlarına sahiptir.
- İleri düzey vakalarda (`akoglu_*` prefixli vakalar) `classic_interpretation` ve `stewart_findings` alanları da vardır.
- Yeni bir hazır vaka eklerken `app.py`'deki sidebar seçim listesine otomatik olarak eklenir (key üzerinden).

---

## 8. Güvenlik ve Güvenlikle İlgili Hususlar

### Eğitim Amaçlı Sorumluluk Reddi
Uygulamanın her yerinde şu mesaj veya benzerleri görülür:
- `"Bu araç fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir."`
- `"Eğitim amaçlıdır. Klinik karar için uzman değerlendirmesi gerekir."`

Yeni UI bölümleri eklerken bu sorumluluk reddi metinlerini korumak veya benzerlerini eklemek gerekir.

### Girdi Güvenliği
- `validation.py`'deki `sanitize_numeric()` virgül ondalık ayırıcıyı (`7,40` → `7.40`), boşlukları, NaN/inf değerlerini ve geçersiz string'leri güvenli şekilde işler.
- `validate_input_dict()` ve `validate_csv_row()` üç katmanlı validasyon uygular.
- **Na/Cl Swap Tespiti**: `analyze_na_cl_swap_suspicion()` Na ve Cl kolonlarının yer değiştirmiş olabileceğini analiz eder ancak **ASLA otomatik düzeltme yapmaz**. Sadece şüpheyi raporlar ve kullanıcının karar vermesini bekler. Bu davranış değiştirilemez.

### Loglama ve PHI (Hasta Kimlik Bilgisi)
- `logger.py`'deki `log_analysis_error()` sadece sayısal parametreleri loglar (`ph`, `pco2`, `na`, `cl`, vb.). Hasta adı, kimlik numarası, doğum tarihi gibi PHI asla loglanmaz.
- `log_user_action()` detayları 100 karakterle sınırlandırır ve string'e çevirir.
- Log seviyeleri: INFO (kullanıcı aksiyonları), WARNING (hesaplama uyarıları), ERROR (başarısız analizler), DEBUG (geliştirme detayları).

### BE İşaret Hatası Tespiti
`app.py`'deki `check_be_sign_error()` fonksiyonu, pH asidemi gösterirken BE pozitif veya pH alkalemi gösterirken BE negatif olduğunda işaret hatası olduğunu tespit eder ve analizi durdurur. Bu, klinik olarak yaygın bir veri giriş hatasını önler.

---

## 9. Ajanlar İçin Kritik Dosya Rehberi

| Değişiklik Amacı | Okunması Gereken Dosyalar |
|------------------|---------------------------|
| Yeni hesaplama / analiz mantığı | `core.py`, `constants.py` (sabitler), `test_core.py` |
| Yeni UI bileşeni / sayfa düzeni | `app.py`, `ui_components.py`, `constants.py` (UI_TEXTS) |
| Yeni grafik / görselleştirme | `visualization.py`, `ui_components.py` (render fonksiyonları) |
| Yeni validasyon kuralı | `validation.py`, `constants.py` (VALIDATION_MESSAGES, limitler), `test_validation.py` |
| Yeni eşik değer / klinik sabit | `constants.py` (tek kaynak), ardından etkilenen `core.py`, `validation.py` |
| Yeni log mesajı / log seviyesi | `logger.py`, `core.py` (log çağrıları) |
| Yeni hazır vaka | `constants.py` (SAMPLE_CASES), `app.py` (sidebar otomatik çeker) |
| Yeni CDS notu | `constants.py` (CDS_NOTES), `core.py` (generate_cds_notes) |
| Regresyon testi yazma | `test_regression_fixed.py`, `test_core.py` (örnekler) |
| Performans optimizasyonu | `core.py` (analyze_stewart ana fonksiyonu), `app.py` (Streamlit cache/SessionState) |

---

## 10. Sık Karşılaşılan Tuzaklar

1. **SIG'i her zaman yorumlamak**: SIG yalnızca metabolik asidoz bağlamında yorumlanır. Primer respiratuvar bozukluk veya normal BE durumlarında yüksek SIG "ölçülmemiş anyon" olarak raporlanmamalıdır.
2. **Tanısal dil kullanmak**: "Ketoasidoz", "üremik asidoz", "laktik asidoz" gibi tanısal terimler kullanılmaz. Bunun yerine mekanizma odaklı, tanı dışı dil kullanılır.
3. **Na/Cl swap'i otomatik düzeltmek**: Validasyon modülü sadece şüphe raporlar, asla otomatik düzeltme yapmaz.
4. **Yeni sabitleri `core.py`'ye yazmak**: Tüm klinik sabitler `constants.py`'de toplanır. `core.py` sadece `constants.py`'den import eder.
5. **İngilizce yorum/docstring eklemek**: Mevcut Türkçe dokümantasyonu İngilizce ile karıştırmamak gerekir. Yeni kod Türkçe açıklamalarla yazılmalıdır.

---

## 11. Mojibake ve Encoding Temizliği (En İyi Pratik)

Projede Türkçe karakterler (ç, ğ, ı, ö, ş, ü), bilimsel semboller (±, →, ↑, ↓, •, ≈, ≤) ve emoji (⚠️, ⚕️, 📚, 🧠) yoğun şekilde kullanılır. Windows/macOS/Linux arası dosya aktarımları veya farklı editörlerde bu karakterler **mojibake** (UTF-8 baytlarının Latin-1/CP1252 olarak yanlış okunması) haline gelebilir.

### Tespit
```bash
grep -rn "â€¢\|Â±\|â†\|â‰\|Ã—\|â^\|âš\|ðŸ\|â€" *.py
```

### Düzeltme — `ftfy` (Önerilen Yöntem)
El-yapımı string replace haritaları yerine **`ftfy.fix_encoding()`** kullanın. Bu yöntem:
- Sadece kodlama bozulmasını onarır, tırnak/boşluk/indent gibi yapısal değişiklik yapmaz.
- `≤`, `⚕️`, varyasyon seçicili `⚠️` gibi edge-case sembolleri de kapsar.
- Kaynak kodda güvenlidir (parse etmez, sadece encoding düzeltir).

```python
import ftfy
from pathlib import Path

for fn in ["constants.py", "core.py", "logger.py", "ui_components.py", "app.py", "visualization.py"]:
    p = Path(fn)
    text = p.read_text(encoding="utf-8")
    fixed = ftfy.fix_encoding(text)
    if fixed != text:
        p.write_text(fixed, encoding="utf-8", newline="\n")
        print(f"FIXED: {fn}")
```

**Not:** `ftfy` tek seferlik geliştirme aracıdır; `requirements.txt`'e eklenmemelidir.

### Düzeltme — Manuel (Yedek Yöntem)
Eğer `ftfy` kullanılamıyorsa, `fix_tr_text.py` gibi bir script ile karakter haritası (`MOJIBAKE_MAP`) oluşturulabilir. Ancak bu yöntem:
- Yeni/beklenmedik mojibake varyasyonlarını kaçırabilir.
- Çift karakterli mojibake'leri (örn. `Â±`, `âš ï¸`) yakalamak için hem byte hem de string literal girişleri gerektirir.

### Doğrulama
Düzeltme sonrası mutlaka şunları teyit edin:
1. `grep -rn "â€¢\|Â±\|â†\|â‰\|Ã—\|â^\|âš\|ðŸ\|â€" *.py` → **0 sonuç**.
2. `git diff -w core.py validation.py` → **0 satır** (hesaplama mantığı değişmemeli).
3. `pytest -v` → **Tüm testler yeşil**.

## 12. İletişim ve Referanslar

Projedeki literatür referansları `constants.py`'nin başında ve `REFERENCES` sözlüğünde dokümante edilmiştir. Ana kaynaklar:

- Stewart PA. Modern quantitative acid-base chemistry. Can J Physiol Pharmacol. 1983
- Figge J, Mydosh T, Fencl V. Serum proteins and acid-base equilibria. J Lab Clin Med. 1991
- Fencl V, Jabor A, Kazda A, Figge J. Diagnosis of metabolic acid-base disturbances. Am J Respir Crit Care. 2000
- Morgan TJ. The Stewart approach. Crit Care Clin. 2009
- Kellum JA. Disorders of acid-base balance. Crit Care Med. 2009
- Berend K, et al. Physiological approach to assessment of acid-base disturbances. NEJM. 2014
- Story DA. Stewart acid-base: A simplified bedside approach. Anesth Analg. 2016

Klinik vaka katkıları: Doç. Dr. Haldun Akoğlu — Marmara Üniversitesi Acil Tıp AD.
