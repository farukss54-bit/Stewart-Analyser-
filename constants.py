# constants.py
# Stewart Asit-Baz Analizi - Sabitler, CDS Notları ve Hazır Vakalar
# v3.0 - Klinik Karar Destek Entegrasyonu

# === pH Aralıkları ===
# Hard physiologic acceptance limits (very permissive for critical care)
PH_MIN = 6.50
PH_MAX = 7.90
PH_NORMAL_LOW = 7.35
PH_NORMAL_HIGH = 7.45

# === pCO2 Aralıkları (mmHg) ===
# Hard physiologic acceptance limits (very permissive for critical care)
PCO2_MIN = 5.0
PCO2_MAX = 250.0
PCO2_NORMAL_LOW = 35.0
PCO2_NORMAL_HIGH = 45.0
PCO2_NORMAL = 40.0

# === HCO3 Aralıkları (mEq/L) ===
HCO3_MIN = 5.0
HCO3_MAX = 50.0
HCO3_NORMAL = 24.0
HCO3_MISMATCH_THRESHOLD = 2.0

# === Elektrolit Aralıkları (mmol/L) ===
# Hard physiologic acceptance limits (very permissive for critical care)
NA_MIN = 80.0
NA_MAX = 220.0
NA_NORMAL = 140.0

K_MIN = 1.5
K_MAX = 10.0
K_NORMAL = 4.0

CL_MIN = 50.0
CL_MAX = 200.0
CL_NORMAL = 100.0

CA_MIN = 0.5
CA_MAX = 2.5
CA_NORMAL = 1.25

MG_MIN = 0.3
MG_MAX = 3.0
MG_NORMAL = 0.85

LACTATE_MIN = 0.0
LACTATE_MAX = 40.0
LACTATE_NORMAL = 1.0
LACTATE_THRESHOLD = 2.0

# === Albümin ===
ALBUMIN_MIN_GL = 5.0
ALBUMIN_MAX_GL = 60.0
ALBUMIN_NORMAL_GL = 40.0
ALBUMIN_LOW_GL = 35.0  # CDS için eşik
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
BE_MISMATCH_THRESHOLD = 2.0

# === SID Değerleri (mEq/L) ===
SID_NORMAL_SIMPLE = 38.0
SID_NORMAL_BASIC = 37.0
SID_NORMAL_FULL = 40.0
SID_LOW_THRESHOLD = 38.0   # CDS: SID düşük
SID_HIGH_THRESHOLD = 44.0  # CDS: SID yüksek
SID_NORMAL_RANGE = 2.0
SID_THRESHOLD = 2.0

# === SIG Değerleri (mEq/L) ===
SIG_NORMAL = 0.0
SIG_THRESHOLD = 2.0
SIG_HIGH = 2.0   # CDS: Ölçülmemiş anyon
SIG_LOW = -2.0   # CDS: Ölçülmemiş katyon

# === Cl/Na Oranı ===
CL_NA_RATIO_THRESHOLD = 0.75  # CDS: Hiperkloremik asidoz

# === Anyon Gap (mEq/L) ===
AG_NORMAL = 12.0
AG_THRESHOLD = 2.0

# === Klinik Yorum Eşikleri ===
CLINICAL_SIGNIFICANCE_THRESHOLD = 2.0

# === Kompanzasyon Sabitleri ===
WINTERS_HCO3_COEFFICIENT = 1.5
WINTERS_CONSTANT = 8
WINTERS_TOLERANCE = 2

ALKALOSIS_PCO2_COEFFICIENT = 0.7
ALKALOSIS_PCO2_CONSTANT = 21
ALKALOSIS_TOLERANCE = 2

RESP_ACIDOSIS_ACUTE_COEFFICIENT = 0.1
RESP_ACIDOSIS_CHRONIC_COEFFICIENT = 0.35
RESP_ALKALOSIS_ACUTE_COEFFICIENT = 0.2
RESP_ALKALOSIS_CHRONIC_COEFFICIENT = 0.5
COMPENSATION_TOLERANCE = 2

