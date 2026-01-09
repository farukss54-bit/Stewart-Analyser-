# constants.py
# Stewart Asit-Baz Analizi - Sabitler, CDS Notları ve Hazır Vakalar
# v3.5 - Literatür Referanslı Threshold Dokümantasyonu

# =============================================================================
# 📚 LİTERATÜR REFERANSLARI
# =============================================================================
# Bu dosyadaki eşik değerleri aşağıdaki kaynaklara dayanmaktadır:
#
# [STEWART-1983]   Stewart PA. Modern quantitative acid-base chemistry.
#                  Can J Physiol Pharmacol. 1983;61(12):1444-61
#
# [FIGGE-1991]     Figge J, Mydosh T, Fencl V. Serum proteins and acid-base
#                  equilibria. J Lab Clin Med. 1991;117(6):453-67
#
# [FENCL-2000]     Fencl V, Jabor A, Kazda A, Figge J. Diagnosis of metabolic
#                  acid-base disturbances. Am J Respir Crit Care. 2000;162:2246-51
#
# [MORGAN-2009]    Morgan TJ. The Stewart approach. Crit Care Clin. 2009;25:261-78
#
# [KELLUM-2009]    Kellum JA. Disorders of acid-base balance.
#                  Crit Care Med. 2009;37(1):76-86
#
# [STORY-2016]     Story DA. Stewart acid-base: A simplified bedside approach.
#                  Anesth Analg. 2016;123(2):511-5
#
# [BEREND-2014]    Berend K, et al. Physiological approach to assessment of
#                  acid-base disturbances. NEJM. 2014;371:1434-45
# =============================================================================

# =============================================================================
# 🔬 pH ARALIKLARI
# =============================================================================
# Referans: [BEREND-2014], [KELLUM-2009]
# Normal arteriyel kan pH'ı: 7.35-7.45
# Yaşamla bağdaşan sınırlar: ~6.8 - ~7.8
# pH < 6.8 veya > 7.8: Ciddi enzim disfonksiyonu, kardiyak arrest riski

PH_MIN = 6.50              # Hard limit - bu altı fizyolojik olarak imkansız
PH_MAX = 7.90              # Hard limit - bu üstü fizyolojik olarak imkansız
PH_NORMAL_LOW = 7.35       # [BEREND-2014] Normal aralık alt sınırı
PH_NORMAL_HIGH = 7.45      # [BEREND-2014] Normal aralık üst sınırı

# Klinik yorumlama eşikleri:
# pH < 7.20: Şiddetli asidemi - acil müdahale
# pH < 7.35: Asidemi
# pH > 7.45: Alkalemi
# pH > 7.55: Şiddetli alkalemi - acil müdahale

# =============================================================================
# 🌬️ pCO2 ARALIKLARI (mmHg)
# =============================================================================
# Referans: [BEREND-2014], [KELLUM-2009]
# Normal: 35-45 mmHg (deniz seviyesinde)
# Fizyolojik kompanzasyon sınırları: ~10-80 mmHg
# Kritik değerler: <20 (şiddetli hipokapni), >80 (şiddetli hiperkapni)

PCO2_MIN = 5.0             # Hard limit - mekanik ventilasyon altında bile nadir
PCO2_MAX = 250.0           # Hard limit - şiddetli hiperkapnik solunum yetmezliği
PCO2_NORMAL_LOW = 35.0     # [BEREND-2014] Normal aralık alt sınırı
PCO2_NORMAL_HIGH = 45.0    # [BEREND-2014] Normal aralık üst sınırı
PCO2_NORMAL = 40.0         # Hesaplamalarda kullanılan referans değer

# =============================================================================
# 🧪 HCO3 ARALIKLARI (mEq/L)
# =============================================================================
# Referans: [BEREND-2014]
# Not: HCO3 doğrudan ölçülmez, Henderson-Hasselbalch ile hesaplanır
# Normal: 22-26 mEq/L
# Metabolik asidoz: <22, Metabolik alkaloz: >26

HCO3_MIN = 5.0             # Şiddetli metabolik asidoz (hayati tehlike)
HCO3_MAX = 50.0            # Şiddetli metabolik alkaloz
HCO3_NORMAL = 24.0         # [BEREND-2014] Referans değer
HCO3_MISMATCH_THRESHOLD = 2.0  # Manuel-hesaplanan fark toleransı

# =============================================================================
# ⚡ ELEKTROLİT ARALIKLARI (mmol/L)
# =============================================================================
# Referans: [KELLUM-2009], [STORY-2016]

# --- Sodyum (Na⁺) ---
# Normal: 135-145 mmol/L
# SID hesaplamasının temel katyonu
NA_MIN = 80.0              # Hard limit - <120 ciddi hiponatremi
NA_MAX = 220.0             # Hard limit - >160 ciddi hipernatremi
NA_NORMAL = 140.0          # [KELLUM-2009] Referans değer

# --- Potasyum (K⁺) ---
# Normal: 3.5-5.0 mmol/L
# SID_full hesaplamasında kullanılır (minör katkı)
K_MIN = 1.5                # Hard limit - kardiyak arrest riski
K_MAX = 10.0               # Hard limit - kardiyak arrest riski
K_NORMAL = 4.0             # Referans değer

# --- Klor (Cl⁻) ---
# Normal: 98-106 mmol/L
# SID hesaplamasının temel anyonu - hiperkloremik asidoz belirleyicisi
CL_MIN = 50.0              # Hard limit
CL_MAX = 200.0             # Hard limit
CL_NORMAL = 100.0          # [KELLUM-2009] Referans değer

# --- Kalsiyum İyonize (Ca²⁺) ---
# Normal: 1.1-1.4 mmol/L (iyonize)
# SID_full'da minör katkı (2x valans)
CA_MIN = 0.5               # Ciddi hipokalsemi
CA_MAX = 2.5               # Ciddi hiperkalsemi
CA_NORMAL = 1.25           # Referans değer

# --- Magnezyum (Mg²⁺) ---
# Normal: 0.7-1.0 mmol/L
# SID_full'da minör katkı (2x valans)
MG_MIN = 0.3               # Ciddi hipomagnezemi
MG_MAX = 3.0               # Ciddi hipermagnezemi
MG_NORMAL = 0.85           # Referans değer

# =============================================================================
# 🔥 LAKTAT (mmol/L)
# =============================================================================
# Referans: [KELLUM-2009], [MORGAN-2009]
# Normal: <2 mmol/L
# Laktat güçlü bir anyondur ve SID'i düşürür (asidoz yönünde)
# Yüksek laktat = doku hipoperfüzyonu, sepsis, şok göstergesi

LACTATE_MIN = 0.0          # Alt sınır
LACTATE_MAX = 40.0         # Hayatta kalma bildirilen en yüksek değerler
LACTATE_NORMAL = 1.0       # Normal üst sınır ~2
LACTATE_THRESHOLD = 2.0    # [KELLUM-2009] Klinik anlamlılık eşiği

# Klinik yorumlama:
# <2: Normal
# 2-4: Hafif yükselme (hipoperfüzyon olabilir)
# 4-10: Orta-şiddetli (ciddi hipoperfüzyon)
# >10: Kritik (şok, çoklu organ yetmezliği)

# =============================================================================
# 🥚 ALBÜMİN
# =============================================================================
# Referans: [FIGGE-1991], [FENCL-2000]
# Albümin zayıf bir asittir (Atot'un ana bileşeni)
# Düşük albümin = alkaloz yönünde etki (maskeleme!)
# Kritik hasta popülasyonunda sık görülür

