# Changelog - Stewart Asit-Baz Analizi

## v3.5.0 (2026-01-08) - Sprint 3: Logging & Documentation

### ✨ Yeni Özellikler

**#4: Kapsamlı Logging Sistemi**
- `log_analysis_start()`: Analiz başlangıcını mod ve input özeti ile loglar
- `log_analysis_complete()`: Analiz süresini (ms) ve sonuç özetini loglar
- `log_extreme_value()`: Kritik değerleri (pH<7.0, laktat>10 vb.) klinik notlarıyla loglar
- `log_mechanism_result()`: Dominant ve anlamlı mekanizmaları loglar
- `log_sid_calculation()`: SID hesaplama adımlarını DEBUG seviyesinde loglar
- `log_compensation_assessment()`: Kompanzasyon değerlendirmesini loglar

**#6: Literatür Referanslı Eşik Dokümantasyonu**
- Tüm threshold değerlerine literatür referansı eklendi
- 8 ana kaynak: Stewart-1983, Figge-1991, Fencl-2000, Morgan-2009, Kellum-2009, Story-2016, Berend-2014
- Her eşik için klinik önem ve fizyolojik gerekçe açıklamaları

### 🔧 Teknik İyileştirmeler

**core.py:**
- `_check_and_log_extreme_values()`: Otomatik ekstrem değer tespiti ve loglama
- `analyze_stewart()`: Baştan sona logging entegrasyonu
- Analiz performans metrikleri (süre ölçümü)

**logger.py:**
- 6 yeni logging fonksiyonu
- Klinik bağlam içeren uyarı mesajları

**constants.py:**
- LITERATURE_REFERENCES bölümü
- Detaylı threshold dokümantasyonu (400+ satır)
- Three-tier validation model açıklaması

---

## v3.4.0 (2026-01-08) - Derived Values & Sign Error Detection

### ✨ Yeni Özellikler
- HCO₃/BE otomatik hesaplama sistemi
- Cihaz değeri doğrulama seçeneği
- BE işaret hatası tespiti ve kullanıcı uyarısı

---

## v3.3.0 (2026-01-08) - UI Fixes

### 🐛 Hata Düzeltmeleri
- Çift ok gösterimi sorunu düzeltildi
- Severity-based renk kodlaması iyileştirildi

---

## v3.2.0 - Modular Architecture

### 🏗️ Mimari Değişiklikler
- ui_components.py modülü eklendi
- visualization.py modülü eklendi
- validation.py modülü eklendi
- logger.py modülü eklendi

---

## v3.1.0 - Contribution-Based Analysis

### ✨ Yeni Özellikler
- Contribution-based mekanizma analizi
- Non-diagnostic, physiology-focused dil
- Mekanizma katkı yüzdeleri

---

## v3.0.0 - Stewart-Fencl Integration

### ✨ Yeni Özellikler
- CDS (Klinik Karar Destek) notları
- Klasik yaklaşım karşılaştırması
- Gamblegram görselleştirme