# === Formül Sabitleri ===
HH_CONSTANT = 6.1
HH_SOLUBILITY = 0.03
BE_HCO3_COEFFICIENT = 1.1
BE_HCO3_NORMAL = 24.0
BE_PH_COEFFICIENT = 32.0
BE_PH_NORMAL = 7.40
ALBUMIN_PH_COEFFICIENT = 0.123
ALBUMIN_CONSTANT = 0.631
PO4_PH_COEFFICIENT = 0.309
PO4_CONSTANT = 0.469
ATOT_ALBUMIN_COEFFICIENT = 0.123
ATOT_PO4_COEFFICIENT = 0.309

# === VALIDASYON MESAJLARI ===
VALIDATION_MESSAGES = {
    "ph_out_of_range": "pH değeri fizyolojik sınırlar dışında (6.80-7.80)",
    "pco2_out_of_range": "pCO₂ değeri kabul edilebilir sınırlar dışında (10-120 mmHg)",
    "na_out_of_range": "Na⁺ değeri kabul edilebilir sınırlar dışında (110-180 mmol/L)",
    "cl_out_of_range": "Cl⁻ değeri kabul edilebilir sınırlar dışında (70-140 mmol/L)",
    "k_out_of_range": "K⁺ değeri kabul edilebilir sınırlar dışında (2-8 mmol/L)",
    "ca_out_of_range": "Ca²⁺ değeri kabul edilebilir sınırlar dışında (0.5-2.5 mmol/L)",
    "mg_out_of_range": "Mg²⁺ değeri kabul edilebilir sınırlar dışında (0.3-3 mmol/L)",
    "lactate_out_of_range": "Laktat değeri kabul edilebilir sınırlar dışında (0-25 mmol/L)",
    "albumin_gl_out_of_range": "Albümin (g/L) değeri kabul edilebilir sınırlar dışında (5-60 g/L)",
    "po4_out_of_range": "Fosfat değeri kabul edilebilir sınırlar dışında (0.3-4 mmol/L)",
    "be_mismatch": "BE mismatch: girilen BE ile hesaplanan BE arasında >2 mEq/L fark var.",
    "hco3_mismatch": "HCO₃ mismatch: girilen HCO₃ ile hesaplanan arasında >2 mEq/L fark var.",
    "sig_no_lactate": "Laktat olmadan SIG muhtemelen düşük hesaplanmıştır.",
    "sig_approximate": "Ca/Mg eksik olduğundan SIG yaklaşık değerdir.",
    "sig_unreliable": "Kritik parametreler eksik, SIG güvenilir değil.",
}

# === Validasyon Eşikleri ===
# Three-tier model: hard physiologic limits, extreme-but-valid warnings, and reference ranges (bilgilendirme)
PHYSIOLOGIC_LIMITS = {
    "ph": (PH_MIN, PH_MAX),
    "pco2": (PCO2_MIN, PCO2_MAX),
    "na": (NA_MIN, NA_MAX),
    "cl": (CL_MIN, CL_MAX),
    "k": (K_MIN, K_MAX),
    "lactate": (LACTATE_MIN, LACTATE_MAX),
}

EXTREME_THRESHOLDS = {
    # Two-sided thresholds where applicable
    "ph": {"low": 7.0, "high": 7.7},
    # Very high pCO₂ is life-threatening but possible
    "pco2": {"high": 120.0},
    "na": {"low": 120.0, "high": 170.0},
    "cl": {"low": 70.0, "high": 130.0},
    "k": {"low": 2.0, "high": 7.0},
    "lactate": {"high": 10.0},
}

REFERENCE_RANGES = {
    "ph": (PH_NORMAL_LOW, PH_NORMAL_HIGH),
    "pco2": (PCO2_NORMAL_LOW, PCO2_NORMAL_HIGH),
    "na": (135.0, 145.0),
    "cl": (98.0, 110.0),
    "k": (3.5, 5.0),
    "lactate": (0.5, 2.0),
}