ALBUMIN_MIN_GL = 5.0       # Şiddetli hipoalbüminemi
ALBUMIN_MAX_GL = 60.0      # Nadir görülen üst değerler
ALBUMIN_NORMAL_GL = 40.0   # [FIGGE-1991] Normal değer (4 g/dL)
ALBUMIN_LOW_GL = 35.0      # CDS eşiği - bu altı "düşük" kabul edilir
ALBUMIN_MIN_GDL = 0.5      # g/dL cinsinden alt sınır
ALBUMIN_MAX_GDL = 6.0      # g/dL cinsinden üst sınır
ALBUMIN_NORMAL_GDL = 4.0   # [FIGGE-1991] Normal değer

# =============================================================================
# 🧫 FOSFAT (mmol/L)
# =============================================================================
# Referans: [FIGGE-1991]
# Fosfat da zayıf asit olarak Atot'a katkıda bulunur
# Albümine göre daha az etkili

PO4_MIN = 0.3              # Ciddi hipofosfatemi
PO4_MAX = 4.0              # Ciddi hiperfosfatemi
PO4_NORMAL = 1.0           # Referans değer

# =============================================================================
# ⚖️ BASE EXCESS (mEq/L)
# =============================================================================
# Referans: [BEREND-2014]
# BE = metabolik komponentin miktarsal göstergesi
# Negatif = metabolik asidoz, Pozitif = metabolik alkaloz

BE_MIN = -30.0             # Şiddetli metabolik asidoz
BE_MAX = 30.0              # Şiddetli metabolik alkaloz
BE_NORMAL = 0.0            # İdeal değer
BE_MISMATCH_THRESHOLD = 2.0  # Manuel-hesaplanan fark toleransı

# =============================================================================
# 🔬 SID DEĞERLERİ (mEq/L) - STEWART YAKLAŞIMI
# =============================================================================
# Referans: [STEWART-1983], [FENCL-2000], [MORGAN-2009]
#
# SID (Strong Ion Difference) = Güçlü katyonlar - Güçlü anyonlar
# Stewart'a göre SID, pH'ın bağımsız belirleyicilerinden biridir
#
# SID_simple  = Na - Cl (pratik, hızlı değerlendirme)
# SID_basic   = Na - Cl - Lactate (laktat etkisi dahil)
# SID_full    = (Na + K + Ca×2 + Mg×2) - (Cl + Lactate) (tam hesaplama)

SID_NORMAL_SIMPLE = 38.0   # [FENCL-2000] Na-Cl için normal değer
SID_NORMAL_BASIC = 37.0    # Laktat dahil normal değer
SID_NORMAL_FULL = 40.0     # [STEWART-1983] Tam SIDa için normal
SID_LOW_THRESHOLD = 38.0   # Bu altı = metabolik asidoz yönünde
SID_HIGH_THRESHOLD = 44.0  # Bu üstü = metabolik alkaloz yönünde
SID_NORMAL_RANGE = 2.0     # Normal kabul edilen varyasyon
SID_THRESHOLD = 2.0        # Klinik anlamlılık eşiği

# =============================================================================
# 🔍 SIG DEĞERLERİ (mEq/L) - STRONG ION GAP
# =============================================================================
# Referans: [FENCL-2000], [KELLUM-2009]
#
# SIG = SIDapparent - SIDeffective
# SIG > 0: Ölçülmemiş anyonlar mevcut (ketonlar, laktat dışı organik asitler,
#          toksik alkoller, sülfatlar, üremik toksinler)
# SIG < 0: Ölçülmemiş katyonlar veya ölçüm hatası (nadir)
#
# Klasik AG'den farkı: Albümin düzeltmesi otomatik dahil

SIG_NORMAL = 0.0           # İdeal değer
SIG_THRESHOLD = 2.0        # Klinik anlamlılık eşiği
SIG_HIGH = 2.0             # Bu üstü = ölçülmemiş anyon varlığı
SIG_LOW = -2.0             # Bu altı = ölçülmemiş katyon (nadir, genellikle hata)

# =============================================================================
# 📊 Cl/Na ORANI
# =============================================================================
# Referans: [STORY-2016]
# Normal oran: ~0.75-0.79
# Yüksek oran (>0.79): Hiperkloremik asidoz lehine
# Düşük oran (<0.75): Hipokloremik alkaloz lehine

CL_NA_RATIO_THRESHOLD = 0.75  # Bu üstü hiperkloremik patern

# =============================================================================
# 🎯 ANYON GAP (mEq/L) - KLASİK YAKLAŞIM
# =============================================================================
# Referans: [BEREND-2014]
# AG = Na - (Cl + HCO3)
# Normal: 8-12 mEq/L (albüminsiz)
# Düzeltilmiş AG = AG + 2.5 × (4.2 - Albümin_g/dL)

AG_NORMAL = 12.0           # [BEREND-2014] Normal üst sınır
AG_THRESHOLD = 2.0         # Klinik anlamlılık toleransı

# =============================================================================
# ⚖️ KLİNİK ANLAMLILIK EŞİĞİ
# =============================================================================
# Bu değer, hesaplanan etkilerin "anlamlı" kabul edilme sınırıdır
# <2 mEq/L farklar genellikle klinik olarak önemsizdir

CLINICAL_SIGNIFICANCE_THRESHOLD = 2.0

# =============================================================================
# 🫁 KOMPANZASYON SABİTLERİ
# =============================================================================
# Referans: [BEREND-2014], Standard fizyoloji kitapları
#
# --- Metabolik Asidoz için Winter's Formülü ---
# Beklenen pCO2 = 1.5 × HCO3 + 8 (±2)
# [BEREND-2014]: En yaygın kullanılan kompanzasyon formülü

WINTERS_HCO3_COEFFICIENT = 1.5
WINTERS_CONSTANT = 8
WINTERS_TOLERANCE = 2

# --- Metabolik Alkaloz için Kompanzasyon ---
# Beklenen pCO2 = 0.7 × HCO3 + 21 (±2)
# Not: Metabolik alkalozda kompanzasyon daha az öngörülebilir

ALKALOSIS_PCO2_COEFFICIENT = 0.7
ALKALOSIS_PCO2_CONSTANT = 21
ALKALOSIS_TOLERANCE = 2

# --- Respiratuvar Asidoz Kompanzasyonu ---
# Akut: HCO3 = 24 + 0.1 × (pCO2 - 40)  → Her 10↑ pCO2 = 1↑ HCO3
# Kronik: HCO3 = 24 + 0.35 × (pCO2 - 40) → Her 10↑ pCO2 = 3.5↑ HCO3

RESP_ACIDOSIS_ACUTE_COEFFICIENT = 0.1
RESP_ACIDOSIS_CHRONIC_COEFFICIENT = 0.35

# --- Respiratuvar Alkaloz Kompanzasyonu ---
# Akut: HCO3 = 24 - 0.2 × (40 - pCO2)  → Her 10↓ pCO2 = 2↓ HCO3
# Kronik: HCO3 = 24 - 0.5 × (40 - pCO2) → Her 10↓ pCO2 = 5↓ HCO3

RESP_ALKALOSIS_ACUTE_COEFFICIENT = 0.2
RESP_ALKALOSIS_CHRONIC_COEFFICIENT = 0.5
COMPENSATION_TOLERANCE = 2

