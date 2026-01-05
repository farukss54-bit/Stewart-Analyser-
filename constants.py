# constants.py
# Stewart Asit-Baz Analizi - Sabitler ve Normal Aralıklar
# Tüm eşik değerleri burada tanımlanır, UI sadece bunları okur.

# === pH Aralıkları ===
PH_MIN = 6.80
PH_MAX = 7.80
PH_NORMAL_LOW = 7.35
PH_NORMAL_HIGH = 7.45

# === pCO2 Aralıkları (mmHg) ===
PCO2_MIN = 10.0
PCO2_MAX = 120.0
PCO2_NORMAL_LOW = 35.0
PCO2_NORMAL_HIGH = 45.0
PCO2_NORMAL = 40.0

# === HCO3 Aralıkları (mEq/L) ===
HCO3_MIN = 5.0
HCO3_MAX = 50.0
HCO3_NORMAL = 24.0
HCO3_MISMATCH_THRESHOLD = 2.0  # Manuel vs hesaplanan fark eşiği

# === Elektrolit Aralıkları (mmol/L) ===
NA_MIN = 100.0
NA_MAX = 180.0
NA_NORMAL = 140.0

K_MIN = 2.0
K_MAX = 8.0
K_NORMAL = 4.0

CL_MIN = 70.0
CL_MAX = 140.0
CL_NORMAL = 100.0

CA_MIN = 0.5
CA_MAX = 2.5
CA_NORMAL = 1.25

MG_MIN = 0.3
MG_MAX = 3.0
MG_NORMAL = 0.85

LACTATE_MIN = 0.0
LACTATE_MAX = 25.0
LACTATE_NORMAL = 1.0
LACTATE_THRESHOLD = 2.0  # Laktik asidoz eşiği

# === Albümin ===
ALBUMIN_MIN_GL = 5.0
ALBUMIN_MAX_GL = 60.0
ALBUMIN_NORMAL_GL = 40.0
ALBUMIN_MIN_GDL = 0.5
ALBUMIN_MAX_GDL = 6.0
ALBUMIN_NORMAL_GDL = 4.0

# === Fosfat (mmol/L) ===
PO4_MIN = 0.3
PO4_MAX = 4.0
PO4_NORMAL = 1.0

# === Base Excess (mEq/L) ===
BE_MIN = -30.0
BE_MAX = 30.0
BE_NORMAL = 0.0
BE_MISMATCH_THRESHOLD = 2.0  # Hesaplanan vs girilen BE fark eşiği

# === SID Değerleri (mEq/L) ===
SID_NORMAL_SIMPLE = 38.0      # Na - Cl için normal
SID_NORMAL_BASIC = 37.0       # Na - Cl - Lac için normal
SID_NORMAL_FULL = 40.0        # Tam SIDapparent için normal
SID_NORMAL_RANGE = 2.0        # ± tolerans
SID_THRESHOLD = 2.0           # Klinik anlamlılık eşiği

# === SIG Değerleri (mEq/L) ===
# SIG = SIDapparent - SIDeffective
# Pozitif SIG → ölçülmemiş anyonlar (HAGMA)
# Negatif SIG → ölçülmemiş katyonlar (nadir)
SIG_NORMAL = 0.0
SIG_THRESHOLD = 2.0  # ± tolerans

# === Anyon Gap (mEq/L) ===
AG_NORMAL = 12.0
AG_THRESHOLD = 2.0

# === Klinik Yorum Eşikleri ===
CLINICAL_SIGNIFICANCE_THRESHOLD = 2.0  # mEq/L altındaki değişimler "normal" kabul

# === Kompanzasyon Sabitleri ===

# Metabolik Asidoz - Winter's formülü
WINTERS_HCO3_COEFFICIENT = 1.5
WINTERS_CONSTANT = 8
WINTERS_TOLERANCE = 2

# Metabolik Alkaloz
ALKALOSIS_PCO2_COEFFICIENT = 0.7
ALKALOSIS_PCO2_CONSTANT = 21
ALKALOSIS_TOLERANCE = 2

# Akut Respiratuvar Asidoz: Her 10 mmHg pCO2 artışı → HCO3 1 mEq/L artar
RESP_ACIDOSIS_ACUTE_COEFFICIENT = 0.1  # ΔHCO3 = 0.1 × ΔpCO2

# Kronik Respiratuvar Asidoz: Her 10 mmHg pCO2 artışı → HCO3 3.5 mEq/L artar
RESP_ACIDOSIS_CHRONIC_COEFFICIENT = 0.35  # ΔHCO3 = 0.35 × ΔpCO2

# Akut Respiratuvar Alkaloz: Her 10 mmHg pCO2 düşüşü → HCO3 2 mEq/L düşer
RESP_ALKALOSIS_ACUTE_COEFFICIENT = 0.2  # ΔHCO3 = 0.2 × ΔpCO2

# Kronik Respiratuvar Alkaloz: Her 10 mmHg pCO2 düşüşü → HCO3 5 mEq/L düşer
RESP_ALKALOSIS_CHRONIC_COEFFICIENT = 0.5  # ΔHCO3 = 0.5 × ΔpCO2

COMPENSATION_TOLERANCE = 2  # ± mEq/L veya mmHg