# === YUMUŞAK MESAJLAR (Yargılamayan dil) ===
SOFT_MESSAGES = {
    "missing_albumin": "Albümin değeri girilmediği için hipoalbüminemi etkisi değerlendirilemedi.",
    "missing_lactate": "Laktat değeri girilmediği için laktik asidoz değerlendirmesi yapılamadı.",
    "missing_ca": "Ca²⁺ girilmediği için ileri SID analizi kısıtlı.",
    "missing_mg": "Mg²⁺ girilmediği için SIDapparent yaklaşık hesaplandı.",
    "missing_po4": "Fosfat girilmediği için SIDeffective yaklaşık hesaplandı.",
    "missing_k": "K⁺ girilmediği için SIDapparent kısıtlı hesaplandı.",
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
    "HCO3_CALCULATED": "HCO₃ hesaplandı",
}

# ============================================================
# 🧠 KLİNİK KARAR DESTEK (CDS) NOT SETİ
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
        "condition": "|SIG| ≤ 2 mmol/L",
        "note": "SIG normal aralıkta; klinik olarak anlamlı ölçülmemiş iyon birikimi saptanmadı.",
        "refs": []
    },
    "albumin_low": {
        "condition": "Albümin < 35 g/L",
        "note": "Albümin düşük; zayıf asit azalması alkaloz yönlü maskeleme etkisi yaratabilir.",
        "refs": ["Kimura et al., 2018", "Quintard et al., 2007"]
    },
    "cl_na_high": {
        "condition": "Cl⁻/Na⁺ > 0.75",
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
        "condition": "Normal BE/HCO₃ + düşük SID",
        "note": "Klasik analizde normal görünebilir; maskelenmiş güçlü iyon asidozu olasılığı.",
        "refs": ["Quintard et al., 2007"]
    },
    "albumin_low_lactate_high": {
        "condition": "Düşük albümin + yüksek laktat",
        "note": "Zayıf asit azalması (alkaloz yönlü) ve laktat artışı (asidoz yönlü) birbiriyle karşıt etkiler yaratıyor olabilir.",
        "refs": ["Szrama & Smuszkiewicz, 2016", "Fencl & Leith, 1993"]
    },
    
    # === C KATEGORİSİ: PATERN → OLASI MEKANİZMA KÜMELERİ ===
    "pattern_hyperchloremic": {
        "condition": "SID↓ + Cl⁻↑",
        "note": "Bu patern hiperkloremik/dilüsyonel asidoz mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["İzotonik salin infüzyonu", "Renal tübüler asidoz", "Diyare kaynaklı bikarbonat kaybı"],
        "refs": ["Kilic et al., 2020"]
    },
    "pattern_unmeasured_anion": {
        "condition": "Normal laktat + SIG↑",
        "note": "Bu patern ölçülmemiş anyon birikimi mekanizmalarıyla uyumlu olabilir.",
        "mechanisms": ["Ketoasidoz", "Üremik asidoz", "Toksin (metanol, etilen glikol)", "Sülfat birikimi"],
        "refs": ["Franconieri et al., 2025"]
    },
    "pattern_masked_mixed": {
        "condition": "Albümin↓ + pH normal + Laktat↑",
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
    "hco3_normal_sid_low": "HCO₃⁻ normal görünmesine rağmen SID düşük → klasik analizde metabolik asidoz gözden kaçabilirdi.",
    "normal_be_low_sid": "BE/HCO₃ normal görünse de SID düşük → klasik yaklaşım güçlü iyon asidozunu maskelerdi.",
    "albumin_masking": "Düşük albümin mevcut asidozu maskelemiş olabilir → klasik AG düzeltmesi gerekli.",
    "sid_primary": "SID değişikliği primer mekanizma olarak öne çıkıyor → klasik yaklaşımda bu ayrım yapılamaz.",
    "ag_vs_sig": "Anyon gap normal ama SIG yüksek olabilir → ölçülmemiş anyonlar AG'de görünmeyebilir.",
    "mixed_hidden": "Karşıt etkiler birbirini dengelemiş → klasik tek parametre değerlendirmesi yetersiz kalabilir.",
}

