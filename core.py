# core.py
# Stewart Asit-Baz Analizi - Hesaplama Motoru
# Tüm hesaplamalar burada, UI bağımsız.

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
import math

from constants import (
    PH_MIN, PH_MAX, PH_NORMAL_LOW, PH_NORMAL_HIGH,
    PCO2_MIN, PCO2_MAX, PCO2_NORMAL_LOW, PCO2_NORMAL_HIGH, PCO2_NORMAL,
    HCO3_NORMAL, HCO3_MISMATCH_THRESHOLD,
    NA_MIN, NA_MAX, CL_MIN, CL_MAX, K_MIN, K_MAX,
    CA_MIN, CA_MAX, MG_MIN, MG_MAX,
    LACTATE_MIN, LACTATE_MAX, LACTATE_THRESHOLD,
    ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL,
    PO4_MIN, PO4_MAX,
    BE_MIN, BE_MAX, BE_MISMATCH_THRESHOLD,
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL, SID_THRESHOLD,
    SIG_NORMAL, SIG_THRESHOLD,
    CLINICAL_SIGNIFICANCE_THRESHOLD,
    HH_CONSTANT, HH_SOLUBILITY,
    BE_HCO3_COEFFICIENT, BE_HCO3_NORMAL, BE_PH_COEFFICIENT, BE_PH_NORMAL,
    ALBUMIN_PH_COEFFICIENT, ALBUMIN_CONSTANT,
    PO4_PH_COEFFICIENT, PO4_CONSTANT,
    ATOT_ALBUMIN_COEFFICIENT, ATOT_PO4_COEFFICIENT,
    WINTERS_HCO3_COEFFICIENT, WINTERS_CONSTANT, WINTERS_TOLERANCE,
    ALKALOSIS_PCO2_COEFFICIENT, ALKALOSIS_PCO2_CONSTANT, ALKALOSIS_TOLERANCE,
    RESP_ACIDOSIS_ACUTE_COEFFICIENT, RESP_ACIDOSIS_CHRONIC_COEFFICIENT,
    RESP_ALKALOSIS_ACUTE_COEFFICIENT, RESP_ALKALOSIS_CHRONIC_COEFFICIENT,
    COMPENSATION_TOLERANCE,
    VALIDATION_MESSAGES, FLAGS
)


class DisorderType(Enum):
    """Asit-baz bozukluk tipleri"""
    NORMAL = "normal"
    METABOLIC_ACIDOSIS_HAGMA = "metabolic_acidosis_hagma"
    METABOLIC_ACIDOSIS_NAGMA = "metabolic_acidosis_nagma"
    METABOLIC_ACIDOSIS_LACTIC = "metabolic_acidosis_lactic"
    METABOLIC_ALKALOSIS = "metabolic_alkalosis"
    METABOLIC_ALKALOSIS_HYPOALB = "metabolic_alkalosis_hypoalbuminemic"
    RESPIRATORY_ACIDOSIS_ACUTE = "respiratory_acidosis_acute"
    RESPIRATORY_ACIDOSIS_CHRONIC = "respiratory_acidosis_chronic"
    RESPIRATORY_ALKALOSIS_ACUTE = "respiratory_alkalosis_acute"
    RESPIRATORY_ALKALOSIS_CHRONIC = "respiratory_alkalosis_chronic"
    MIXED = "mixed_disorder"