# =============================================================================
# 🧮 FORMÜL SABİTLERİ
# =============================================================================
# Referans: [STEWART-1983], [FIGGE-1991]

# --- Henderson-Hasselbalch Denklemi ---
# pH = pK + log([HCO3] / (0.03 × pCO2))
HH_CONSTANT = 6.1          # pK değeri (karbondioksit/bikarbonat sistemi)
HH_SOLUBILITY = 0.03       # CO2 çözünürlük katsayısı (mmol/L per mmHg)

# --- Siggaard-Andersen BE Hesaplama ---
# BE = 0.9287 × (HCO3 - 24.4 + 14.83 × (pH - 7.4))
# Referans: Siggaard-Andersen equation (klinik standart)
# Eski Van Slyke: BE ≈ 1.1 × (HCO3 - 24) + 32 × (pH - 7.40) [deprecated]
BE_COEFFICIENT = 0.9287        # Siggaard-Andersen ana katsayısı
BE_HCO3_NORMAL = 24.4          # Referans HCO3 değeri
BE_PH_COEFFICIENT = 14.83      # pH katkı katsayısı
BE_PH_NORMAL = 7.4             # Referans pH değeri

# Geriye uyumluluk için eski sabitler (kullanılmıyor)
BE_HCO3_COEFFICIENT = 1.1      # [DEPRECATED] Van Slyke katsayısı

# --- Figge-Fencl Albümin/Fosfat Katsayıları ---
# Referans: [FIGGE-1991]
# SIDeffective hesaplamasında kullanılır
# Atot = (0.123 × pH - 0.631) × Albumin_g/L + (0.309 × pH - 0.469) × PO4_mmol/L
ALBUMIN_PH_COEFFICIENT = 0.123   # [FIGGE-1991]
ALBUMIN_CONSTANT = 0.631        # [FIGGE-1991]
PO4_PH_COEFFICIENT = 0.309      # [FIGGE-1991]
PO4_CONSTANT = 0.469            # [FIGGE-1991]

# --- Atot Basitleştirilmiş Katsayılar ---
# Atot ≈ 0.123 × Albumin + 0.309 × PO4 (pH 7.4'te)
ATOT_ALBUMIN_COEFFICIENT = 0.123
ATOT_PO4_COEFFICIENT = 0.309

# === VALIDASYON MESAJLARI ===
VALIDATION_MESSAGES = {
    "ph_out_of_range": "pH değeri fizyolojik sınırlar dışında (6.80-7.80)",
    "pco2_out_of_range": "pCO2 değeri kabul edilebilir sınırlar dışında (10-120 mmHg)",
    "na_out_of_range": "Na+ değeri kabul edilebilir sınırlar dışında (110-180 mmol/L)",
    "cl_out_of_range": "Cl- değeri kabul edilebilir sınırlar dışında (70-140 mmol/L)",
    "k_out_of_range": "K+ değeri kabul edilebilir sınırlar dışında (2-8 mmol/L)",
    "ca_out_of_range": "Ca2+ değeri kabul edilebilir sınırlar dışında (0.5-2.5 mmol/L)",
    "mg_out_of_range": "Mg2+ değeri kabul edilebilir sınırlar dışında (0.3-3 mmol/L)",
    "lactate_out_of_range": "Laktat değeri kabul edilebilir sınırlar dışında (0-25 mmol/L)",
    "albumin_gl_out_of_range": "Albümin (g/L) değeri kabul edilebilir sınırlar dışında (5-60 g/L)",
    "po4_out_of_range": "Fosfat değeri kabul edilebilir sınırlar dışında (0.3-4 mmol/L)",
    "be_mismatch": "BE mismatch: girilen BE ile hesaplanan BE arasında >2 mEq/L fark var.",
    "hco3_mismatch": "HCO3 mismatch: girilen HCO3 ile hesaplanan arasında >2 mEq/L fark var.",
    "sig_no_lactate": "Laktat olmadan SIG muhtemelen düşük hesaplanmıştır.",
    "sig_approximate": "Ca/Mg eksik olduğundan SIG yaklaşık değerdir.",
    "sig_unreliable": "Kritik parametreler eksik, SIG güvenilir değil.",
}

# =============================================================================
# 🚦 SEVERITY / CRITICAL MESSAGE MAPS (validation.py uyumu)
# =============================================================================

SEVERITY_LEVELS = {
    "critical": "⚠️ KRİTİK",
    "severe": "🔴",
    "normal": "",
}

# validation.py şu key formatını üretir:
#   f"{param}_critical_low/high"
#   f"{param}_severe_low/high"
CRITICAL_MESSAGES = {
    # pH
    "ph_critical_low": "⚠️ KRİTİK: pH çok düşük (hayati düzey).",
    "ph_critical_high": "⚠️ KRİTİK: pH çok yüksek (hayati düzey).",
    "ph_severe_low": "🔴 pH çok düşük (şiddetli asidemi patern).",
    "ph_severe_high": "🔴 pH çok yüksek (şiddetli alkalemi patern).",

    # pCO2
    "pco2_critical_low": "⚠️ KRİTİK: pCO₂ çok düşük (hayati düzey).",
    "pco2_critical_high": "⚠️ KRİTİK: pCO₂ çok yüksek (hayati düzey).",
    "pco2_severe_low": "🔴 pCO₂ çok düşük (şiddetli hipokapni patern).",
    "pco2_severe_high": "🔴 pCO₂ çok yüksek (şiddetli hiperkapni patern).",

    # Na
    "na_critical_low": "⚠️ KRİTİK: Na⁺ çok düşük (hayati düzey).",
    "na_critical_high": "⚠️ KRİTİK: Na⁺ çok yüksek (hayati düzey).",
    "na_severe_low": "🔴 Na⁺ çok düşük (ciddi hiponatremi patern).",
    "na_severe_high": "🔴 Na⁺ çok yüksek (ciddi hipernatremi patern).",

    # Cl
    "cl_critical_low": "⚠️ KRİTİK: Cl⁻ çok düşük (hayati düzey).",
    "cl_critical_high": "⚠️ KRİTİK: Cl⁻ çok yüksek (hayati düzey).",
    "cl_severe_low": "🔴 Cl⁻ çok düşük (ciddi hipokloremi patern).",
    "cl_severe_high": "🔴 Cl⁻ çok yüksek (ciddi hiperkloremi patern).",

    # K
    "k_critical_low": "⚠️ KRİTİK: K⁺ çok düşük (hayati düzey).",
    "k_critical_high": "⚠️ KRİTİK: K⁺ çok yüksek (hayati düzey).",
    "k_severe_low": "🔴 K⁺ çok düşük (ciddi aritmi riski patern).",
    "k_severe_high": "🔴 K⁺ çok yüksek (ciddi aritmi riski patern).",

    # Lactate
    "lactate_critical_high": "⚠️ KRİTİK: Laktat çok yüksek (hayati düzey).",
    "lactate_severe_high": "🔴 Laktat çok yüksek (şiddetli hipoperfüzyon/şok patern).",
}