# ============================================================
# 📚 HAZIR VAKALAR (Case-Based Learning)
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
        "teaching_point": "Akut respiratuvar asidoz. HCO₃ hafif yükselmiş ama kronik kompanzasyon düzeyinde değil."
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
}

# === UI METİNLERİ ===
UI_TEXTS = {
    "app_title": "🩸 Stewart Asit-Baz Analizi",
    "app_subtitle": "Fizikokimyasal yaklaşımla kan gazı değerlendirmesi",
    "landing_description": """
Bu araç, kompleks asit-baz bozukluklarını **Stewart-Fencl sentezi** ile analiz etmek için 
geliştirilmiş bir eğitim ve klinik destek aracıdır.

**Klasik yaklaşımdan farkı:**
- Sadece pH ve HCO₃'e bakmak yerine, asit-baz dengesini etkileyen **tüm güçlü iyonları** değerlendirir
- **Maskelenmiş bozuklukları** (örn. hipoalbüminemi + asidoz) ortaya çıkarır  
- Her bileşenin **ayrı ayrı katkısını** gösterir
""",
    "disclaimer": "⚕️ Bu araç klinik karar destek sistemi değildir. Eğitim amaçlıdır. Tüm klinik kararlar uzman hekim değerlendirmesi gerektirir.",
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
# 📖 PARAMETRE TANIMLARI (Tooltip / Help için)
# ============================================================

PARAM_DEFINITIONS = {
    # === SID Tanımları ===
    "sid_simple": {
        "short": "Na − Cl farkı. Klor yükünü değerlendirmek için pratik gösterge.",
        "long": """**SID_simple (Na − Cl)**

Sodyum ile klor arasındaki farktır. Klor yükünü değerlendirmek için pratik bir göstergedir.

**Normal:** ≈ 36–40 mmol/L

**Düşükse:**
• Klor göreceli olarak yüksek
• Hiperkloremik metabolik asidoz eğilimi

**Yüksekse:**
• Klor göreceli olarak düşük
• Metabolik alkaloz eğilimi (örn. kusma, diüretik)""",
        "normal": "≈ 38 mmol/L"
    },
    
    "sid_basic": {
        "short": "Na − Cl − Laktat. Laktatın asidoz yükünü SID üzerinden yansıtır.",
        "long": """**SID_basic (Na − Cl − Lactate)**

Na–Cl farkına laktatın eklenmiş halidir. Laktatın asidoz yükünü SID üzerinden yansıtır.

**Normal:** ≈ 36–38 mmol/L

**Düşükse:**
• Laktat artışı ve/veya klor fazlalığı
• Laktik ± hiperkloremik metabolik asidoz

**Yüksekse:**
• Metabolik alkaloz yönlü durumlar""",
        "normal": "≈ 37 mmol/L"
    },
    
    "sid_full": {
        "short": "Tüm güçlü iyonlarla hesaplanan apparent SID. Stewart'ın ana değişkeni.",
        "long": """**SID_full / SIDapparent (Na+K+Ca+Mg − Cl − Lactate)**

Tüm ölçülen güçlü iyonlar kullanılarak hesaplanan teorik apparent SID. Stewart yaklaşımının ana değişkenlerinden biridir.

**Normal:** ≈ 40–44 mmol/L

**Düşükse:**
• Güçlü anyon fazlalığı veya katyon azlığı
• Primer metabolik asidoz

**Yüksekse:**
• Güçlü katyon fazlalığı veya anyon azlığı
• Primer metabolik alkaloz

⚠️ Ca²⁺/Mg²⁺ eksikse yaklaşık (approximate) kabul edilir.""",
        "normal": "≈ 40-44 mmol/L"
    },
    
    "sid_effective": {
        "short": "HCO₃ ve zayıf asitlerin etkisini içeren 'etkin' SID. SIG hesabında kullanılır.",
        "long": """**SIDeffective**

Bikarbonat ve zayıf asitlerin (albümin, fosfat) etkisini içeren "etkin" SID değeridir.

SIG hesaplamasında kullanılır:
**SIG = SIDapparent − SIDeffective**

Doğrudan referans aralığı yoktur; SIDapparent ile karşılaştırılarak yorumlanır.""",
        "normal": "SIDa ile karşılaştırılır"
    },
    
    # === Stewart Parametreleri ===
    "atot": {
        "short": "Zayıf asitlerin (albümin, fosfat) toplam etkisi.",
        "long": """**Atot (Total Weak Acids)**

Zayıf asitlerin (özellikle albümin ve fosfat) toplam etkisini temsil eder.

**Normal:** ≈ 2.5–3.0 mmol/L (albümin ~40 g/L varsayımıyla)

**Düşükse:**
• Albümin düşüklüğü
• pH alkaloz yönüne itilir
• Metabolik asidoz maskelenebilir

**Yüksekse:**
• Albümin/fosfat artışı
• Metabolik asidoz eğilimi""",
        "normal": "≈ 2.5-3.0 mmol/L"
    },
    
    "sig": {
        "short": "Ölçülmemiş anyonların (keton, toksin, sülfat vb.) varlığını gösterir.",
        "long": """**SIG (Strong Ion Gap)**

Ölçülmemiş anyonların (ketonlar, toksinler, sülfatlar vb.) varlığını gösterir.

**Formül:** SIG = SIDapparent − SIDeffective

**Normal:** ≈ −2 ile +2 mmol/L

**Yüksekse (> +2):**
• Ölçülmemiş anyon artışı
• Klasik AG normal olsa bile gizli asidoz olabilir

**Düşükse (< −2):**
• Ölçülmemiş katyonlar veya ölçüm artefaktı
• Klinik olarak nadir

⚠️ Eksik elektrolitlerde yaklaşık kabul edilir.""",
        "normal": "−2 ile +2 mmol/L"
    },
    
    "cl_na_ratio": {
        "short": "Klor yükünü sodyuma göre değerlendiren pratik oran.",
        "long": """**Cl/Na Oranı**

Klor yükünü sodyuma göre değerlendiren pratik bir orandır.

**Normal:** ≈ 0.75 – 0.80

**Yüksekse:**
• Göreceli klor fazlalığı
• Hiperkloremik metabolik asidoz lehine

**Düşükse:**
• Klor kaybı
• Metabolik alkaloz lehine""",
        "normal": "0.75-0.80"
    },
    
    # === Anyon Gap ===
    "anion_gap": {
        "short": "Klasik yaklaşımla ölçülen anyon-katyon farkı. AG = Na − (Cl + HCO₃)",
        "long": """**Anyon Gap (AG)**

Klasik yaklaşımla ölçülen anyon–katyon farkı.

**Formül:** AG = Na − (Cl + HCO₃)

**Normal:** ≈ 8–12 mmol/L

**Yüksekse:**
• Laktat, keton, toksin gibi asit yükleri
• Yüksek AG metabolik asidoz (HAGMA)

**Normal/Düşükse:**
• Asidoz yok veya hiperkloremik asidoz (NAGMA) olabilir""",
        "normal": "8-12 mmol/L"
    },
    
    "anion_gap_corrected": {
        "short": "Albümin düzeyi dikkate alınarak düzeltilmiş AG.",
        "long": """**Düzeltilmiş Anyon Gap**

Albümin düzeyi dikkate alınarak hesaplanan AG.

**Formül:** AG_düz = AG + 2.5 × (4.2 − Albümin_g/dL)

**Normal:** ≈ 12–16 mmol/L

**Yüksekse:**
• Albümin düşüklüğüne rağmen gerçek AG artışı
• Gizli yüksek AG asidozu

**Normal görünüyorsa:**
• Albümin düşüklüğü klasik AG'yi maskelemiş olabilir""",
        "normal": "12-16 mmol/L"
    },
    
    # === Bileşen Etkileri ===
    "sid_effect": {
        "short": "SID'in BE'ye katkısı. Negatif = asidoz yönünde, Pozitif = alkaloz yönünde.",
        "long": """**SID Etkisi**

SID'in Base Excess'e katkısıdır.

**Formül:** SID_effect = SID_simple − 38

**Negatif değer:** Asidoz yönünde etki (hiperkloremik)
**Pozitif değer:** Alkaloz yönünde etki (hipokloremik)""",
        "normal": "0 ± 2 mEq/L"
    },
    
    "albumin_effect": {
        "short": "Albüminin BE'ye katkısı. Düşük albümin = alkaloz yönünde etki.",
        "long": """**Albümin Etkisi**

Albüminin Base Excess'e katkısıdır.

**Formül:** Alb_effect = 2.5 × (4.2 − Albümin_g/dL)

**Pozitif değer (düşük albümin):** Alkaloz yönünde etki, asidozu maskeleyebilir
**Negatif değer (yüksek albümin):** Asidoz yönünde etki""",
        "normal": "0 ± 2 mEq/L"
    },
    
    "lactate_effect": {
        "short": "Laktatın BE'ye katkısı. Her mmol/L laktat ≈ 1 mEq/L asidoz.",
        "long": """**Laktat Etkisi**

Laktatın Base Excess'e katkısıdır.

**Formül:** Lac_effect = −Laktat

Her 1 mmol/L laktat artışı ≈ 1 mEq/L asidoz etkisi yapar.""",
        "normal": "−1 ile 0 mEq/L"
    },
    
    "residual_effect": {
        "short": "Açıklanamayan kısım. Negatif = ölçülmemiş anyonlar olabilir.",
        "long": """**Residual / Ölçülmemiş Bileşen**

BE'den bilinen bileşenlerin çıkarılmasıyla elde edilen açıklanamayan kısımdır.

**Formül:** Residual = BE − SID_effect − Alb_effect − Lac_effect

**Negatif değer:** Ölçülmemiş anyonlar (keton, toksin vb.) olabilir
**Pozitif değer:** Ölçülmemiş katyonlar (nadir)

⚠️ Bu tam SIG değildir, Fencl-derived yaklaşık değerdir.""",
        "normal": "0 ± 2 mEq/L"
    },
    
    # === Temel Kan Gazı ===
    "ph": {
        "short": "Kan asitliği. < 7.35 asidemi, > 7.45 alkalemi.",
        "long": """**pH**

Kanın asitlik derecesini gösteren logaritmik ölçek.

**Normal:** 7.35 – 7.45

**< 7.35:** Asidemi
**> 7.45:** Alkalemi""",
        "normal": "7.35-7.45"
    },
    
    "pco2": {
        "short": "Karbondioksit parsiyel basıncı. Solunumsal bileşeni yansıtır.",
        "long": """**pCO₂ (mmHg)**

Karbondioksit parsiyel basıncı. Asit-baz dengesinin solunumsal bileşenini yansıtır.

**Normal:** 35–45 mmHg

**Yüksekse:** Respiratuvar asidoz (hipoventilasyon)
**Düşükse:** Respiratuvar alkaloz (hiperventilasyon)""",
        "normal": "35-45 mmHg"
    },
    
    "hco3": {
        "short": "Bikarbonat. Metabolik bileşeni yansıtır.",
        "long": """**HCO₃⁻ (mEq/L)**

Bikarbonat konsantrasyonu. Asit-baz dengesinin metabolik bileşenini yansıtır.

**Normal:** 22–26 mEq/L

**Düşükse:** Metabolik asidoz
**Yüksekse:** Metabolik alkaloz""",
        "normal": "22-26 mEq/L"
    },
    
    "be": {
        "short": "Base Excess. Metabolik bileşenin miktarını gösterir.",
        "long": """**Base Excess (mEq/L)**

Metabolik asit-baz bozukluğunun miktarını gösteren değer.

**Normal:** −2 ile +2 mEq/L

**Negatif:** Metabolik asidoz (baz eksikliği)
**Pozitif:** Metabolik alkaloz (baz fazlalığı)""",
        "normal": "−2 ile +2 mEq/L"
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