@dataclass
class ValidationResult:
    """Girdi validasyon sonucu"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StewartInput:
    """Stewart analizi için girdi parametreleri"""
    # Zorunlu
    ph: float
    pco2: float
    na: float
    cl: float
    
    # Opsiyonel - kan gazı
    hco3: Optional[float] = None  # None ise hesaplanır
    be: Optional[float] = None    # None ise hesaplanır
    
    # Opsiyonel - elektrolitler
    k: Optional[float] = None
    ca: Optional[float] = None
    mg: Optional[float] = None
    lactate: Optional[float] = None
    
    # Opsiyonel - zayıf asitler
    albumin_gl: Optional[float] = None  # g/L cinsinden
    po4: Optional[float] = None
    
    # Meta
    is_be_base_deficit: bool = False  # True ise BE değeri base deficit olarak girilmiş


@dataclass
class SIDValues:
    """3 katmanlı SID değerleri"""
    sid_simple: float              # Na - Cl
    sid_simple_status: str         # "measured"
    
    sid_basic: Optional[float]     # Na - Cl - Lactate
    sid_basic_status: str          # "measured" veya "lactate_missing"
    
    sid_full: Optional[float]      # (Na + K + Ca + Mg) - (Cl + Lactate)
    sid_full_status: str           # "complete", "partial", "k_missing" vb.
    sid_full_missing: List[str]    # Eksik parametreler


@dataclass
class StewartOutput:
    """Stewart analizi çıktıları"""
    # Hesaplanan temel değerler
    hco3_calculated: float
    hco3_used: float              # Kullanılan HCO3 (manuel veya hesaplanan)
    hco3_source: str              # "calculated" veya "manual"
    
    be_calculated: float
    be_used: float                # Kullanılan BE
    be_source: str                # "calculated" veya "manual"
    
    # 3 katmanlı SID
    sid_values: SIDValues
    
    # SIDeffective ve SIG (Advanced mod için)
    sid_effective: Optional[float] = None
    sig: Optional[float] = None
    sig_reliability: str = "unknown"  # "reliable", "approximate", "underestimated", "unreliable"
    
    # Atot
    atot: Optional[float] = None
    
    # Bileşen etkileri (Quick mod - Fencl derived)
    sid_effect: float = 0.0            # SID'in BE'ye katkısı
    albumin_effect: Optional[float] = None
    lactate_effect: Optional[float] = None
    residual_effect: Optional[float] = None  # Açıklanamayan kısım
    
    # Anyon gap
    anion_gap: float = 0.0
    anion_gap_corrected: Optional[float] = None
    
    # Kompanzasyon
    expected_pco2: Optional[float] = None
    expected_hco3: Optional[float] = None
    compensation_status: str = ""
    compensation_details: str = ""
    observed_expected_diff: Optional[float] = None
    
    # Flags
    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Yorumlar
    interpretations: List[str] = field(default_factory=list)
    
    # Dominant disorder (kural tabanlı)
    dominant_disorder: Optional[str] = None
    disorder_components: List[str] = field(default_factory=list)
    
    # Eksik ve varsayılan parametreler
    missing_params: List[str] = field(default_factory=list)
    assumed_params: List[str] = field(default_factory=list)  # Artık boş kalacak


# === VALIDASYON FONKSİYONLARI ===

def validate_input(inp: StewartInput) -> ValidationResult:
    """Girdi değerlerini validate et - tüm parametreler için"""
    errors = []
    warnings = []
    
    # pH kontrolü
    if not (PH_MIN <= inp.ph <= PH_MAX):
        errors.append(VALIDATION_MESSAGES["ph_out_of_range"])
    
    # pCO2 kontrolü
    if not (PCO2_MIN <= inp.pco2 <= PCO2_MAX):
        errors.append(VALIDATION_MESSAGES["pco2_out_of_range"])
    
    # Na kontrolü
    if not (NA_MIN <= inp.na <= NA_MAX):
        errors.append(VALIDATION_MESSAGES["na_out_of_range"])
    
    # Cl kontrolü
    if not (CL_MIN <= inp.cl <= CL_MAX):
        errors.append(VALIDATION_MESSAGES["cl_out_of_range"])
    
    # K kontrolü
    if inp.k is not None and not (K_MIN <= inp.k <= K_MAX):
        errors.append(VALIDATION_MESSAGES["k_out_of_range"])
    
    # Ca kontrolü
    if inp.ca is not None and not (CA_MIN <= inp.ca <= CA_MAX):
        errors.append(VALIDATION_MESSAGES["ca_out_of_range"])
    
    # Mg kontrolü
    if inp.mg is not None and not (MG_MIN <= inp.mg <= MG_MAX):
        errors.append(VALIDATION_MESSAGES["mg_out_of_range"])
    
    # Laktat kontrolü
    if inp.lactate is not None and not (LACTATE_MIN <= inp.lactate <= LACTATE_MAX):
        errors.append(VALIDATION_MESSAGES["lactate_out_of_range"])
    
    # Albümin kontrolü (g/L)
    if inp.albumin_gl is not None and not (ALBUMIN_MIN_GL <= inp.albumin_gl <= ALBUMIN_MAX_GL):
        errors.append(VALIDATION_MESSAGES["albumin_gl_out_of_range"])
    
    # Fosfat kontrolü
    if inp.po4 is not None and not (PO4_MIN <= inp.po4 <= PO4_MAX):
        errors.append(VALIDATION_MESSAGES["po4_out_of_range"])
    
    # Eksik parametre uyarıları
    if inp.albumin_gl is None:
        warnings.append(VALIDATION_MESSAGES["missing_albumin"])
    
    if inp.lactate is None:
        warnings.append(VALIDATION_MESSAGES["missing_lactate"])
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


# === TEMEL HESAPLAMA FONKSİYONLARI ===

def calculate_hco3(ph: float, pco2: float) -> float:
    """
    Henderson-Hasselbalch denklemi ile HCO3 hesapla
    HCO3 = 0.03 × pCO2 × 10^(pH - 6.1)
    """
    hco3 = HH_SOLUBILITY * pco2 * (10 ** (ph - HH_CONSTANT))
    return round(hco3, 1)


def calculate_be(ph: float, hco3: float) -> float:
    """
    Base Excess hesapla (Van Slyke yaklaşımı)
    BE ≈ 0.93 × (HCO₃ − 24.4) + 14.8 × (pH − 7.40)
    """
    be = BE_HCO3_COEFFICIENT * (hco3 - BE_HCO3_NORMAL) + BE_PH_COEFFICIENT * (ph - BE_PH_NORMAL)
    return round(be, 1)


def check_hco3_consistency(hco3_manual: float, hco3_calculated: float) -> Tuple[bool, float]:
    """
    Manuel girilen HCO3 ile hesaplanan arasındaki tutarlılığı kontrol et
    Returns: (is_consistent, difference)
    """
    diff = abs(hco3_manual - hco3_calculated)
    return diff <= HCO3_MISMATCH_THRESHOLD, round(diff, 1)


def check_be_consistency(be_manual: float, be_calculated: float) -> Tuple[bool, float]:
    """
    Manuel girilen BE ile hesaplanan arasındaki tutarlılığı kontrol et
    Returns: (is_consistent, difference)
    """
    diff = abs(be_manual - be_calculated)
    return diff <= BE_MISMATCH_THRESHOLD, round(diff, 1)


# === SID HESAPLAMALARI (3 KATMANLI) ===

def calculate_sid_simple(na: float, cl: float) -> float:
    """
    Basit SID hesabı
    SID_simple = Na - Cl
    Normal: ~38 mEq/L
    """
    return round(na - cl, 1)


def calculate_sid_basic(na: float, cl: float, lactate: Optional[float]) -> Tuple[Optional[float], str]:
    """
    Temel SID hesabı (laktat dahil)
    SID_basic = Na - Cl - Lactate
    Normal: ~37 mEq/L
    
    Returns: (sid_basic, status)
    """
    if lactate is None:
        return None, "lactate_missing"
    
    sid_basic = na - cl - lactate
    return round(sid_basic, 1), "measured"


def calculate_sid_full(
    na: float,
    cl: float,
    k: Optional[float] = None,
    ca: Optional[float] = None,
    mg: Optional[float] = None,
    lactate: Optional[float] = None
) -> Tuple[Optional[float], str, List[str]]:
    """
    Tam SIDapparent hesabı
    SID_full = (Na + K + Ca + Mg) - (Cl + Lactate)
    Normal: ~40-44 mEq/L
    
    Returns: (sid_full, status, missing_params)
    """
    missing = []
    
    # Katyonlar
    cations = na
    if k is not None:
        cations += k
    else:
        missing.append("K⁺")
    
    if ca is not None:
        cations += ca
    else:
        missing.append("Ca²⁺")
    
    if mg is not None:
        cations += mg
    else:
        missing.append("Mg²⁺")
    
    # Anyonlar
    anions = cl
    if lactate is not None:
        anions += lactate
    else:
        missing.append("Laktat")
    
    # Status belirleme
    if len(missing) == 0:
        status = "complete"
    elif len(missing) <= 2:
        status = "partial"
    else:
        status = "incomplete"
    
    sid_full = cations - anions
    return round(sid_full, 1), status, missing


def calculate_all_sids(inp: StewartInput) -> SIDValues:
    """Tüm SID değerlerini hesapla"""
    sid_simple = calculate_sid_simple(inp.na, inp.cl)
    sid_basic, sid_basic_status = calculate_sid_basic(inp.na, inp.cl, inp.lactate)
    sid_full, sid_full_status, sid_full_missing = calculate_sid_full(
        inp.na, inp.cl, inp.k, inp.ca, inp.mg, inp.lactate
    )
    
    return SIDValues(
        sid_simple=sid_simple,
        sid_simple_status="measured",
        sid_basic=sid_basic,
        sid_basic_status=sid_basic_status,
        sid_full=sid_full,
        sid_full_status=sid_full_status,
        sid_full_missing=sid_full_missing
    )


# === SIDeffective ve SIG ===

def calculate_sid_effective(
    ph: float,
    hco3: float,
    albumin_gl: Optional[float] = None,
    po4: Optional[float] = None
) -> Tuple[float, List[str]]:
    """
    SIDeffective hesabı
    SIDe = [Alb] × (0.123 × pH - 0.631) + [PO4] × (0.309 × pH - 0.469) + [HCO3]
    
    Returns: (sid_effective, missing_params)
    """
    missing = []
    sid_e = hco3
    
    if albumin_gl is not None:
        alb_charge = albumin_gl * (ALBUMIN_PH_COEFFICIENT * ph - ALBUMIN_CONSTANT)
        sid_e += alb_charge
    else:
        missing.append("Albümin")
    
    if po4 is not None:
        po4_charge = po4 * (PO4_PH_COEFFICIENT * ph - PO4_CONSTANT)
        sid_e += po4_charge
    else:
        missing.append("Fosfat")
    
    return round(sid_e, 1), missing


def calculate_sig(sid_apparent: float, sid_effective: float) -> float:
    """
    Strong Ion Gap hesabı
    SIG = SIDapparent - SIDeffective
    
    Pozitif SIG → ölçülmemiş anyonlar mevcut (HAGMA)
    Negatif SIG → ölçülmemiş katyonlar mevcut (nadir)
    """
    return round(sid_apparent - sid_effective, 1)


def assess_sig_reliability(
    lactate: Optional[float],
    ca: Optional[float],
    mg: Optional[float],
    albumin_gl: Optional[float]
) -> Tuple[str, List[str]]:
    """
    SIG güvenilirliğini değerlendir
    
    Returns: (reliability, warnings)
    """
    warnings = []
    
    # Laktat kritik
    if lactate is None:
        warnings.append(VALIDATION_MESSAGES["sig_no_lactate"])
        return "underestimated", warnings
    
    # Albümin önemli
    if albumin_gl is None:
        return "unreliable", [VALIDATION_MESSAGES["sig_unreliable"]]
    
    # Ca/Mg eksikse yaklaşık
    if ca is None or mg is None:
        warnings.append(VALIDATION_MESSAGES["sig_approximate"])
        return "approximate", warnings
    
    return "reliable", []


# === ATOT ===

def calculate_atot(albumin_gl: Optional[float] = None, po4: Optional[float] = None) -> Optional[float]:
    """
    Zayıf asitlerin toplam konsantrasyonu (Atot)
    Atot = (0.123 × Alb) + (0.309 × PO4)
    """
    if albumin_gl is None:
        return None
    
    atot = ATOT_ALBUMIN_COEFFICIENT * albumin_gl
    
    if po4 is not None:
        atot += ATOT_PO4_COEFFICIENT * po4
    
    return round(atot, 1)


# === BİLEŞEN ETKİLERİ (Quick mod - Fencl derived) ===

def calculate_sid_effect(sid_simple: float) -> float:
    """
    SID'in metabolik etkisi
    Etki = SID - 38 (normal SID)
    Negatif → asidoz, Pozitif → alkaloz
    """
    return round(sid_simple - SID_NORMAL_SIMPLE, 1)


def calculate_albumin_effect(albumin_gdl: float) -> float:
    """
    Albüminin metabolik etkisi
    Etki = 2.5 × (4.2 - Alb)
    Düşük albümin → pozitif etki (alkaloz)
    """
    return round(2.5 * (4.2 - albumin_gdl), 1)


def calculate_lactate_effect(lactate: float) -> float:
    """
    Laktatın metabolik etkisi
    Her mmol/L laktat = 1 mEq/L asidoz
    """
    return round(-lactate, 1)


def calculate_residual_effect(
    be: float,
    sid_effect: float,
    albumin_effect: Optional[float],
    lactate_effect: Optional[float]
) -> float:
    """
    Açıklanamayan / Ölçülmemiş bileşen (Unmeasured component)
    Residual = BE - SID_effect - Alb_effect - Lactate_effect
    
    NOT: Bu tam SIG değil, hızlı mod için yaklaşık değer.
    """
    residual = be - sid_effect
    if albumin_effect is not None:
        residual -= albumin_effect
    if lactate_effect is not None:
        residual -= lactate_effect
    return round(residual, 1)


# === ANYON GAP ===

def calculate_anion_gap(na: float, cl: float, hco3: float) -> float:
    """
    Anyon Gap hesabı
    AG = Na - (Cl + HCO3)
    """
    return round(na - (cl + hco3), 1)


def calculate_corrected_anion_gap(ag: float, albumin_gdl: float) -> float:
    """
    Albümin için düzeltilmiş Anyon Gap
    AG_corrected = AG + 2.5 × (4.2 - Albumin)
    """
    correction = 2.5 * (4.2 - albumin_gdl)
    return round(ag + correction, 1)


# === KOMPANZASYON (GENİŞLETİLMİŞ) ===

def calculate_expected_pco2_metabolic_acidosis(hco3: float) -> float:
    """
    Metabolik asidoz için beklenen pCO2 (Winter's formülü)
    Expected pCO2 = 1.5 × HCO3 + 8 (± 2)
    """
    return round(WINTERS_HCO3_COEFFICIENT * hco3 + WINTERS_CONSTANT, 0)


def calculate_expected_pco2_metabolic_alkalosis(hco3: float) -> float:
    """
    Metabolik alkaloz için beklenen pCO2
    Expected pCO2 = 0.7 × HCO3 + 21 (± 2)
    """
    return round(ALKALOSIS_PCO2_COEFFICIENT * hco3 + ALKALOSIS_PCO2_CONSTANT, 0)


def calculate_expected_hco3_respiratory_acidosis(pco2: float, is_chronic: bool = False) -> float:
    """
    Respiratuvar asidoz için beklenen HCO3
    Akut: ΔHCO3 = 0.1 × ΔpCO2
    Kronik: ΔHCO3 = 0.35 × ΔpCO2
    """
    delta_pco2 = pco2 - PCO2_NORMAL
    if is_chronic:
        delta_hco3 = RESP_ACIDOSIS_CHRONIC_COEFFICIENT * delta_pco2
    else:
        delta_hco3 = RESP_ACIDOSIS_ACUTE_COEFFICIENT * delta_pco2
    return round(HCO3_NORMAL + delta_hco3, 1)


def calculate_expected_hco3_respiratory_alkalosis(pco2: float, is_chronic: bool = False) -> float:
    """
    Respiratuvar alkaloz için beklenen HCO3
    Akut: ΔHCO3 = 0.2 × ΔpCO2
    Kronik: ΔHCO3 = 0.5 × ΔpCO2
    """
    delta_pco2 = PCO2_NORMAL - pco2  # pCO2 düşük, pozitif delta istiyoruz
    if is_chronic:
        delta_hco3 = RESP_ALKALOSIS_CHRONIC_COEFFICIENT * delta_pco2
    else:
        delta_hco3 = RESP_ALKALOSIS_ACUTE_COEFFICIENT * delta_pco2
    return round(HCO3_NORMAL - delta_hco3, 1)


def assess_compensation(
    ph: float,
    pco2: float,
    hco3: float,
    be: float
) -> Tuple[Optional[float], Optional[float], str, str, Optional[float]]:
    """
    Kapsamlı kompanzasyon değerlendirmesi
    
    Returns:
        (expected_pco2, expected_hco3, status, details, observed_expected_diff)
    """
    # pH durumunu belirle
    is_acidemia = ph < PH_NORMAL_LOW
    is_alkalemia = ph > PH_NORMAL_HIGH
    
    # pCO2 durumunu belirle
    is_pco2_high = pco2 > PCO2_NORMAL_HIGH
    is_pco2_low = pco2 < PCO2_NORMAL_LOW
    
    # BE/metabolik durumu belirle
    is_metabolic_acidosis = be < -CLINICAL_SIGNIFICANCE_THRESHOLD
    is_metabolic_alkalosis = be > CLINICAL_SIGNIFICANCE_THRESHOLD
    
    # Primer bozukluğu belirle ve kompanzasyonu değerlendir
    
    # 1. Primer Metabolik Asidoz
    if is_metabolic_acidosis and (is_acidemia or ph <= PH_NORMAL_HIGH):
        expected_pco2 = calculate_expected_pco2_metabolic_acidosis(hco3)
        diff = pco2 - expected_pco2
        
        if abs(diff) <= WINTERS_TOLERANCE:
            status = "Uygun respiratuvar kompanzasyon"
            details = f"Beklenen pCO₂: {expected_pco2:.0f} ± 2 mmHg"
        elif diff < -WINTERS_TOLERANCE:
            status = "Ek respiratuvar alkaloz"
            details = f"pCO₂ beklenenden {abs(diff):.0f} mmHg düşük"
        else:
            status = "Ek respiratuvar asidoz"
            details = f"pCO₂ beklenenden {diff:.0f} mmHg yüksek"
        
        return expected_pco2, None, status, details, round(diff, 1)
    
    # 2. Primer Metabolik Alkaloz
    if is_metabolic_alkalosis and (is_alkalemia or ph >= PH_NORMAL_LOW):
        expected_pco2 = calculate_expected_pco2_metabolic_alkalosis(hco3)
        diff = pco2 - expected_pco2
        
        if abs(diff) <= ALKALOSIS_TOLERANCE:
            status = "Uygun respiratuvar kompanzasyon"
            details = f"Beklenen pCO₂: {expected_pco2:.0f} ± 2 mmHg"
        elif diff < -ALKALOSIS_TOLERANCE:
            status = "Ek respiratuvar alkaloz"
            details = f"pCO₂ beklenenden {abs(diff):.0f} mmHg düşük"
        else:
            status = "Ek respiratuvar asidoz"
            details = f"pCO₂ beklenenden {diff:.0f} mmHg yüksek"
        
        return expected_pco2, None, status, details, round(diff, 1)
    
    # 3. Primer Respiratuvar Asidoz
    if is_pco2_high and is_acidemia:
        # Akut ve kronik için ayrı hesapla
        expected_hco3_acute = calculate_expected_hco3_respiratory_acidosis(pco2, is_chronic=False)
        expected_hco3_chronic = calculate_expected_hco3_respiratory_acidosis(pco2, is_chronic=True)
        
        if hco3 <= expected_hco3_acute + COMPENSATION_TOLERANCE:
            status = "Akut respiratuvar asidoz"
            details = f"Beklenen HCO₃⁻ (akut): {expected_hco3_acute:.1f} mEq/L"
            return None, expected_hco3_acute, status, details, round(hco3 - expected_hco3_acute, 1)
        elif hco3 >= expected_hco3_chronic - COMPENSATION_TOLERANCE:
            status = "Kronik respiratuvar asidoz"
            details = f"Beklenen HCO₃⁻ (kronik): {expected_hco3_chronic:.1f} mEq/L"
            return None, expected_hco3_chronic, status, details, round(hco3 - expected_hco3_chronic, 1)
        else:
            status = "Subakut veya miks respiratuvar asidoz"
            details = f"HCO₃⁻ akut ({expected_hco3_acute:.1f}) ve kronik ({expected_hco3_chronic:.1f}) beklenti arasında"
            return None, expected_hco3_acute, status, details, None
    
    # 4. Primer Respiratuvar Alkaloz
    if is_pco2_low and is_alkalemia:
        expected_hco3_acute = calculate_expected_hco3_respiratory_alkalosis(pco2, is_chronic=False)
        expected_hco3_chronic = calculate_expected_hco3_respiratory_alkalosis(pco2, is_chronic=True)
        
        if hco3 >= expected_hco3_acute - COMPENSATION_TOLERANCE:
            status = "Akut respiratuvar alkaloz"
            details = f"Beklenen HCO₃⁻ (akut): {expected_hco3_acute:.1f} mEq/L"
            return None, expected_hco3_acute, status, details, round(hco3 - expected_hco3_acute, 1)
        elif hco3 <= expected_hco3_chronic + COMPENSATION_TOLERANCE:
            status = "Kronik respiratuvar alkaloz"
            details = f"Beklenen HCO₃⁻ (kronik): {expected_hco3_chronic:.1f} mEq/L"
            return None, expected_hco3_chronic, status, details, round(hco3 - expected_hco3_chronic, 1)
        else:
            status = "Subakut veya miks respiratuvar alkaloz"
            details = f"HCO₃⁻ akut ({expected_hco3_acute:.1f}) ve kronik ({expected_hco3_chronic:.1f}) beklenti arasında"
            return None, expected_hco3_acute, status, details, None
    
    # Normal veya miks
    return None, None, "Belirgin primer bozukluk saptanmadı", "", None


# === YORUMLAMA ===

def interpret_ph(ph: float) -> Tuple[str, str]:
    """pH yorumla -> (yorum, seviye: normal/warning/critical)"""
    if ph < PH_NORMAL_LOW:
        return "Asidemi", "critical"
    elif ph > PH_NORMAL_HIGH:
        return "Alkalemi", "critical"
    return "Normal", "normal"


def interpret_pco2(pco2: float) -> Tuple[str, str]:
    """pCO2 yorumla"""
    if pco2 > PCO2_NORMAL_HIGH:
        return "Respiratuvar asidoz", "warning"
    elif pco2 < PCO2_NORMAL_LOW:
        return "Respiratuvar alkaloz", "warning"
    return "Normal", "normal"


def interpret_sid_effect(sid_effect: float) -> Tuple[str, str]:
    """SID etkisini yorumla"""
    if sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "SID asidozu (NAGMA)", "warning"
    elif sid_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "SID alkalozu", "info"
    return "Normal", "normal"


def interpret_albumin_effect(alb_effect: float) -> Tuple[str, str]:
    """Albümin etkisini yorumla"""
    if alb_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "Hipoalbüminemik alkaloz", "info"
    elif alb_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "Hiperalbüminemik asidoz", "warning"
    return "Normal", "normal"


def interpret_lactate(lactate: float) -> Tuple[str, str]:
    """Laktat yorumla"""
    if lactate > LACTATE_THRESHOLD:
        return "Laktik asidoz", "warning"
    return "Normal", "normal"


def interpret_sig(sig: float) -> Tuple[str, str]:
    """
    SIG yorumla
    SIG = SIDa - SIDe
    Pozitif → ölçülmemiş anyonlar
    """
    if sig > SIG_THRESHOLD:
        return "Ölçülmemiş anyonlar mevcut (HAGMA)", "warning"
    elif sig < -SIG_THRESHOLD:
        return "Ölçülmemiş katyonlar mevcut (nadir)", "info"
    return "Normal", "normal"


def interpret_residual(residual: float) -> Tuple[str, str]:
    """
    Residual/Unmeasured component yorumla (Quick mod için)
    """
    if residual < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "Açıklanamayan asidoz (ölçülmemiş anyonlar?)", "warning"
    elif residual > CLINICAL_SIGNIFICANCE_THRESHOLD:
        return "Açıklanamayan alkaloz", "info"
    return "Normal", "normal"


# === DOMINANT DISORDER (KURAL TABANLI) ===

def determine_dominant_disorder(
    ph: float,
    pco2: float,
    be: float,
    sid_effect: float,
    albumin_effect: Optional[float],
    lactate: Optional[float],
    residual_effect: Optional[float],
    sig: Optional[float]
) -> Tuple[str, List[str]]:
    """
    Kural tabanlı dominant bozukluk belirleme
    
    Returns: (dominant_disorder, component_list)
    """
    components = []
    
    # pH durumu
    is_acidemia = ph < PH_NORMAL_LOW
    is_alkalemia = ph > PH_NORMAL_HIGH
    
    # pCO2 durumu
    is_resp_acidosis = pco2 > PCO2_NORMAL_HIGH
    is_resp_alkalosis = pco2 < PCO2_NORMAL_LOW
    
    # Metabolik durumlar
    is_met_acidosis = be < -CLINICAL_SIGNIFICANCE_THRESHOLD
    is_met_alkalosis = be > CLINICAL_SIGNIFICANCE_THRESHOLD
    
    # Bileşenler
    has_sid_acidosis = sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD
    has_sid_alkalosis = sid_effect > CLINICAL_SIGNIFICANCE_THRESHOLD
    has_alb_alkalosis = albumin_effect is not None and albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD
    has_lactic_acidosis = lactate is not None and lactate > LACTATE_THRESHOLD
    has_unmeasured_acidosis = (residual_effect is not None and residual_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD) or \
                              (sig is not None and sig > SIG_THRESHOLD)
    
    # Respiratuvar bileşenler
    if is_resp_acidosis:
        components.append("respiratory_acidosis")
    if is_resp_alkalosis:
        components.append("respiratory_alkalosis")
    
    # Metabolik bileşenler
    if has_sid_acidosis:
        components.append("hyperchloremic_acidosis")
    if has_sid_alkalosis:
        components.append("hypochloremic_alkalosis")
    if has_alb_alkalosis:
        components.append("hypoalbuminemic_alkalosis")
    if has_lactic_acidosis:
        components.append("lactic_acidosis")
    if has_unmeasured_acidosis:
        components.append("hagma")
    
    # Dominant disorder belirleme
    if len(components) == 0:
        return "normal", []
    elif len(components) == 1:
        return components[0], components
    elif len(components) == 2:
        return "mixed_disorder", components
    else:
        return "triple_disorder", components


# === ANA ANALİZ FONKSİYONU ===

def analyze_stewart(inp: StewartInput, mode: str = "quick") -> Tuple[StewartOutput, ValidationResult]:
    """
    Ana Stewart analizi fonksiyonu
    
    Args:
        inp: StewartInput objesi
        mode: "quick" veya "advanced"
    
    Returns:
        Tuple[StewartOutput, ValidationResult]
    """
    # Validasyon
    validation = validate_input(inp)
    if not validation.is_valid:
        # Boş output dön
        empty_sid = SIDValues(0, "", None, "", None, "", [])
        return StewartOutput(
            hco3_calculated=0, hco3_used=0, hco3_source="",
            be_calculated=0, be_used=0, be_source="",
            sid_values=empty_sid,
            flags=["VALIDATION_FAILED"]
        ), validation
    
    # HCO3 hesapla
    hco3_calculated = calculate_hco3(inp.ph, inp.pco2)
    
    # HCO3 seç ve tutarlılık kontrolü
    flags = []
    warnings = validation.warnings.copy()
    
    if inp.hco3 is not None:
        hco3_used = inp.hco3
        hco3_source = "manual"
        is_consistent, hco3_diff = check_hco3_consistency(inp.hco3, hco3_calculated)
        if not is_consistent:
            warnings.append(f"{VALIDATION_MESSAGES['hco3_mismatch']} (Fark: {hco3_diff} mEq/L)")
            flags.append("HCO3_MISMATCH")
    else:
        hco3_used = hco3_calculated
        hco3_source = "calculated"
        flags.append("HCO3_CALCULATED")
    
    # BE hesapla
    be_calculated = calculate_be(inp.ph, hco3_used)
    
    # BE seç ve tutarlılık kontrolü
    if inp.be is not None:
        be_input = -inp.be if inp.is_be_base_deficit else inp.be
        be_used = be_input
        be_source = "manual"
        is_consistent, be_diff = check_be_consistency(be_input, be_calculated)
        if not is_consistent:
            warnings.append(f"{VALIDATION_MESSAGES['be_mismatch']} (Fark: {be_diff} mEq/L)")
            flags.append("BE_MISMATCH")
    else:
        be_used = be_calculated
        be_source = "calculated"
        flags.append("BE_CALCULATED")
    
    # 3 katmanlı SID hesapla
    sid_values = calculate_all_sids(inp)
    
    # Albümin g/dL'ye çevir (varsa)
    albumin_gdl = inp.albumin_gl / 10 if inp.albumin_gl is not None else None
    
    # Bileşen etkileri (quick mod)
    sid_effect = calculate_sid_effect(sid_values.sid_simple)
    albumin_effect = calculate_albumin_effect(albumin_gdl) if albumin_gdl is not None else None
    lactate_effect = calculate_lactate_effect(inp.lactate) if inp.lactate is not None else None
    residual_effect = calculate_residual_effect(be_used, sid_effect, albumin_effect, lactate_effect)
    
    # Anyon gap
    ag = calculate_anion_gap(inp.na, inp.cl, hco3_used)
    ag_corrected = calculate_corrected_anion_gap(ag, albumin_gdl) if albumin_gdl is not None else None
    
    # SIDeffective ve SIG (advanced mod için)
    sid_effective = None
    sig = None
    sig_reliability = "unknown"
    sig_warnings = []
    atot = None
    
    if mode == "advanced":
        sid_effective, side_missing = calculate_sid_effective(inp.ph, hco3_used, inp.albumin_gl, inp.po4)
        
        if sid_values.sid_full is not None:
            sig = calculate_sig(sid_values.sid_full, sid_effective)
            sig_reliability, sig_warnings = assess_sig_reliability(
                inp.lactate, inp.ca, inp.mg, inp.albumin_gl
            )
            warnings.extend(sig_warnings)
            
            if sig_reliability == "approximate":
                flags.append("SIG_APPROXIMATE")
            elif sig_reliability == "underestimated":
                flags.append("SIG_UNDERESTIMATED")
            elif sig_reliability == "unreliable":
                flags.append("SIG_UNRELIABLE")
        
        atot = calculate_atot(inp.albumin_gl, inp.po4)
    
    # Kompanzasyon
    expected_pco2, expected_hco3, comp_status, comp_details, obs_exp_diff = assess_compensation(
        inp.ph, inp.pco2, hco3_used, be_used
    )
    
    # Yorumlar
    interpretations = []
    
    # pH yorumu
    ph_interp, _ = interpret_ph(inp.ph)
    if ph_interp != "Normal":
        interpretations.append(f"pH: {ph_interp}")
    
    # pCO2 yorumu
    pco2_interp, _ = interpret_pco2(inp.pco2)
    if pco2_interp != "Normal":
        interpretations.append(f"pCO₂: {pco2_interp}")
    
    if mode == "quick":
        # SID etkisi
        sid_interp, _ = interpret_sid_effect(sid_effect)
        if sid_interp != "Normal":
            interpretations.append(f"{abs(sid_effect):.1f} mEq/L {sid_interp}")
        
        # Albümin etkisi
        if albumin_effect is not None:
            alb_interp, _ = interpret_albumin_effect(albumin_effect)
            if alb_interp != "Normal":
                interpretations.append(f"{abs(albumin_effect):.1f} mEq/L {alb_interp}")
        
        # Laktat
        if inp.lactate is not None and inp.lactate > LACTATE_THRESHOLD:
            interpretations.append(f"{inp.lactate:.1f} mEq/L Laktik asidoz")
        
        # Residual
        if residual_effect is not None:
            res_interp, _ = interpret_residual(residual_effect)
            if res_interp != "Normal":
                interpretations.append(f"{abs(residual_effect):.1f} mEq/L {res_interp}")
    
    else:  # advanced
        # SIG yorumu
        if sig is not None:
            sig_interp, _ = interpret_sig(sig)
            if sig_interp != "Normal":
                interpretations.append(f"SIG: {sig:.1f} mEq/L - {sig_interp}")
        
        # SIDa yorumu
        if sid_values.sid_full is not None:
            if sid_values.sid_full < SID_NORMAL_FULL - SID_THRESHOLD:
                interpretations.append(f"SIDa düşük ({sid_values.sid_full:.1f}) → Metabolik asidoz eğilimi")
            elif sid_values.sid_full > SID_NORMAL_FULL + SID_THRESHOLD:
                interpretations.append(f"SIDa yüksek ({sid_values.sid_full:.1f}) → Metabolik alkaloz eğilimi")
    
    # Eksik parametreler
    missing_params = []
    if inp.albumin_gl is None:
        missing_params.append("Albümin")
    if inp.lactate is None:
        missing_params.append("Laktat")
    if mode == "advanced":
        missing_params.extend(sid_values.sid_full_missing)
    
    if missing_params:
        flags.append("INCOMPLETE_DATA")
    
    # Dominant disorder
    dominant, disorder_components = determine_dominant_disorder(
        inp.ph, inp.pco2, be_used, sid_effect,
        albumin_effect, inp.lactate, residual_effect, sig
    )
    
    # Output oluştur
    output = StewartOutput(
        hco3_calculated=hco3_calculated,
        hco3_used=hco3_used,
        hco3_source=hco3_source,
        be_calculated=be_calculated,
        be_used=be_used,
        be_source=be_source,
        sid_values=sid_values,
        sid_effective=sid_effective,
        sig=sig,
        sig_reliability=sig_reliability,
        atot=atot,
        sid_effect=sid_effect,
        albumin_effect=albumin_effect,
        lactate_effect=lactate_effect,
        residual_effect=residual_effect,
        anion_gap=ag,
        anion_gap_corrected=ag_corrected,
        expected_pco2=expected_pco2,
        expected_hco3=expected_hco3,
        compensation_status=comp_status,
        compensation_details=comp_details,
        observed_expected_diff=obs_exp_diff,
        flags=flags,
        warnings=warnings,
        interpretations=interpretations,
        dominant_disorder=dominant,
        disorder_components=disorder_components,
        missing_params=missing_params,
        assumed_params=[]  # Artık varsayım yok
    )
    
    return output, validation


# === CSV EXPORT/IMPORT ===

def output_to_dict(inp: StewartInput, out: StewartOutput) -> Dict:
    """Çıktıyı dictionary'ye çevir (CSV export için)"""
    return {
        # Input
        "ph": inp.ph,
        "pco2": inp.pco2,
        "na": inp.na,
        "cl": inp.cl,
        "k": inp.k,
        "ca": inp.ca,
        "mg": inp.mg,
        "lactate": inp.lactate,
        "albumin_gl": inp.albumin_gl,
        "po4": inp.po4,
        "be_input": inp.be,
        "hco3_input": inp.hco3,
        
        # Output - temel
        "hco3_calculated": out.hco3_calculated,
        "hco3_used": out.hco3_used,
        "hco3_source": out.hco3_source,
        "be_calculated": out.be_calculated,
        "be_used": out.be_used,
        "be_source": out.be_source,
        
        # SID değerleri
        "sid_simple": out.sid_values.sid_simple,
        "sid_basic": out.sid_values.sid_basic,
        "sid_full": out.sid_values.sid_full,
        "sid_full_status": out.sid_values.sid_full_status,
        
        # SIG ve diğerleri
        "sid_effective": out.sid_effective,
        "sig": out.sig,
        "sig_reliability": out.sig_reliability,
        "atot": out.atot,
        
        # Bileşen etkileri
        "sid_effect": out.sid_effect,
        "albumin_effect": out.albumin_effect,
        "lactate_effect": out.lactate_effect,
        "residual_effect": out.residual_effect,
        
        # AG
        "anion_gap": out.anion_gap,
        "anion_gap_corrected": out.anion_gap_corrected,
        
        # Kompanzasyon
        "expected_pco2": out.expected_pco2,
        "expected_hco3": out.expected_hco3,
        "compensation_status": out.compensation_status,
        "observed_expected_diff": out.observed_expected_diff,
        
        # Disorder
        "dominant_disorder": out.dominant_disorder,
        "disorder_components": ",".join(out.disorder_components),
        
        # Meta
        "flags": ",".join(out.flags),
        "warnings": "|".join(out.warnings),
        "missing_params": ",".join(out.missing_params),
        "assumed_params": ",".join(out.assumed_params),
        "interpretations": " | ".join(out.interpretations),
    }


def dict_to_input(d: Dict) -> StewartInput:
    """Dictionary'den input oluştur (CSV import için)"""
    def safe_float(val):
        if val is None or val == "" or (isinstance(val, float) and math.isnan(val)):
            return None
        return float(val)
    
    return StewartInput(
        ph=float(d.get("ph", 7.4)),
        pco2=float(d.get("pco2", 40)),
        na=float(d.get("na", 140)),
        cl=float(d.get("cl", 100)),
        hco3=safe_float(d.get("hco3") or d.get("hco3_input")),
        be=safe_float(d.get("be") or d.get("be_input")),
        k=safe_float(d.get("k")),
        ca=safe_float(d.get("ca")),
        mg=safe_float(d.get("mg")),
        lactate=safe_float(d.get("lactate")),
        albumin_gl=safe_float(d.get("albumin_gl")),
        po4=safe_float(d.get("po4")),
    )