# =============================================================================
# 🚦 VALİDASYON EŞİKLERİ - ÜÇ KATMANLI MODEL
# =============================================================================
# Referans: Klinik pratiğe dayalı, literatür destekli
#
# KATMAN 1: PHYSIOLOGIC_LIMITS (Hard Limits)
# - Bu sınırların dışındaki değerler FİZYOLOJİK OLARAK İMKANSIZ
# - Giriş reddedilir, analiz yapılmaz
# - Örn: pH 5.0 veya Na 300 → Ölçüm hatası kesin
#
# KATMAN 2: EXTREME_THRESHOLDS (Extreme but Valid)
# - Fizyolojik olarak MÜMKÜN ama NADİR ve KRİTİK
# - Uyarı verilir ama analiz devam eder
# - Klinik aciliyet vurgulanır
# - Örn: pH 6.9 → Şiddetli asidemi, acil müdahale gerekir
#
# KATMAN 3: REFERENCE_RANGES (Normal Ranges)
# - Sağlıklı bireylerdeki tipik değerler
# - Bilgilendirme amaçlı, kısıtlayıcı değil

PHYSIOLOGIC_LIMITS = {
    "ph": (PH_MIN, PH_MAX),           # 6.50-7.90
    "pco2": (PCO2_MIN, PCO2_MAX),     # 5-250 mmHg
    "na": (NA_MIN, NA_MAX),           # 80-220 mmol/L
    "cl": (CL_MIN, CL_MAX),           # 50-200 mmol/L
    "k": (K_MIN, K_MAX),              # 1.5-10 mmol/L
    "lactate": (LACTATE_MIN, LACTATE_MAX),  # 0-40 mmol/L
}

EXTREME_THRESHOLDS = {
    # pH: <7.0 şiddetli asidemi, >7.7 şiddetli alkalemi
    # [KELLUM-2009]: pH <7.1 veya >7.6 acil müdahale gerektirir
    "ph": {"low": 7.0, "high": 7.7},
    
    # pCO2: >80 şiddetli hiperkapni, <20 şiddetli hipokapni
    # >120 genellikle mekanik ventilasyon gerektirir
    "pco2": {"high": 120.0},
    
    # Na: <120 ciddi hiponatremi (serebral ödem riski)
    #     >160 ciddi hipernatremi (nörolojik hasar riski)
    "na": {"low": 120.0, "high": 170.0},
    
    # Cl: <70 şiddetli hipokloremi, >130 şiddetli hiperkloremi
    "cl": {"low": 70.0, "high": 130.0},
    
    # K: <2.5 kardiyak aritmi riski, >6.5 kardiyak arrest riski
    "k": {"low": 2.0, "high": 7.0},
    
    # Laktat: >4 ciddi hipoperfüzyon, >10 şok/çoklu organ yetmezliği
    "lactate": {"high": 10.0},
}

REFERENCE_RANGES = {
    "ph": (PH_NORMAL_LOW, PH_NORMAL_HIGH),    # 7.35-7.45
    "pco2": (PCO2_NORMAL_LOW, PCO2_NORMAL_HIGH),  # 35-45 mmHg
    "na": (135.0, 145.0),           # Normal sodyum
    "cl": (98.0, 110.0),            # Normal klor (bazı kaynaklar 98-106)
    "k": (3.5, 5.0),                # Normal potasyum
    "lactate": (0.5, 2.0),          # Normal laktat
}

# === YUMUŞAK MESAJLAR (Yargılamayan dil) ===
SOFT_MESSAGES = {
    "missing_albumin": "Albümin değeri girilmediği için hipoalbüminemi etkisi değerlendirilemedi.",
    "missing_lactate": "Laktat değeri girilmediği için laktik asidoz değerlendirmesi yapılamadı.",
    "missing_ca": "Ca2+ girilmediği için ileri SID analizi kısıtlı.",
    "missing_mg": "Mg2+ girilmediği için SIDapparent yaklaşık hesaplandı.",
    "missing_po4": "Fosfat girilmediği için SIDeffective yaklaşık hesaplandı.",
    "missing_k": "K+ girilmediği için SIDapparent kısıtlı hesaplandı.",
    "sig_not_calculated": "Yeterli veri olmadığı için SIG hesaplanamadı.",
}

# === FLAGS ===
FLAGS = {
    "VALIDATION_FAILED": "Validasyon başarısız",
    "INCOMPLETE_DATA": "Bazı parametreler eksik",
    "BE_MISMATCH": "BE tutarsızlığı",
    "HCO3_MISMATCH": "HCO3 tutarsızlığı",
    "SIG_APPROXIMATE": "SIG yaklaşık",
    "SIG_UNDERESTIMATED": "SIG düşük hesaplanmış olabilir",
    "SIG_UNRELIABLE": "SIG güvenilir değil",
    "SID_FULL_APPROXIMATE": "SID_full yaklaşık",
    "SID_EFFECTIVE_APPROXIMATE": "SID_effective yaklaşık",
    "BE_CALCULATED": "BE otomatik hesaplandı",
    "HCO3_CALCULATED": "HCO3 hesaplandı",
}

# ============================================================
# ðŸ§  KLİNİK KARAR DESTEK (CDS) NOT SETİ
# Literatür dayanaklı, deterministik, eylemsiz ifadeler
# ============================================================

CDS_NOTES = {
    # === A KATEGORİSİ: FİZİKOKİMYASAL ZORUNLULUKLAR ===
    "sid_low": {
        "condition": "SID < 38 mmol/L",
        "note": "Güçlü iyon farkı azalmış; bu patern, güçlü iyon aracılı metabolik asidoz yönlü etki ile uyumludur.",
        "refs": ["Quintard et al., 2007", "Rehm et al., 2004"]
    },
    "sid_high": {
        "condition": "SID > 44 mmol/L",
        "note": "Güçlü iyon farkı artmış; metabolik alkaloz yönlü etki ile uyumlu patern.",
        "refs": ["Fencl & Leith, 1993"]
    },
    "sig_positive": {
        "condition": "SIG > 2 mmol/L",
        "note": "Ölçülmemiş anyon birikimi mevcut; gizli asidoz yönlü etki ile uyumlu olabilir.",
        "refs": ["Szrama & Smuszkiewicz, 2016", "Maria et al., 2017"]
    },
    "sig_negative": {
        "condition": "SIG < -2 mmol/L",
        "note": "Ölçülmemiş katyon fazlası veya artefakt olasılığı (nadir durum).",
        "refs": ["Fencl & Leith, 1993"]
    },
    "sig_normal": {
        "condition": "|SIG| â‰¤ 2 mmol/L",
        "note": "SIG normal aralıkta; klinik olarak anlamlı ölçülmemiş iyon birikimi saptanmadı.",
        "refs": []
    },
    "albumin_low": {
        "condition": "Albümin < 35 g/L",
        "note": "Albümin düşük; zayıf asit azalması alkaloz yönlü maskeleme etkisi yaratabilir.",
        "refs": ["Kimura et al., 2018", "Quintard et al., 2007"]
    },
    "cl_na_high": {
        "condition": "Cl-/Na+ > 0.75",
        "note": "Yüksek klorür yükü mevcut; hiperkloremik asidoz yönlü etki ile uyumlu patern.",
        "refs": ["Szrama & Smuszkiewicz, 2016", "Kilic et al., 2020"]
    },
    
    # === B KATEGORİSİ: MASKELENME VE KARŞIT ETKİLER ===
    "normal_ph_low_sid": {
        "condition": "Normal pH + düşük SID",
        "note": "Normal pH, zıt yönlü metabolik etkilerin dengesiyle uyumlu olabilir.",
        "refs": ["Szrama & Smuszkiewicz, 2016", "Masevicius & Dubin, 2015"]
    },
    "normal_be_low_sid": {
        "condition": "Normal BE/HCO3 + düşük SID",
        "note": "Klasik analizde normal görünebilir; maskelenmiş güçlü iyon asidozu olasılığı.",
        "refs": ["Quintard et al., 2007"]
    },
    "albumin_low_lactate_high": {
        "condition": "Düşük albümin + yüksek laktat",
        "note": "Zayıf asit azalması (alkaloz yönlü) ve laktat artışı (asidoz yönlü) birbiriyle karşıt etkiler yaratıyor olabilir.",
        "refs": ["Szrama & Smuszkiewicz, 2016", "Fencl & Leith, 1993"]
    },
    
    # === C KATEGORİSİ: PATERN â†’ OLASI MEKANİZMA KÜMELERİ ===
    "pattern_hyperchloremic": {
        "condition": "SIDâ†“ + Cl-â†‘",
        "note": "Bu patern hiperkloremik/dilüsyonel asidoz mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["İzotonik salin infüzyonu", "Renal tübüler asidoz", "Diyare kaynaklı bikarbonat kaybı"],
        "refs": ["Kilic et al., 2020"]
    },
    "pattern_unmeasured_anion": {
        "condition": "Normal laktat + SIGâ†‘",
        "note": "Bu patern ölçülmemiş anyon birikimi mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["Ketoasidoz", "Üremik asidoz", "Toksin (metanol, etilen glikol)", "Sülfat birikimi"],
        "refs": ["Franconieri et al., 2025"]
    },
    "pattern_masked_mixed": {
        "condition": "Albüminâ†“ + pH normal + Laktatâ†‘",
        "note": "Bu patern maskelenmiş karışık bozukluk mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["Sepsis + hipoalbüminemi", "Karaciğer yetmezliği", "Malnutrisyon + enfeksiyon"],
        "refs": ["Szrama & Smuszkiewicz, 2016"]
    },
    "pattern_compensatory": {
        "condition": "SID ve Atot değişimi zıt yönlü",
        "note": "Bu patern kompansatuvar fizyolojik denge mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["Kronik adaptasyon", "Çoklu organ etkileşimi"],
        "refs": ["Tsuboi et al., 2020"]
    },
}