# === Validasyon Mesajları ===
VALIDATION_MESSAGES = {
    # Hatalar (hesaplama engeller)
    "ph_out_of_range": "pH değeri fizyolojik sınırlar dışında (6.80-7.80)",
    "pco2_out_of_range": "pCO₂ değeri kabul edilebilir sınırlar dışında (10-120 mmHg)",
    "na_out_of_range": "Na⁺ değeri kabul edilebilir sınırlar dışında (100-180 mmol/L)",
    "cl_out_of_range": "Cl⁻ değeri kabul edilebilir sınırlar dışında (70-140 mmol/L)",
    "k_out_of_range": "K⁺ değeri kabul edilebilir sınırlar dışında (2-8 mmol/L)",
    "ca_out_of_range": "Ca²⁺ değeri kabul edilebilir sınırlar dışında (0.5-2.5 mmol/L)",
    "mg_out_of_range": "Mg²⁺ değeri kabul edilebilir sınırlar dışında (0.3-3 mmol/L)",
    "lactate_out_of_range": "Laktat değeri kabul edilebilir sınırlar dışında (0-25 mmol/L)",
    "albumin_gl_out_of_range": "Albümin (g/L) değeri kabul edilebilir sınırlar dışında (5-60 g/L)",
    "albumin_gdl_out_of_range": "Albümin (g/dL) değeri kabul edilebilir sınırlar dışında (0.5-6 g/dL)",
    "po4_out_of_range": "Fosfat değeri kabul edilebilir sınırlar dışında (0.3-4 mmol/L)",
    
    # Uyarılar (hesaplama devam eder)
    "be_mismatch": "Girilen BE ile hesaplanan BE arasında >2 mEq/L fark var. Girdileri kontrol edin.",
    "hco3_mismatch": "Girilen HCO₃ ile Henderson-Hasselbalch'tan hesaplanan arasında >2 mEq/L fark var.",
    "missing_albumin": "Albümin girilmedi. Hipoalbüminemi maskelenmiş asidoza neden olabilir.",
    "missing_lactate": "Laktat girilmedi. Laktik asidoz değerlendirilemez.",
    "missing_k": "K⁺ girilmedi. SIDapparent tam hesaplanamaz.",
    "missing_ca": "Ca²⁺ girilmedi. SIDapparent yaklaşık değerdir.",
    "missing_mg": "Mg²⁺ girilmedi. SIDapparent yaklaşık değerdir.",
    "missing_po4": "Fosfat girilmedi. SIDeffective yaklaşık değerdir.",
    
    # SIG güvenilirlik uyarıları
    "sig_no_lactate": "Laktat olmadan SIG muhtemelen underestimate edilmiştir.",
    "sig_approximate": "Ca/Mg eksik olduğundan SIG yaklaşık değerdir.",
    "sig_unreliable": "Kritik parametreler eksik, SIG hesaplanamadı.",
}

# === Flag Tanımları ===
FLAGS = {
    # Veri kalitesi
    "VALIDATION_FAILED": "Validasyon başarısız, hesaplama yapılamadı",
    "INCOMPLETE_DATA": "Bazı parametreler eksik",
    "BE_MISMATCH": "BE tutarsızlığı tespit edildi",
    "HCO3_MISMATCH": "HCO3 tutarsızlığı tespit edildi",
    
    # Varsayım flagleri
    "ASSUMED_CA": "Ca²⁺ için varsayılan değer kullanıldı",
    "ASSUMED_PO4": "PO₄ için varsayılan değer kullanıldı",
    
    # SIG güvenilirlik
    "SIG_APPROXIMATE": "SIG yaklaşık değerdir (eksik parametreler)",
    "SIG_UNDERESTIMATED": "SIG muhtemelen düşük hesaplandı (laktat eksik)",
    "SIG_UNRELIABLE": "SIG güvenilir değil",
    
    # Hesaplama kaynağı
    "BE_CALCULATED": "BE otomatik hesaplandı",
    "HCO3_CALCULATED": "HCO₃ Henderson-Hasselbalch'tan hesaplandı",
}

# === Bozukluk Etiketleri (ML için) ===
DISORDER_LABELS = [
    "normal",
    "metabolic_acidosis_hagma",
    "metabolic_acidosis_nagma", 
    "metabolic_acidosis_lactic",
    "metabolic_acidosis_hyperchloremic",
    "metabolic_alkalosis",
    "metabolic_alkalosis_hypoalbuminemic",
    "respiratory_acidosis_acute",
    "respiratory_acidosis_chronic",
    "respiratory_alkalosis_acute",
    "respiratory_alkalosis_chronic",
    "mixed_metabolic_acidosis_alkalosis",
    "mixed_metabolic_respiratory",
    "triple_disorder",
]

# === Formül Sabitleri ===
# Henderson-Hasselbalch
HH_CONSTANT = 6.1
HH_SOLUBILITY = 0.03

# BE hesaplama katsayıları (Van Slyke denklemi yaklaşımı)
BE_HCO3_COEFFICIENT = 0.93
BE_HCO3_NORMAL = 24.4
BE_PH_COEFFICIENT = 14.8
BE_PH_NORMAL = 7.40

# SIDeffective hesaplama katsayıları
ALBUMIN_PH_COEFFICIENT = 0.123
ALBUMIN_CONSTANT = 0.631
PO4_PH_COEFFICIENT = 0.309
PO4_CONSTANT = 0.469

# Atot hesaplama katsayıları
ATOT_ALBUMIN_COEFFICIENT = 0.123
ATOT_PO4_COEFFICIENT = 0.309