# === KLASİK YAKLAŞIM KARŞILAŞTIRMA MESAJLARI ===
CLASSIC_COMPARISON = {
    "hco3_normal_sid_low": "HCO3- normal görünmesine rağmen SID düşük â†’ klasik analizde metabolik asidoz gözden kaçabilirdi.",
    "normal_be_low_sid": "BE/HCO3 normal görünse de SID düşük â†’ klasik yaklaşım güçlü iyon asidozunu maskelerdi.",
    "albumin_masking": "Düşük albümin mevcut asidozu maskelemiş olabilir â†’ klasik AG düzeltmesi gerekli.",
    "sid_primary": "SID değişikliği primer mekanizma olarak öne çıkıyor â†’ klasik yaklaşımda bu ayrım yapılamaz.",
    "ag_vs_sig": "Anyon gap normal ama SIG yüksek olabilir â†’ ölçülmemiş anyonlar AG'de görünmeyebilir.",
    "mixed_hidden": "Karşıt etkiler birbirini dengelemiş â†’ klasik tek parametre değerlendirmesi yetersiz kalabilir.",
}

# ============================================================
# ðŸ“š HAZIR VAKALAR (Case-Based Learning)
# ============================================================

SAMPLE_CASES = {
    "sepsis_hipoalb": {
        "name": "Sepsis + Hipoalbüminemi",
        "description": "65 yaş, pnömoni kaynaklı sepsis, uzun süreli yoğun bakım",
        "values": {
            "ph": 7.38, "pco2": 32.0, "na": 138.0, "cl": 108.0,
            "k": 4.2, "lactate": 3.5, "albumin_gl": 22.0, "be": -4.0
        },
        "teaching_point": "Normal pH'a rağmen maskelenmiş metabolik asidoz. Hipoalbüminemi alkaloz etkisi, laktik asidoz etkisini kısmen kompanse ediyor."
    },
    "dka": {
        "name": "Diyabetik Ketoasidoz (DKA)",
        "description": "28 yaş, Tip 1 DM, bulantı-kusma, dehidratasyon",
        "values": {
            "ph": 7.18, "pco2": 22.0, "na": 132.0, "cl": 98.0,
            "k": 5.8, "lactate": 2.2, "albumin_gl": 42.0, "be": -18.0
        },
        "teaching_point": "Yüksek anyon gap metabolik asidoz. SIG yüksek (keton anyonları). Uygun respiratuvar kompanzasyon."
    },
    "nacl_infusion": {
        "name": "NaCl İnfüzyonu Sonrası",
        "description": "45 yaş, cerrahi sonrası 4L %0.9 NaCl verilmiş",
        "values": {
            "ph": 7.28, "pco2": 34.0, "na": 142.0, "cl": 116.0,
            "k": 3.8, "lactate": 1.2, "albumin_gl": 38.0, "be": -8.0
        },
        "teaching_point": "Hiperkloremik metabolik asidoz. SID düşük (Cl yüksek). Normal anyon gap. Dilüsyonel asidoz örneği."
    },
    "copd_acute": {
        "name": "KOAH Akut Alevlenme",
        "description": "72 yaş, KOAH, akut solunum sıkıntısı",
        "values": {
            "ph": 7.28, "pco2": 68.0, "na": 140.0, "cl": 98.0,
            "k": 4.5, "lactate": 1.0, "albumin_gl": 36.0, "be": 4.0
        },
        "teaching_point": "Akut respiratuvar asidoz. HCO3 hafif yükselmiş ama kronik kompanzasyon düzeyinde değil."
    },
    "vomiting": {
        "name": "Uzamış Kusma",
        "description": "35 yaş, 3 gündür kusma, dehidratasyon",
        "values": {
            "ph": 7.52, "pco2": 48.0, "na": 138.0, "cl": 88.0,
            "k": 2.8, "lactate": 1.5, "albumin_gl": 44.0, "be": 12.0
        },
        "teaching_point": "Hipokloremik metabolik alkaloz. SID yüksek (Cl düşük). Uygun respiratuvar kompanzasyon."
    },
    "renal_failure": {
        "name": "Kronik Böbrek Yetmezliği",
        "description": "68 yaş, GFR 15, diyaliz öncesi",
        "values": {
            "ph": 7.30, "pco2": 30.0, "na": 136.0, "cl": 106.0,
            "k": 5.6, "lactate": 1.8, "albumin_gl": 32.0, "be": -10.0
        },
        "teaching_point": "Karma asidoz: SID düşük + muhtemel ölçülmemiş anyonlar (sülfat, fosfat). Hipoalbüminemi kısmen maskeleme yapmış."
    },
    "normal": {
        "name": "Normal Kan Gazı",
        "description": "Sağlıklı erişkin, rutin kontrol",
        "values": {
            "ph": 7.40, "pco2": 40.0, "na": 140.0, "cl": 102.0,
            "k": 4.0, "lactate": 0.8, "albumin_gl": 42.0, "be": 0.0
        },
        "teaching_point": "Normal değerler. SID ~38, tüm bileşenler dengede."
    },
    "lactic_acidosis": {
        "name": "Laktik Asidoz (Şok)",
        "description": "55 yaş, septik şok, hipotansiyon",
        "values": {
            "ph": 7.22, "pco2": 24.0, "na": 140.0, "cl": 100.0,
            "k": 4.8, "lactate": 8.5, "albumin_gl": 28.0, "be": -14.0
        },
        "teaching_point": "Ciddi laktik asidoz. Laktat etkisi baskın. Hipoalbüminemi kısmen maskeliyor - gerçek asidoz daha şiddetli."
    },
    "akoglu_triple": {
        "name": "Triple Bozukluk (Akoğlu Vaka 1)",
        "description": "pH 7.48 ama 5 ayrı asit-baz bozukluğu - klasik yaklaşım yetersiz kalır",
        "values": {
            "ph": 7.48, "pco2": 60.0, "na": 132.0, "cl": 76.0,
            "lactate": 1.9, "albumin_gl": 18.0
        },
        "teaching_point": "Stewart'ın gücü: pH alkalotik ama altında 5 ayrı mekanizma! 1) Respiratuvar asidoz (pCO2↑), 2) Metabolik alkaloz (SID↑, Cl↓), 3) Hipoalbüminemi alkalozu, 4) Laktat yüksekliği, 5) Kompanzasyon yetersizliği. Klasik yaklaşım sadece 'metabolik alkaloz + respiratuvar kompanzasyon' der, gerçek kompleksliği kaçırır."
    },
    "akoglu_nagma_lactic": {
        "name": "NAGMA + Laktik Asidoz (Akoğlu Vaka 2)",
        "description": "pH 7.07 - ciddi hipoalbüminemi gerçek asidozu maskeler",
        "values": {
            "ph": 7.07, "pco2": 50.0, "na": 135.0, "cl": 113.0,
            "lactate": 3.3, "albumin_gl": 8.0
        },
        "teaching_point": "Stewart'ın maskeleme tespiti: Ciddi hipoalbüminemi (8 g/L) alkaloz yönünde güçlü etki. Gerçek asidoz çok daha şiddetli! SID düşük (NAGMA) + laktat yüksek + respiratuvar asidoz da var (pCO2 50, yetersiz kompanzasyon). Klasik AG hesabı hipoalbüminemi nedeniyle düşük çıkar, HAGMA'yı kaçırır. Stewart düzeltilmiş SIG ile gerçek ölçülmemiş anyon yükünü gösterir."
    },
    "akoglu_nagma_hidden_alk": {
        "name": "NAGMA + Gizli Alkaloz (Akoğlu Vaka 3)",
        "description": "pH 7.30 - hiperkloremik asidoz, ama SID analizi gizli alkalozu ortaya çıkarır",
        "values": {
            "ph": 7.30, "pco2": 30.0, "na": 140.0, "cl": 115.0,
            "lactate": 1.3, "albumin_gl": 45.0
        },
        "teaching_point": "Stewart'ın 'gizli bozukluk' tespiti: Klasik yaklaşım sadece NAGMA (hiperkloremik asidoz) görür. Ancak Stewart SID analiziyle gizli bir alkaloz mekanizmasının varlığını ortaya çıkarır - muhtemelen geçirilmiş kusma veya diüretik kullanımı. pH 7.30 olmasının sebebi NAGMA ile gizli alkalozun karşıt etkisi. Tek başına NAGMA olsaydı pH çok daha düşük olurdu."
    },
    "akoglu_hagma_nagma": {
        "name": "HAGMA + NAGMA Birlikteliği (Akoğlu Vaka 4)",
        "description": "pH 7.05 - karma asidoz, her iki tip birden",
        "values": {
            "ph": 7.05, "pco2": 14.0, "na": 122.0, "cl": 88.0,
            "lactate": 0.5, "albumin_gl": 55.0
        },
        "teaching_point": "Stewart'ın karma bozukluk ayrıştırması: Klasik AG yüksek ama laktat normal - demek ki başka ölçülmemiş anyonlar var (keton, üremik toksinler vb). Aynı zamanda Cl/Na oranı bozuk değil ama SID analizi ile NAGMA bileşeni de tespit edilir. Stewart her iki mekanizmanın ayrı ayrı katkısını gösterir. Not: Ciddi hiponatremi (122) ve yüksek albümin (55) - konsantrasyon sorunları olabilir."
    },
    "akoglu_pure_nagma": {
        "name": "Saf NAGMA (Akoğlu Vaka 5)",
        "description": "pH 7.05 - normal anyon gap asidozu, Stewart'la mekanizma netleşir",
        "values": {
            "ph": 7.05, "pco2": 22.0, "na": 132.0, "cl": 112.0,
            "lactate": 0.5, "albumin_gl": 32.0
        },
        "teaching_point": "Stewart'ın NAGMA mekanizma açıklaması: Klasik yaklaşım 'normal AG asidoz, böbrek veya ishal' der, mekanizma belirsiz kalır. Stewart SID düşüklüğünü (hiperkloremi veya hiponatremi) açıkça gösterir. Bu vakada Cl/Na = 112/132 = 0.85 yüksek (normal ~0.73), demek ki görece hiperkloremi var. SIG normal, yani ölçülmemiş anyon yok. Saf güçlü iyon dengesizliği. Hipoalbüminemi (32) kısmen maskeler - düzeltme yapınca asidoz daha belirgin."
    },
}

# === UI METİNLERİ ===
UI_TEXTS = {
    "app_title": "Stewart Asit-Baz Analizi",
    "app_subtitle": "Fizikokimyasal yaklaşımla kan gazı değerlendirmesi",
    "landing_description": """
Bu araç, kompleks asit-baz bozukluklarını **Stewart-Fencl sentezi** ile analiz etmek için 
geliştirilmiş bir eğitim ve klinik destek aracıdır.

**Klasik yaklaşımdan farkı:**
- Sadece pH ve HCO3'e bakmak yerine, asit-baz dengesini etkileyen **tüm güçlü iyonları** değerlendirir
- **Maskelenmiş bozuklukları** (örn. hipoalbüminemi + asidoz) ortaya çıkarır  
- Her bileşenin **ayrı ayrı katkısını** gösterir
""",
    "disclaimer": "âš•ï¸ Bu araç klinik karar destek sistemi değildir. Eğitim amaçlıdır. Tüm klinik kararlar uzman hekim değerlendirmesi gerektirir.",
    "disclaimer_short": "Eğitim amaçlıdır. Klinik karar için uzman değerlendirmesi gerekir.",
}

# === CONTRIBUTION-BASED LABELS (Non-diagnostic, mechanism-focused) ===
CONTRIBUTION_LABELS = {
    # Contribution levels
    "dominant": "dominant",      # >50% contribution
    "significant": "significant", # 25-50% contribution
    "contributing": "contributing", # <25% contribution
    
    # Mechanism names (non-diagnostic)
    "sid_acidosis": "Güçlü iyon (SID) aracılı metabolik asidoz",
    "sid_alkalosis": "Güçlü iyon (SID) aracılı metabolik alkaloz",
    "lactate_acidosis": "Laktat aracılı metabolik asidoz",
    "albumin_alkalosis": "Zayıf asit azalmasına (hipoalbüminemi) bağlı alkaloz etkisi",
    "albumin_acidosis": "Zayıf asit artışına bağlı asidoz etkisi",
    "unmeasured_anion_acidosis": "Ölçülmemiş anyon aracılı metabolik asidoz",
    "unmeasured_cation_alkalosis": "Ölçülmemiş katyon etkisi",
    
    # Direction labels for SID table
    "sid_low_direction": "Güçlü iyon aracılı metabolik asidoz yönünde",
    "sid_high_direction": "Güçlü iyon aracılı metabolik alkaloz yönünde",
    "sid_normal_direction": "Nötr (normal SID)",
    
    # Summary labels
    "dominant_mechanism": "Dominant metabolik mekanizma",
    "significant_mechanisms": "Anlamlı katkıda bulunan mekanizmalar",
    "contributing_mechanisms": "Katkıda bulunan mekanizmalar",
    "respiratory_status": "Solunumsal durum",
    
    # Pattern descriptions (non-diagnostic)
    "pattern_unmeasured_anion": "Bu patern, ölçülmemiş anyon aracılı metabolik asidoz ile uyumludur (örn. keton birikimi, toksinler, organik asitler).",
    "pattern_hyperchloremic": "Bu patern, hiperkloremik (dilüsyonel) metabolik asidoz ile uyumludur.",
    "pattern_lactic": "Bu patern, laktat birikimi aracılı metabolik asidoz ile uyumludur.",
    "pattern_mixed_masking": "Karşıt yönlü etkiler birbirini kısmen maskelemektedir.",
}

# SID interpretation thresholds
SID_INTERPRETATION = {
    "low": {"threshold": 36, "direction": "acidosis", "label": "Güçlü iyon aracılı metabolik asidoz yönünde"},
    "normal_low": {"threshold": 36, "direction": "normal", "label": "Normal aralığın alt sınırı"},
    "normal": {"threshold": 38, "direction": "normal", "label": "Normal"},
    "normal_high": {"threshold": 42, "direction": "normal", "label": "Normal aralığın üst sınırı"},
    "high": {"threshold": 44, "direction": "alkalosis", "label": "Güçlü iyon aracılı metabolik alkaloz yönünde"},
}
REFERENCES = {
    "fencl_1993": "Fencl V, Leith DE. Stewart's quantitative acid-base chemistry. Respir Physiol. 1993",
    "rehm_2004": "Rehm M, et al. Stewart's theory of acid-base chemistry. Anaesthesist. 2004",
    "quintard_2007": "Quintard H, et al. Strong ion gap and metabolic acidosis in ICU. Crit Care Med. 2007",
    "szrama_2016": "Szrama J, Smuszkiewicz P. Stewart approach in sepsis patients. J Crit Care. 2016",
    "maria_2017": "Maria TH, et al. Traditional vs Stewart approach comparison. 2017",
    "masevicius_2015": "Masevicius FD, Dubin A. Clinical performance of Stewart variables. 2015",
    "kilic_2020": "Kilic O, et al. IV fluids and acid-base effects. 2020",
    "franconieri_2025": "Franconieri F, et al. Ketosis and unmeasured anions. 2025",
    "tsuboi_2020": "Tsuboi N, et al. Clinical application modeling. 2020",
    "kimura_2018": "Kimura S, et al. Albumin masking effect. 2018",
    "stewart_1983": "Stewart PA. Modern quantitative acid-base chemistry. Can J Physiol Pharmacol. 1983",
    "morgan_2019": "Morgan TJ. The Stewart approach. Clinica Chimica Acta. 2019",
    "story_2016": "Story DA. Stewart acid-base. Anaesthesia Intensive Care. 2016",
}

# ============================================================
# ðŸ“– PARAMETRE TANIMLARI (Tooltip / Help için)
# ============================================================

PARAM_DEFINITIONS = {
    # === SID Tanımları ===
    "sid_simple": {
        "short": "Na âˆ’ Cl farkı. Klor yükünü değerlendirmek için pratik gösterge.",
        "long": """**SID_simple (Na âˆ’ Cl)**

Sodyum ile klor arasındaki farktır. Klor yükünü değerlendirmek için pratik bir göstergedir.

**Normal:** â‰ˆ 36â€“40 mmol/L

**Düşükse:**
â€¢ Klor göreceli olarak yüksek
â€¢ Hiperkloremik metabolik asidoz eğilimi

**Yüksekse:**
â€¢ Klor göreceli olarak düşük
â€¢ Metabolik alkaloz eğilimi (örn. kusma, diüretik)""",
        "normal": "â‰ˆ 38 mmol/L"
    },
    
    "sid_basic": {
        "short": "Na âˆ’ Cl âˆ’ Laktat. Laktatın asidoz yükünü SID üzerinden yansıtır.",
        "long": """**SID_basic (Na âˆ’ Cl âˆ’ Lactate)**

Naâ€“Cl farkına laktatın eklenmiş halidir. Laktatın asidoz yükünü SID üzerinden yansıtır.

**Normal:** â‰ˆ 36â€“38 mmol/L

**Düşükse:**
â€¢ Laktat artışı ve/veya klor fazlalığı
â€¢ Laktik Â± hiperkloremik metabolik asidoz

**Yüksekse:**
â€¢ Metabolik alkaloz yönlü durumlar""",
        "normal": "â‰ˆ 37 mmol/L"
    },
    
    "sid_full": {
        "short": "Tüm güçlü iyonlarla hesaplanan apparent SID. Stewart'ın ana değişkeni.",
        "long": """**SID_full / SIDapparent (Na+K+Ca+Mg âˆ’ Cl âˆ’ Lactate)**

Tüm ölçülen güçlü iyonlar kullanılarak hesaplanan teorik apparent SID. Stewart yaklaşımının ana değişkenlerinden biridir.

**Normal:** â‰ˆ 40â€“44 mmol/L

**Düşükse:**
â€¢ Güçlü anyon fazlalığı veya katyon azlığı
â€¢ Primer metabolik asidoz

**Yüksekse:**
â€¢ Güçlü katyon fazlalığı veya anyon azlığı
â€¢ Primer metabolik alkaloz

âš ï¸ Ca2+/Mg2+ eksikse yaklaşık (approximate) kabul edilir.""",
        "normal": "â‰ˆ 40-44 mmol/L"
    },
    
    "sid_effective": {
        "short": "HCO3 ve zayıf asitlerin etkisini içeren 'etkin' SID. SIG hesabında kullanılır.",
        "long": """**SIDeffective**

Bikarbonat ve zayıf asitlerin (albümin, fosfat) etkisini içeren "etkin" SID değeridir.

SIG hesaplamasında kullanılır:
**SIG = SIDapparent âˆ’ SIDeffective**

Doğrudan referans aralığı yoktur; SIDapparent ile karşılaştırılarak yorumlanır.""",
        "normal": "SIDa ile karşılaştırılır"
    },
    
    # === Stewart Parametreleri ===
    "atot": {
        "short": "Zayıf asitlerin (albümin, fosfat) toplam etkisi.",
        "long": """**Atot (Total Weak Acids)**

Zayıf asitlerin (özellikle albümin ve fosfat) toplam etkisini temsil eder.

**Normal:** â‰ˆ 2.5â€“3.0 mmol/L (albümin ~40 g/L varsayımıyla)

**Düşükse:**
â€¢ Albümin düşüklüğü
â€¢ pH alkaloz yönüne itilir
â€¢ Metabolik asidoz maskelenebilir

**Yüksekse:**
â€¢ Albümin/fosfat artışı
â€¢ Metabolik asidoz eğilimi""",
        "normal": "â‰ˆ 2.5-3.0 mmol/L"
    },
    
    "sig": {
        "short": "Ölçülmemiş anyonların (keton, toksin, sülfat vb.) varlığını gösterir.",
        "long": """**SIG (Strong Ion Gap)**

Ölçülmemiş anyonların (ketonlar, toksinler, sülfatlar vb.) varlığını gösterir.

**Formül:** SIG = SIDapparent âˆ’ SIDeffective

**Normal:** â‰ˆ âˆ’2 ile +2 mmol/L

**Yüksekse (> +2):**
â€¢ Ölçülmemiş anyon artışı
â€¢ Klasik AG normal olsa bile gizli asidoz olabilir

**Düşükse (< âˆ’2):**
â€¢ Ölçülmemiş katyonlar veya ölçüm artefaktı
â€¢ Klinik olarak nadir

âš ï¸ Eksik elektrolitlerde yaklaşık kabul edilir.""",
        "normal": "âˆ’2 ile +2 mmol/L"
    },
    
    "cl_na_ratio": {
        "short": "Klor yükünü sodyuma göre değerlendiren pratik oran.",
        "long": """**Cl/Na Oranı**

Klor yükünü sodyuma göre değerlendiren pratik bir orandır.

**Normal:** â‰ˆ 0.75 â€“ 0.80

**Yüksekse:**
â€¢ Göreceli klor fazlalığı
â€¢ Hiperkloremik metabolik asidoz lehine

**Düşükse:**
â€¢ Klor kaybı
â€¢ Metabolik alkaloz lehine""",
        "normal": "0.75-0.80"
    },
    
    # === Anyon Gap ===
    "anion_gap": {
        "short": "Klasik yaklaşımla ölçülen anyon-katyon farkı. AG = Na âˆ’ (Cl + HCO3)",
        "long": """**Anyon Gap (AG)**

Klasik yaklaşımla ölçülen anyonâ€“katyon farkı.

**Formül:** AG = Na âˆ’ (Cl + HCO3)

**Normal:** â‰ˆ 8â€“12 mmol/L

**Yüksekse:**
â€¢ Laktat, keton, toksin gibi asit yükleri
â€¢ Yüksek AG metabolik asidoz (HAGMA)

**Normal/Düşükse:**
â€¢ Asidoz yok veya hiperkloremik asidoz (NAGMA) olabilir""",
        "normal": "8-12 mmol/L"
    },
    
    "anion_gap_corrected": {
        "short": "Albümin düzeyi dikkate alınarak düzeltilmiş AG.",
        "long": """**Düzeltilmiş Anyon Gap**

Albümin düzeyi dikkate alınarak hesaplanan AG.

**Formül:** AG_düz = AG + 2.5 Ã— (4.2 âˆ’ Albümin_g/dL)

**Normal:** â‰ˆ 12â€“16 mmol/L

**Yüksekse:**
â€¢ Albümin düşüklüğüne rağmen gerçek AG artışı
â€¢ Gizli yüksek AG asidozu

**Normal görünüyorsa:**
â€¢ Albümin düşüklüğü klasik AG'yi maskelemiş olabilir""",
        "normal": "12-16 mmol/L"
    },
    
    # === Bileşen Etkileri ===
    "sid_effect": {
        "short": "SID'in BE'ye katkısı. Negatif = asidoz yönünde, Pozitif = alkaloz yönünde.",
        "long": """**SID Etkisi**

SID'in Base Excess'e katkısıdır.

**Formül:** SID_effect = SID_simple âˆ’ 38

**Negatif değer:** Asidoz yönünde etki (hiperkloremik)
**Pozitif değer:** Alkaloz yönünde etki (hipokloremik)""",
        "normal": "0 Â± 2 mEq/L"
    },
    
    "albumin_effect": {
        "short": "Albüminin BE'ye katkısı. Düşük albümin = alkaloz yönünde etki.",
        "long": """**Albümin Etkisi**

Albüminin Base Excess'e katkısıdır.

**Formül:** Alb_effect = 2.5 Ã— (4.2 âˆ’ Albümin_g/dL)

**Pozitif değer (düşük albümin):** Alkaloz yönünde etki, asidozu maskeleyebilir
**Negatif değer (yüksek albümin):** Asidoz yönünde etki""",
        "normal": "0 Â± 2 mEq/L"
    },
    
    "lactate_effect": {
        "short": "Laktatın BE'ye katkısı. Her mmol/L laktat â‰ˆ 1 mEq/L asidoz.",
        "long": """**Laktat Etkisi**

Laktatın Base Excess'e katkısıdır.

**Formül:** Lac_effect = âˆ’Laktat

Her 1 mmol/L laktat artışı â‰ˆ 1 mEq/L asidoz etkisi yapar.""",
        "normal": "âˆ’1 ile 0 mEq/L"
    },
    
    "residual_effect": {
        "short": "Açıklanamayan kısım. Negatif = ölçülmemiş anyonlar olabilir.",
        "long": """**Residual / Ölçülmemiş Bileşen**

BE'den bilinen bileşenlerin çıkarılmasıyla elde edilen açıklanamayan kısımdır.

**Formül:** Residual = BE âˆ’ SID_effect âˆ’ Alb_effect âˆ’ Lac_effect

**Negatif değer:** Ölçülmemiş anyonlar (keton, toksin vb.) olabilir
**Pozitif değer:** Ölçülmemiş katyonlar (nadir)

âš ï¸ Bu tam SIG değildir, Fencl-derived yaklaşık değerdir.""",
        "normal": "0 Â± 2 mEq/L"
    },
    
    # === Temel Kan Gazı ===
    "ph": {
        "short": "Kan asitliği. < 7.35 asidemi, > 7.45 alkalemi.",
        "long": """**pH**

Kanın asitlik derecesini gösteren logaritmik ölçek.

**Normal:** 7.35 â€“ 7.45

**< 7.35:** Asidemi
**> 7.45:** Alkalemi""",
        "normal": "7.35-7.45"
    },
    
    "pco2": {
        "short": "Karbondioksit parsiyel basıncı. Solunumsal bileşeni yansıtır.",
        "long": """**pCO2 (mmHg)**

Karbondioksit parsiyel basıncı. Asit-baz dengesinin solunumsal bileşenini yansıtır.

**Normal:** 35â€“45 mmHg

**Yüksekse:** Respiratuvar asidoz (hipoventilasyon)
**Düşükse:** Respiratuvar alkaloz (hiperventilasyon)""",
        "normal": "35-45 mmHg"
    },
    
    "hco3": {
        "short": "Bikarbonat. Metabolik bileşeni yansıtır.",
        "long": """**HCO3- (mEq/L)**

Bikarbonat konsantrasyonu. Asit-baz dengesinin metabolik bileşenini yansıtır.

**Normal:** 22â€“26 mEq/L

**Düşükse:** Metabolik asidoz
**Yüksekse:** Metabolik alkaloz""",
        "normal": "22-26 mEq/L"
    },
    
    "be": {
        "short": "Base Excess. Metabolik bileşenin miktarını gösterir.",
        "long": """**Base Excess (mEq/L)**

Metabolik asit-baz bozukluğunun miktarını gösteren değer.

**Normal:** âˆ’2 ile +2 mEq/L

**Negatif:** Metabolik asidoz (baz eksikliği)
**Pozitif:** Metabolik alkaloz (baz fazlalığı)""",
        "normal": "âˆ’2 ile +2 mEq/L"
    },
}

# Kısa tooltip'ler için helper
def get_tooltip(param: str) -> str:
    """Parametre için kısa tooltip döndür"""
    if param in PARAM_DEFINITIONS:
        return PARAM_DEFINITIONS[param]["short"]
    return ""

def get_full_definition(param: str) -> str:
    """Parametre için uzun tanım döndür"""
    if param in PARAM_DEFINITIONS:
        return PARAM_DEFINITIONS[param]["long"]
    return ""
