# core.py
# Stewart Asit-Baz Analizi - Hesaplama Motoru
# v3.0 - CDS Entegrasyonu, Contribution Breakdown, Headline Generation

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import math

from constants import (
    PH_MIN, PH_MAX, PH_NORMAL_LOW, PH_NORMAL_HIGH,
    PCO2_MIN, PCO2_MAX, PCO2_NORMAL_LOW, PCO2_NORMAL_HIGH, PCO2_NORMAL,
    HCO3_NORMAL, HCO3_MISMATCH_THRESHOLD,
    NA_MIN, NA_MAX, CL_MIN, CL_MAX, K_MIN, K_MAX,
    CA_MIN, CA_MAX, MG_MIN, MG_MAX,
    LACTATE_MIN, LACTATE_MAX, LACTATE_THRESHOLD,
    ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, ALBUMIN_LOW_GL,
    PO4_MIN, PO4_MAX,
    BE_MIN, BE_MAX, BE_MISMATCH_THRESHOLD,
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL,
    SID_LOW_THRESHOLD, SID_HIGH_THRESHOLD, SID_THRESHOLD,
    SIG_NORMAL, SIG_THRESHOLD, SIG_HIGH, SIG_LOW,
    CL_NA_RATIO_THRESHOLD,
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
    VALIDATION_MESSAGES, SOFT_MESSAGES, FLAGS,
    CDS_NOTES, CLASSIC_COMPARISON
)
from validation import validate_input_dict, validate_csv_row
from logger import log_calculation_warning, log_analysis_error, log_batch_progress


# === DATA CLASSES ===

@dataclass
class ValidationResult:
    """Girdi validasyon sonucu"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StewartInput:
    """Stewart analizi için girdi parametreleri"""
    ph: float
    pco2: float
    na: float
    cl: float
    hco3: Optional[float] = None
    be: Optional[float] = None
    k: Optional[float] = None
    ca: Optional[float] = None
    mg: Optional[float] = None
    lactate: Optional[float] = None
    albumin_gl: Optional[float] = None
    po4: Optional[float] = None
    is_be_base_deficit: bool = False


@dataclass
class SIDValues:
    """3 katmanlı SID değerleri"""
    sid_simple: float
    sid_simple_status: str
    sid_basic: Optional[float]
    sid_basic_status: str
    sid_full: Optional[float]
    sid_full_status: str
    sid_full_missing: List[str]


@dataclass
class ContributionBreakdown:
    """pH'a etki eden kuvvetlerin ayrıştırılması"""
    # Asidoz yönüne itenler (negatif değerler)
    acidosis_contributors: List[Tuple[str, float, str]]  # (isim, değer, açıklama)
    
    # Alkaloz yönüne itenler (pozitif değerler)
    alkalosis_contributors: List[Tuple[str, float, str]]
    
    # Respiratuvar etki
    respiratory_effect: Tuple[str, float, str]  # (yön, değer, açıklama)
    
    # Net metabolik etki
    net_metabolic: float
    
    # Özet
    summary: str


@dataclass
class MechanismContribution:
    """Bir mekanizmanın BE'ye katkısı"""
    name: str                    # Mekanizma adı (non-diagnostic)
    identifier: str              # Tekil kimlik ("sid", "lactate", "albumin", "unmeasured")
    effect_meq: float           # mEq/L olarak etki
    contribution_percent: float  # BE'ye yüzde katkı
    level: str                  # "dominant", "significant", "contributing", "minimal"
    direction: str              # "acidosis" veya "alkalosis"
    description: str            # Açıklama


@dataclass
class MechanismAnalysis:
    """Contribution-based mekanizma analizi"""
    total_metabolic_effect: float  # Total BE
    
    # Ranked mechanisms by contribution
    dominant_mechanism: Optional[MechanismContribution] = None
    significant_mechanisms: List[MechanismContribution] = field(default_factory=list)
    contributing_mechanisms: List[MechanismContribution] = field(default_factory=list)
    
    # All mechanisms for detailed view
    all_mechanisms: List[MechanismContribution] = field(default_factory=list)
    
    # Pattern description (non-diagnostic)
    pattern_description: str = ""
    
    # Respiratory status
    respiratory_status: str = ""
    respiratory_details: str = ""


@dataclass
class DominanceResult:
    """Tekil kaynak: metabolik dominans sonucu"""
    total_metabolic_effect: float
    all_mechanisms: List[MechanismContribution]
    dominant: Optional[MechanismContribution]
    significant: List[MechanismContribution]
    contributing: List[MechanismContribution]
    pattern_flags: List[str] = field(default_factory=list)


@dataclass
class Headline:
    """Primer sonuç satırı - REFACTORED for mechanism-based output"""
    dominant_mechanism: str           # Dominant metabolik mekanizma
    significant_mechanisms: List[str] = field(default_factory=list)  # Anlamlı katkıda bulunanlar
    contributing_mechanisms: List[str] = field(default_factory=list) # Katkıda bulunanlar
    respiratory_status: str = ""      # Solunumsal durum
    pattern_note: str = ""            # Patern notu (non-diagnostic)
    confidence: str = "high"          # high, medium, low


@dataclass
class ClassicComparison:
    """Klasik yaklaşıma göre fark analizi"""
    differences: List[str]  # Tespit edilen farklar
    missed_by_classic: List[str]  # Klasik yaklaşımda kaçırılabilecekler
    stewart_advantage: str  # Stewart'ın avantajı


@dataclass 
class CDSNote:
    """Klinik karar destek notu"""
    category: str  # A, B, C
    condition: str
    note: str
    mechanisms: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class StewartOutput:
    """Stewart analizi çıktıları"""
    # Temel değerler
    hco3_calculated: float
    hco3_used: float
    hco3_source: str
    be_calculated: float
    be_used: float
    be_source: str
    
    # SID
    sid_values: SIDValues
    sid_effective: Optional[float] = None
    sig: Optional[float] = None
    sig_reliability: str = "unknown"
    sig_interpretation: str = ""  # Kategorik yorum
    
    # Atot
    atot: Optional[float] = None
    
    # Cl/Na oranı
    cl_na_ratio: float = 0.0
    
    # Bileşen etkileri
    sid_effect: float = 0.0
    albumin_effect: Optional[float] = None
    lactate_effect: Optional[float] = None
    residual_effect: Optional[float] = None
    respiratory_effect: float = 0.0  # pCO2'nin BE'ye etkisi (yaklaşık)
    
    # Anyon gap
    anion_gap: float = 0.0
    anion_gap_corrected: Optional[float] = None
    
    # Kompanzasyon
    expected_pco2: Optional[float] = None
    expected_hco3: Optional[float] = None
    compensation_status: str = ""
    compensation_details: str = ""
    observed_expected_diff: Optional[float] = None
    
    # YENİ: Contribution Breakdown
    contribution: Optional[ContributionBreakdown] = None
    
    # YENİ: Mechanism Analysis (contribution-based)
    mechanism_analysis: Optional[MechanismAnalysis] = None
    
    # YENİ: Headline (refactored)
    headline: Optional[Headline] = None
    
    # YENİ: Klasik karşılaştırma
    classic_comparison: Optional[ClassicComparison] = None
    
    # YENİ: CDS Notları
    cds_notes: List[CDSNote] = field(default_factory=list)
    
    # Flags ve yorumlar
    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    soft_warnings: List[str] = field(default_factory=list)  # Yumuşak uyarılar
    interpretations: List[str] = field(default_factory=list)
    
    # Dominant disorder
    dominant_disorder: Optional[str] = None
    disorder_components: List[str] = field(default_factory=list)
    
    # Eksik parametreler
    missing_params: List[str] = field(default_factory=list)
    assumed_params: List[str] = field(default_factory=list)


# === VALİDASYON ===

def validate_input(inp: StewartInput) -> ValidationResult:
    """Girdi validasyonu"""
    errors = []
    warnings = []
    
    if not (PH_MIN <= inp.ph <= PH_MAX):
        errors.append(VALIDATION_MESSAGES["ph_out_of_range"])
    if not (PCO2_MIN <= inp.pco2 <= PCO2_MAX):
        errors.append(VALIDATION_MESSAGES["pco2_out_of_range"])
    if not (NA_MIN <= inp.na <= NA_MAX):
        errors.append(VALIDATION_MESSAGES["na_out_of_range"])
    if not (CL_MIN <= inp.cl <= CL_MAX):
        errors.append(VALIDATION_MESSAGES["cl_out_of_range"])
    if inp.k is not None and not (K_MIN <= inp.k <= K_MAX):
        errors.append(VALIDATION_MESSAGES["k_out_of_range"])
    if inp.ca is not None and not (CA_MIN <= inp.ca <= CA_MAX):
        errors.append(VALIDATION_MESSAGES["ca_out_of_range"])
    if inp.mg is not None and not (MG_MIN <= inp.mg <= MG_MAX):
        errors.append(VALIDATION_MESSAGES["mg_out_of_range"])
    if inp.lactate is not None and not (LACTATE_MIN <= inp.lactate <= LACTATE_MAX):
        errors.append(VALIDATION_MESSAGES["lactate_out_of_range"])
    if inp.albumin_gl is not None and not (ALBUMIN_MIN_GL <= inp.albumin_gl <= ALBUMIN_MAX_GL):
        errors.append(VALIDATION_MESSAGES["albumin_gl_out_of_range"])
    if inp.po4 is not None and not (PO4_MIN <= inp.po4 <= PO4_MAX):
        errors.append(VALIDATION_MESSAGES["po4_out_of_range"])
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)


# === TEMEL HESAPLAMALAR ===

def calculate_hco3(ph: float, pco2: float) -> float:
    """Henderson-Hasselbalch ile HCO3"""
    return round(HH_SOLUBILITY * pco2 * (10 ** (ph - HH_CONSTANT)), 1)


def calculate_be(ph: float, hco3: float) -> float:
    """Van Slyke yaklaşımı ile BE"""
    return round(BE_HCO3_COEFFICIENT * (hco3 - BE_HCO3_NORMAL) + BE_PH_COEFFICIENT * (ph - BE_PH_NORMAL), 1)


def check_hco3_consistency(hco3_manual: float, hco3_calc: float) -> Tuple[bool, float]:
    diff = abs(hco3_manual - hco3_calc)
    return diff <= HCO3_MISMATCH_THRESHOLD, round(diff, 1)


def check_be_consistency(be_manual: float, be_calc: float) -> Tuple[bool, float]:
    diff = abs(be_manual - be_calc)
    return diff <= BE_MISMATCH_THRESHOLD, round(diff, 1)


# === SID HESAPLAMALARI ===

def calculate_sid_simple(na: float, cl: float) -> float:
    return round(na - cl, 1)


def calculate_sid_basic(na: float, cl: float, lactate: Optional[float]) -> Tuple[Optional[float], str]:
    if lactate is None:
        return None, "lactate_missing"
    return round(na - cl - lactate, 1), "measured"


def calculate_sid_full(na: float, cl: float, k: Optional[float], ca: Optional[float], 
                       mg: Optional[float], lactate: Optional[float]) -> Tuple[Optional[float], str, List[str]]:
    missing = []
    cations = na
    if k is not None: cations += k
    else: missing.append("K⁺")
    if ca is not None: cations += ca
    else: missing.append("Ca²⁺")
    if mg is not None: cations += mg
    else: missing.append("Mg²⁺")
    
    anions = cl
    if lactate is not None: anions += lactate
    else: missing.append("Laktat")
    
    status = "complete" if len(missing) == 0 else ("partial" if len(missing) <= 2 else "incomplete")
    return round(cations - anions, 1), status, missing


def calculate_all_sids(inp: StewartInput) -> SIDValues:
    sid_simple = calculate_sid_simple(inp.na, inp.cl)
    sid_basic, sid_basic_status = calculate_sid_basic(inp.na, inp.cl, inp.lactate)
    sid_full, sid_full_status, sid_full_missing = calculate_sid_full(
        inp.na, inp.cl, inp.k, inp.ca, inp.mg, inp.lactate)
    return SIDValues(sid_simple, "measured", sid_basic, sid_basic_status, 
                     sid_full, sid_full_status, sid_full_missing)


def calculate_sid_effective(ph: float, hco3: float, albumin_gl: Optional[float], 
                           po4: Optional[float]) -> Tuple[float, List[str]]:
    missing = []
    sid_e = hco3
    if albumin_gl is not None:
        sid_e += albumin_gl * (ALBUMIN_PH_COEFFICIENT * ph - ALBUMIN_CONSTANT)
    else:
        missing.append("Albümin")
    if po4 is not None:
        sid_e += po4 * (PO4_PH_COEFFICIENT * ph - PO4_CONSTANT)
    else:
        missing.append("Fosfat")
    return round(sid_e, 1), missing


def calculate_sig(sid_apparent: float, sid_effective: float) -> float:
    return round(sid_apparent - sid_effective, 1)


def assess_sig_reliability(lactate: Optional[float], ca: Optional[float], 
                          mg: Optional[float], albumin_gl: Optional[float]) -> Tuple[str, List[str]]:
    warnings = []
    if lactate is None:
        warnings.append(VALIDATION_MESSAGES["sig_no_lactate"])
        return "underestimated", warnings
    if albumin_gl is None:
        return "unreliable", [VALIDATION_MESSAGES["sig_unreliable"]]
    if ca is None or mg is None:
        warnings.append(VALIDATION_MESSAGES["sig_approximate"])
        return "approximate", warnings
    return "reliable", []


def interpret_sig_categorical(sig: Optional[float]) -> str:
    """SIG kategorik yorum"""
    if sig is None:
        return "Hesaplanamadı"
    if sig > SIG_HIGH:
        return "Ölçülmemiş anyonlar mevcut (unmeasured anions likely)"
    elif sig < SIG_LOW:
        return "Ölçülmemiş katyonlar / artefakt (nadir)"
    else:
        return "Normal / klinik olarak önemsiz"


# === BİLEŞEN ETKİLERİ ===

def calculate_sid_effect(sid_simple: float) -> float:
    return round(sid_simple - SID_NORMAL_SIMPLE, 1)


def calculate_albumin_effect(albumin_gdl: float) -> float:
    return round(2.5 * (4.2 - albumin_gdl), 1)


def calculate_lactate_effect(lactate: float) -> float:
    return round(-lactate, 1)


def calculate_respiratory_effect(pco2: float) -> float:
    """pCO2'nin yaklaşık BE etkisi"""
    # pCO2 yüksekse asidoz yönünde, düşükse alkaloz yönünde
    delta_pco2 = pco2 - PCO2_NORMAL
    # Her 10 mmHg değişim için yaklaşık ±1-2 mEq/L etki
    return round(-0.1 * delta_pco2, 1)


def calculate_residual_effect(be: float, sid_effect: float, albumin_effect: Optional[float],
                             lactate_effect: Optional[float]) -> float:
    residual = be - sid_effect
    if albumin_effect is not None:
        residual -= albumin_effect
    if lactate_effect is not None:
        residual -= lactate_effect
    return round(residual, 1)


def interpret_sid_direction(sid_value: float, sid_type: str = "simple") -> str:
    """
    SID değeri için yön yorumu döndür.
    Non-diagnostic, physiology-focused language.
    """
    if sid_type == "simple":
        normal = SID_NORMAL_SIMPLE
    elif sid_type == "basic":
        normal = SID_NORMAL_BASIC
    else:
        normal = SID_NORMAL_FULL
    
    diff = sid_value - normal
    
    if diff < -4:
        return "Güçlü iyon aracılı metabolik asidoz yönünde (belirgin)"
    elif diff < -2:
        return "Güçlü iyon aracılı metabolik asidoz yönünde (hafif)"
    elif diff > 4:
        return "Güçlü iyon aracılı metabolik alkaloz yönünde (belirgin)"
    elif diff > 2:
        return "Güçlü iyon aracılı metabolik alkaloz yönünde (hafif)"
    else:
        return "Normal aralıkta (nötr)"


# === ANYON GAP ===

def calculate_anion_gap(na: float, cl: float, hco3: float) -> float:
    return round(na - (cl + hco3), 1)


def calculate_corrected_anion_gap(ag: float, albumin_gdl: float) -> float:
    return round(ag + 2.5 * (4.2 - albumin_gdl), 1)


# === KOMPANZASYON ===

def calculate_expected_pco2_metabolic_acidosis(hco3: float) -> float:
    return round(WINTERS_HCO3_COEFFICIENT * hco3 + WINTERS_CONSTANT, 0)


def calculate_expected_pco2_metabolic_alkalosis(hco3: float) -> float:
    return round(ALKALOSIS_PCO2_COEFFICIENT * hco3 + ALKALOSIS_PCO2_CONSTANT, 0)


def calculate_expected_hco3_respiratory_acidosis(pco2: float, is_chronic: bool = False) -> float:
    delta_pco2 = pco2 - PCO2_NORMAL
    coef = RESP_ACIDOSIS_CHRONIC_COEFFICIENT if is_chronic else RESP_ACIDOSIS_ACUTE_COEFFICIENT
    return round(HCO3_NORMAL + coef * delta_pco2, 1)


def calculate_expected_hco3_respiratory_alkalosis(pco2: float, is_chronic: bool = False) -> float:
    delta_pco2 = PCO2_NORMAL - pco2
    coef = RESP_ALKALOSIS_CHRONIC_COEFFICIENT if is_chronic else RESP_ALKALOSIS_ACUTE_COEFFICIENT
    return round(HCO3_NORMAL - coef * delta_pco2, 1)


def assess_compensation(ph: float, pco2: float, hco3: float, be: float) -> Tuple[Optional[float], Optional[float], str, str, Optional[float]]:
    is_acidemia = ph < PH_NORMAL_LOW
    is_alkalemia = ph > PH_NORMAL_HIGH
    is_pco2_high = pco2 > PCO2_NORMAL_HIGH
    is_pco2_low = pco2 < PCO2_NORMAL_LOW
    is_met_acidosis = be < -CLINICAL_SIGNIFICANCE_THRESHOLD
    is_met_alkalosis = be > CLINICAL_SIGNIFICANCE_THRESHOLD
    
    if is_met_acidosis and (is_acidemia or ph <= PH_NORMAL_HIGH):
        expected_pco2 = calculate_expected_pco2_metabolic_acidosis(hco3)
        diff = pco2 - expected_pco2
        if abs(diff) <= WINTERS_TOLERANCE:
            return expected_pco2, None, "Uygun respiratuvar kompanzasyon", f"Beklenen pCO₂: {expected_pco2:.0f} ± 2", round(diff, 1)
        elif diff < -WINTERS_TOLERANCE:
            return expected_pco2, None, "Ek respiratuvar alkaloz", f"pCO₂ beklenenden {abs(diff):.0f} düşük", round(diff, 1)
        else:
            return expected_pco2, None, "Ek respiratuvar asidoz", f"pCO₂ beklenenden {diff:.0f} yüksek", round(diff, 1)
    
    if is_met_alkalosis and (is_alkalemia or ph >= PH_NORMAL_LOW):
        expected_pco2 = calculate_expected_pco2_metabolic_alkalosis(hco3)
        diff = pco2 - expected_pco2
        if abs(diff) <= ALKALOSIS_TOLERANCE:
            return expected_pco2, None, "Uygun respiratuvar kompanzasyon", f"Beklenen pCO₂: {expected_pco2:.0f} ± 2", round(diff, 1)
        elif diff < -ALKALOSIS_TOLERANCE:
            return expected_pco2, None, "Ek respiratuvar alkaloz", f"pCO₂ beklenenden düşük", round(diff, 1)
        else:
            return expected_pco2, None, "Ek respiratuvar asidoz", f"pCO₂ beklenenden yüksek", round(diff, 1)
    
    if is_pco2_high and is_acidemia:
        exp_acute = calculate_expected_hco3_respiratory_acidosis(pco2, False)
        exp_chronic = calculate_expected_hco3_respiratory_acidosis(pco2, True)
        if hco3 <= exp_acute + COMPENSATION_TOLERANCE:
            return None, exp_acute, "Akut respiratuvar asidoz", f"Beklenen HCO₃⁻ (akut): {exp_acute:.1f}", round(hco3 - exp_acute, 1)
        elif hco3 >= exp_chronic - COMPENSATION_TOLERANCE:
            return None, exp_chronic, "Kronik respiratuvar asidoz", f"Beklenen HCO₃⁻ (kronik): {exp_chronic:.1f}", round(hco3 - exp_chronic, 1)
        return None, exp_acute, "Subakut respiratuvar asidoz", f"HCO₃⁻ akut ve kronik arasında", None
    
    if is_pco2_low and is_alkalemia:
        exp_acute = calculate_expected_hco3_respiratory_alkalosis(pco2, False)
        exp_chronic = calculate_expected_hco3_respiratory_alkalosis(pco2, True)
        if hco3 >= exp_acute - COMPENSATION_TOLERANCE:
            return None, exp_acute, "Akut respiratuvar alkaloz", f"Beklenen HCO₃⁻ (akut): {exp_acute:.1f}", round(hco3 - exp_acute, 1)
        elif hco3 <= exp_chronic + COMPENSATION_TOLERANCE:
            return None, exp_chronic, "Kronik respiratuvar alkaloz", f"Beklenen HCO₃⁻ (kronik): {exp_chronic:.1f}", round(hco3 - exp_chronic, 1)
        return None, exp_acute, "Subakut respiratuvar alkaloz", f"HCO₃⁻ akut ve kronik arasında", None
    
    return None, None, "Belirgin primer bozukluk yok", "", None


# === YORUMLAMA ===

def interpret_ph(ph: float) -> Tuple[str, str]:
    if ph < PH_NORMAL_LOW: return "Asidemi", "critical"
    elif ph > PH_NORMAL_HIGH: return "Alkalemi", "critical"
    return "Normal", "normal"


def interpret_pco2(pco2: float) -> Tuple[str, str]:
    if pco2 > PCO2_NORMAL_HIGH: return "Respiratuvar asidoz", "warning"
    elif pco2 < PCO2_NORMAL_LOW: return "Respiratuvar alkaloz", "warning"
    return "Normal", "normal"


def interpret_sid_effect(sid_effect: float) -> Tuple[str, str]:
    if sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD: return "SID asidozu", "warning"
    elif sid_effect > CLINICAL_SIGNIFICANCE_THRESHOLD: return "SID alkalozu", "info"
    return "Normal", "normal"


def interpret_albumin_effect(alb_effect: float) -> Tuple[str, str]:
    if alb_effect > CLINICAL_SIGNIFICANCE_THRESHOLD: return "Hipoalbüminemik alkaloz", "info"
    elif alb_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD: return "Hiperalbüminemik asidoz", "warning"
    return "Normal", "normal"


def interpret_lactate(lactate: float) -> Tuple[str, str]:
    if lactate > LACTATE_THRESHOLD: return "Laktik asidoz", "warning"
    return "Normal", "normal"


def interpret_sig(sig: float) -> Tuple[str, str]:
    if sig > SIG_THRESHOLD: return "Ölçülmemiş anyonlar (HAGMA)", "warning"
    elif sig < -SIG_THRESHOLD: return "Ölçülmemiş katyonlar", "info"
    return "Normal", "normal"


def interpret_residual(residual: float) -> Tuple[str, str]:
    if residual < -CLINICAL_SIGNIFICANCE_THRESHOLD: return "Açıklanamayan asidoz", "warning"
    elif residual > CLINICAL_SIGNIFICANCE_THRESHOLD: return "Açıklanamayan alkaloz", "info"
    return "Normal", "normal"


# === YENİ: CONTRIBUTION BREAKDOWN ===

def generate_contribution_breakdown(
    sid_effect: float,
    albumin_effect: Optional[float],
    lactate_effect: Optional[float],
    residual_effect: Optional[float],
    pco2: float,
    be: float
) -> ContributionBreakdown:
    """pH'a etki eden kuvvetlerin ayrıştırılması"""
    
    acidosis_contributors = []
    alkalosis_contributors = []
    
    # SID etkisi
    if sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        acidosis_contributors.append(("SID etkisi", sid_effect, "Düşük SID (hiperkloremik patern)"))
    elif sid_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
        alkalosis_contributors.append(("SID etkisi", sid_effect, "Yüksek SID (hipokloremik patern)"))
    
    # Laktat etkisi
    if lactate_effect is not None and lactate_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        acidosis_contributors.append(("Laktat etkisi", lactate_effect, "Laktik asidoz"))
    
    # Albümin etkisi
    if albumin_effect is not None:
        if albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
            alkalosis_contributors.append(("Albümin etkisi", albumin_effect, "Hipoalbüminemi"))
        elif albumin_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
            acidosis_contributors.append(("Albümin etkisi", albumin_effect, "Hiperalbüminemi"))
    
    # Residual/SIG etkisi
    if residual_effect is not None:
        if residual_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
            acidosis_contributors.append(("Ölçülmemiş anyonlar", residual_effect, "SIG/Residual pozitif"))
        elif residual_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
            alkalosis_contributors.append(("Ölçülmemiş katyonlar", residual_effect, "SIG/Residual negatif"))
    
    # Respiratuvar etki
    respiratory_effect_val = calculate_respiratory_effect(pco2)
    if pco2 > PCO2_NORMAL_HIGH:
        resp = ("Asidoz yönünde", respiratory_effect_val, f"pCO₂ yüksek ({pco2:.0f} mmHg)")
    elif pco2 < PCO2_NORMAL_LOW:
        resp = ("Alkaloz yönünde", respiratory_effect_val, f"pCO₂ düşük ({pco2:.0f} mmHg)")
    else:
        resp = ("Nötr", 0.0, "pCO₂ normal")
    
    # Net metabolik etki
    net_metabolic = sid_effect
    if albumin_effect is not None:
        net_metabolic += albumin_effect
    if lactate_effect is not None:
        net_metabolic += lactate_effect
    if residual_effect is not None:
        net_metabolic += residual_effect
    
    # Özet
    if len(acidosis_contributors) > 0 and len(alkalosis_contributors) > 0:
        summary = "Karşıt etkiler mevcut - bileşenler birbirini kısmen dengeliyor"
    elif len(acidosis_contributors) > 0:
        summary = f"{len(acidosis_contributors)} asidoz yönlü etki tespit edildi"
    elif len(alkalosis_contributors) > 0:
        summary = f"{len(alkalosis_contributors)} alkaloz yönlü etki tespit edildi"
    else:
        summary = "Belirgin metabolik bozukluk yok"
    
    return ContributionBreakdown(
        acidosis_contributors=acidosis_contributors,
        alkalosis_contributors=alkalosis_contributors,
        respiratory_effect=resp,
        net_metabolic=round(net_metabolic, 1),
        summary=summary
    )


# === YENİ: CONTRIBUTION-BASED MECHANISM ANALYSIS ===

def calculate_contribution_percent(effect: float, total_effect: float) -> float:
    """Bir bileşenin BE'ye yüzde katkısını hesapla"""
    if abs(total_effect) < 0.1:
        return 0.0
    return round(abs(effect) / abs(total_effect) * 100, 1)


def classify_contribution_level(percent: float, mechanism_name: str = "") -> str:
    """Contribution yüzdesine göre seviye belirle"""
    name_lower = mechanism_name.lower()

    if "laktat" in name_lower:
        if percent >= 50:
            return "dominant"
        if percent >= 25:
            return "significant"
        if percent > 0:
            return "contributing"
        return "minimal"

    if percent >= 50:
        return "dominant"
    if percent >= 25:
        return "significant"
    if percent >= 10:
        return "contributing"
    return "minimal"


def determine_metabolic_dominance(contributions: Dict[str, Any], flags: List[str]) -> DominanceResult:
    """
    Tekil kaynak: mekanizma katkılarından dominant metabolik mekanizmayı belirler.

    Beklenen giriş:
        contributions = {
            "be": float,
            "sig": Optional[float],
            "mechanisms": [
                {"identifier": "sid", "name": "SID etkisi", "description": str,
                 "effect": float, "direction": "acidosis"|"alkalosis"},
                ...
            ],
            "compensation": Optional[str]
        }
    """

    be = contributions.get("be", 0.0)
    sig = contributions.get("sig")
    mechanism_inputs = contributions.get("mechanisms", [])

    total_acidosis = sum(abs(m.get("effect", 0.0)) for m in mechanism_inputs if m.get("direction") == "acidosis")
    total_alkalosis = sum(m.get("effect", 0.0) for m in mechanism_inputs if m.get("direction") == "alkalosis")

    if be < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        total_reference = max(abs(be), total_acidosis)
    elif be > CLINICAL_SIGNIFICANCE_THRESHOLD:
        total_reference = max(abs(be), total_alkalosis)
    else:
        total_reference = max(abs(be), total_acidosis, total_alkalosis)

    mechanism_contributions: List[MechanismContribution] = []
    for m in mechanism_inputs:
        effect = m.get("effect", 0.0)
        if abs(effect) < CLINICAL_SIGNIFICANCE_THRESHOLD:
            continue
        percent = calculate_contribution_percent(effect, total_reference)
        level = classify_contribution_level(percent, m.get("name", ""))
        mechanism_contributions.append(
            MechanismContribution(
                name=m.get("name", ""),
                identifier=m.get("identifier", ""),
                effect_meq=round(effect, 1),
                contribution_percent=percent,
                level=level,
                direction=m.get("direction", ""),
                description=m.get("description", m.get("name", "")),
            )
        )

    mechanism_contributions.sort(key=lambda x: x.contribution_percent, reverse=True)

    dominant = None
    significant: List[MechanismContribution] = []
    contributing: List[MechanismContribution] = []

    for mc in mechanism_contributions:
        if mc.level == "dominant" and dominant is None:
            dominant = mc
        elif mc.level == "significant":
            significant.append(mc)
        elif mc.level == "contributing":
            contributing.append(mc)

    if dominant is None and mechanism_contributions:
        dominant = mechanism_contributions[0]

    pattern_flags: List[str] = []
    if dominant:
        if dominant.identifier == "unmeasured":
            pattern_flags.append("unmeasured_anion")
        if dominant.identifier == "sid" and dominant.direction == "acidosis":
            pattern_flags.append("hyperchloremic_pattern")
        if dominant.identifier == "lactate":
            pattern_flags.append("lactate_dominant")

    lactate_component = next((m for m in mechanism_contributions if m.identifier == "lactate"), None)
    if lactate_component and lactate_component.level in ("significant", "dominant") and "lactate_dominant" not in pattern_flags:
        pattern_flags.append("lactate_significant")

    if sig is not None and sig > SIG_THRESHOLD:
        pattern_flags.append("sig_elevated")

    if total_acidosis > 2 and total_alkalosis > 2:
        pattern_flags.append("masking_present")

    albumin_component = next((m for m in mechanism_contributions if m.identifier == "albumin" and m.direction == "alkalosis"), None)
    if albumin_component and total_acidosis > CLINICAL_SIGNIFICANCE_THRESHOLD:
        pattern_flags.append("masked_acidosis_risk")

    if be >= 0 and dominant and dominant.direction == "acidosis":
        alkalosis_leader = next((m for m in mechanism_contributions if m.direction == "alkalosis"), None)
        dominant = alkalosis_leader

    if abs(total_reference) < CLINICAL_SIGNIFICANCE_THRESHOLD:
        dominant = None
        pattern_flags = []

    return DominanceResult(
        total_metabolic_effect=be,
        all_mechanisms=mechanism_contributions,
        dominant=dominant,
        significant=significant,
        contributing=contributing,
        pattern_flags=pattern_flags,
    )


def analyze_mechanisms(
    be: float,
    sid_effect: float,
    albumin_effect: Optional[float],
    lactate_effect: Optional[float],
    residual_effect: Optional[float],
    sig: Optional[float],
    pco2: float,
    compensation_status: str
) -> MechanismAnalysis:
    """
    Contribution-based mechanism analysis.
    Determines dominant mechanism based on absolute mEq/L contribution, not presence.
    """

    mechanisms: List[Dict[str, Any]] = []

    if abs(sid_effect) > CLINICAL_SIGNIFICANCE_THRESHOLD:
        direction = "acidosis" if sid_effect < 0 else "alkalosis"
        mechanisms.append({
            "identifier": "sid",
            "name": "SID etkisi",
            "description": f"Güçlü iyon (SID) aracılı metabolik {'asidoz' if direction == 'acidosis' else 'alkaloz'}",
            "effect": sid_effect,
            "direction": direction,
        })

    if lactate_effect is not None and abs(lactate_effect) > 0.5:
        mechanisms.append({
            "identifier": "lactate",
            "name": "Laktat aracılı etki",
            "description": "Laktat aracılı metabolik asidoz mekanizması",
            "effect": lactate_effect,
            "direction": "acidosis",
        })

    if albumin_effect is not None and abs(albumin_effect) > CLINICAL_SIGNIFICANCE_THRESHOLD:
        direction = "alkalosis" if albumin_effect > 0 else "acidosis"
        mechanisms.append({
            "identifier": "albumin",
            "name": "Albümin etkisi",
            "description": f"Zayıf asit {'azalması (hipoalbüminemi)' if direction == 'alkalosis' else 'artışı'} etkisi",
            "effect": albumin_effect,
            "direction": direction,
        })

    if residual_effect is not None and abs(residual_effect) > CLINICAL_SIGNIFICANCE_THRESHOLD:
        direction = "acidosis" if residual_effect < 0 else "alkalosis"
        mechanisms.append({
            "identifier": "unmeasured",
            "name": "Ölçülmemiş bileşen etkisi",
            "description": f"Ölçülmemiş {'anyon' if direction == 'acidosis' else 'katyon'} aracılı etki",
            "effect": residual_effect,
            "direction": direction,
        })

    dominance_result = determine_metabolic_dominance(
        {
            "be": be,
            "sig": sig,
            "mechanisms": mechanisms,
        },
        [],
    )

    pattern = ""
    if dominance_result.dominant:
        if dominance_result.dominant.identifier == "unmeasured":
            pattern = (
                "Patern: ölçülmemiş anyon birikimi ile uyumlu (örn. keton birikimi, toksik metabolitler, organik asitler)."
            )
        elif dominance_result.dominant.identifier == "sid" and dominance_result.dominant.direction == "acidosis":
            pattern = "Patern: hiperkloremik (dilüsyonel) güçlü iyon aracılı metabolik asidoz."
        elif dominance_result.dominant.identifier == "lactate":
            pattern = "Patern: laktat aracılı metabolik asidoz (fizyoloji odaklı, tanı dışı bilgilendirme)."

    if "masking_present" in dominance_result.pattern_flags:
        pattern = f"{pattern} Karşıt yönlü metabolik etkiler birbirini kısmen maskeleyebilir.".strip()

    resp_status = ""
    if pco2 > PCO2_NORMAL_HIGH:
        if "kompanzasyon" in compensation_status.lower() and "uygun" in compensation_status.lower():
            resp_status = "Solunumsal kompanzasyon (yetersiz veya ek respiratuvar asidoz)"
        else:
            resp_status = "Respiratuvar asidoz bileşeni mevcut"
    elif pco2 < PCO2_NORMAL_LOW:
        if "kompanzasyon" in compensation_status.lower() and "uygun" in compensation_status.lower():
            resp_status = "Uygun solunumsal kompanzasyon"
        else:
            resp_status = "Respiratuvar alkaloz bileşeni mevcut"
    else:
        resp_status = "Solunumsal bileşen normal"

    return MechanismAnalysis(
        total_metabolic_effect=be,
        dominant_mechanism=dominance_result.dominant,
        significant_mechanisms=dominance_result.significant,
        contributing_mechanisms=dominance_result.contributing,
        all_mechanisms=dominance_result.all_mechanisms,
        pattern_description=pattern,
        respiratory_status=resp_status,
        respiratory_details=compensation_status,
    )


def generate_headline(
    mechanism_analysis: MechanismAnalysis,
    ph: float,
    pco2: float,
    be: float
) -> Headline:
    """
    Generate mechanism-based headline (non-diagnostic).
    Uses contribution percentages, not presence-based detection.
    """
    
    dominant_str = ""
    significant_list = []
    contributing_list = []
    
    # Check if there's any metabolic disorder
    if abs(be) < CLINICAL_SIGNIFICANCE_THRESHOLD:
        dominant_str = "Normal asit-baz dengesi"
    elif mechanism_analysis.dominant_mechanism:
        dm = mechanism_analysis.dominant_mechanism
        # Format: "Mechanism (XX% katkı, Y.Y mEq/L)"
        dominant_str = f"{dm.description} ({dm.contribution_percent:.0f}% katkı)"
    else:
        if be < 0:
            dominant_str = "Metabolik asidoz (mekanizma belirlenemedi)"
        else:
            dominant_str = "Metabolik alkaloz (mekanizma belirlenemedi)"
    
    # Significant mechanisms
    for sm in mechanism_analysis.significant_mechanisms:
        significant_list.append(f"{sm.description} ({sm.contribution_percent:.0f}%)")
    
    # Contributing mechanisms
    for cm in mechanism_analysis.contributing_mechanisms:
        if cm.contribution_percent >= 10:  # Only show >10%
            contributing_list.append(f"{cm.name} ({cm.contribution_percent:.0f}%)")
    
    # Pattern note
    pattern_note = mechanism_analysis.pattern_description
    
    return Headline(
        dominant_mechanism=dominant_str,
        significant_mechanisms=significant_list,
        contributing_mechanisms=contributing_list,
        respiratory_status=mechanism_analysis.respiratory_status,
        pattern_note=pattern_note
    )


# === YENİ: KLASİK KARŞILAŞTIRMA ===

def generate_classic_comparison(
    hco3: float, be: float, sid_effect: float,
    albumin_gl: Optional[float], albumin_effect: Optional[float],
    anion_gap: float, anion_gap_corrected: Optional[float],
    sig: Optional[float]
) -> ClassicComparison:
    """Klasik yaklaşıma göre fark analizi"""
    
    differences = []
    missed = []
    advantage = ""
    
    # HCO3 normal ama SID düşük
    if 22 <= hco3 <= 26 and sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        differences.append(CLASSIC_COMPARISON["hco3_normal_sid_low"])
        missed.append("SID düşük - güçlü iyon asidozu mevcut")
    
    # BE normal ama SID düşük
    if -2 <= be <= 2 and sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        differences.append(CLASSIC_COMPARISON["normal_be_low_sid"])
        missed.append("Maskelenmiş asidoz")
    
    # Albümin maskeleme
    if albumin_gl is not None and albumin_gl < ALBUMIN_LOW_GL and albumin_effect is not None:
        if albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD:
            differences.append(CLASSIC_COMPARISON["albumin_masking"])
            missed.append("Hipoalbüminemi maskeleme etkisi")
    
    # AG vs SIG farkı
    if anion_gap_corrected is not None and sig is not None:
        if anion_gap <= 16 and sig > SIG_HIGH:
            differences.append(CLASSIC_COMPARISON["ag_vs_sig"])
            missed.append("AG normal ama SIG yüksek")
    
    # Karşıt etkiler
    if albumin_effect is not None and sid_effect != 0:
        if (albumin_effect > 0 and sid_effect < 0) or (albumin_effect < 0 and sid_effect > 0):
            differences.append(CLASSIC_COMPARISON["mixed_hidden"])
            missed.append("Karşıt etkiler birbirini maskelemiş")
    
    if differences:
        advantage = "Stewart-Fencl yaklaşımı, klasik analizde gözden kaçabilecek bozuklukları ortaya çıkardı."
    else:
        advantage = "Bu vakada klasik ve Stewart yaklaşımları benzer sonuç veriyor."
    
    return ClassicComparison(differences=differences, missed_by_classic=missed, stewart_advantage=advantage)


# === YENİ: CDS NOT OLUŞTURMA ===

def generate_cds_notes(
    sid_simple: float, sid_effect: float,
    sig: Optional[float], albumin_gl: Optional[float],
    lactate: Optional[float], ph: float, be: float,
    hco3: float, na: float, cl: float
) -> List[CDSNote]:
    """Klinik karar destek notları oluştur"""
    
    notes = []
    cl_na_ratio = cl / na if na > 0 else 0
    
    # A Kategorisi: Fizikokimyasal zorunluluklar
    
    # SID düşük
    if sid_simple < SID_LOW_THRESHOLD:
        cds = CDS_NOTES["sid_low"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # SID yüksek
    if sid_simple > SID_HIGH_THRESHOLD:
        cds = CDS_NOTES["sid_high"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # SIG pozitif
    if sig is not None and sig > SIG_HIGH:
        cds = CDS_NOTES["sig_positive"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # SIG negatif
    if sig is not None and sig < SIG_LOW:
        cds = CDS_NOTES["sig_negative"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # Albümin düşük
    if albumin_gl is not None and albumin_gl < ALBUMIN_LOW_GL:
        cds = CDS_NOTES["albumin_low"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # Cl/Na yüksek
    if cl_na_ratio > CL_NA_RATIO_THRESHOLD:
        cds = CDS_NOTES["cl_na_high"]
        notes.append(CDSNote("A", cds["condition"], cds["note"], [], cds["refs"]))
    
    # B Kategorisi: Maskelenme
    
    # Normal pH + düşük SID
    if PH_NORMAL_LOW <= ph <= PH_NORMAL_HIGH and sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        cds = CDS_NOTES["normal_ph_low_sid"]
        notes.append(CDSNote("B", cds["condition"], cds["note"], [], cds["refs"]))
    
    # Normal BE + düşük SID
    if -2 <= be <= 2 and sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD:
        cds = CDS_NOTES["normal_be_low_sid"]
        notes.append(CDSNote("B", cds["condition"], cds["note"], [], cds["refs"]))
    
    # Albümin düşük + laktat yüksek
    if albumin_gl is not None and albumin_gl < ALBUMIN_LOW_GL:
        if lactate is not None and lactate > LACTATE_THRESHOLD:
            cds = CDS_NOTES["albumin_low_lactate_high"]
            notes.append(CDSNote("B", cds["condition"], cds["note"], [], cds["refs"]))
    
    # C Kategorisi: Patern → Mekanizma
    
    # Hiperkloremik patern
    if sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD and cl > 105:
        cds = CDS_NOTES["pattern_hyperchloremic"]
        notes.append(CDSNote("C", cds["condition"], cds["note"], cds.get("mechanisms", []), cds["refs"]))
    
    # Ölçülmemiş anyon paternı
    if lactate is not None and lactate <= LACTATE_THRESHOLD and sig is not None and sig > SIG_HIGH:
        cds = CDS_NOTES["pattern_unmeasured_anion"]
        notes.append(CDSNote("C", cds["condition"], cds["note"], cds.get("mechanisms", []), cds["refs"]))
    
    # Maskelenmiş karışık patern
    if albumin_gl is not None and albumin_gl < ALBUMIN_LOW_GL:
        if PH_NORMAL_LOW <= ph <= PH_NORMAL_HIGH and lactate is not None and lactate > LACTATE_THRESHOLD:
            cds = CDS_NOTES["pattern_masked_mixed"]
            notes.append(CDSNote("C", cds["condition"], cds["note"], cds.get("mechanisms", []), cds["refs"]))
    
    return notes


# === DOMINANT DISORDER ===

def determine_dominant_disorder(
    ph: float, pco2: float, be: float, sid_effect: float,
    albumin_effect: Optional[float], lactate: Optional[float],
    residual_effect: Optional[float], sig: Optional[float]
) -> Tuple[str, List[str]]:
    
    components = []
    is_acidemia = ph < PH_NORMAL_LOW
    is_alkalemia = ph > PH_NORMAL_HIGH
    is_resp_acidosis = pco2 > PCO2_NORMAL_HIGH
    is_resp_alkalosis = pco2 < PCO2_NORMAL_LOW
    has_sid_acidosis = sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD
    has_sid_alkalosis = sid_effect > CLINICAL_SIGNIFICANCE_THRESHOLD
    has_alb_alkalosis = albumin_effect is not None and albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD
    has_lactic_acidosis = lactate is not None and lactate > LACTATE_THRESHOLD
    has_unmeasured = (residual_effect is not None and residual_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD) or \
                     (sig is not None and sig > SIG_THRESHOLD)
    
    if is_resp_acidosis: components.append("respiratory_acidosis")
    if is_resp_alkalosis: components.append("respiratory_alkalosis")
    if has_sid_acidosis: components.append("hyperchloremic_acidosis")
    if has_sid_alkalosis: components.append("hypochloremic_alkalosis")
    if has_alb_alkalosis: components.append("hypoalbuminemic_alkalosis")
    if has_lactic_acidosis: components.append("lactic_acidosis")
    if has_unmeasured: components.append("hagma")
    
    if len(components) == 0: return "normal", []
    elif len(components) == 1: return components[0], components
    elif len(components) == 2: return "mixed_disorder", components
    return "triple_disorder", components


# === ATOT ===

def calculate_atot(albumin_gl: Optional[float], po4: Optional[float]) -> Optional[float]:
    if albumin_gl is None: return None
    atot = ATOT_ALBUMIN_COEFFICIENT * albumin_gl
    if po4 is not None: atot += ATOT_PO4_COEFFICIENT * po4
    return round(atot, 1)


# === ANA ANALİZ FONKSİYONU ===

def analyze_stewart(inp: StewartInput, mode: str = "quick") -> Tuple[StewartOutput, ValidationResult]:
    """Ana Stewart analizi"""
    
    validation = validate_input(inp)
    if not validation.is_valid:
        empty_sid = SIDValues(0, "", None, "", None, "", [])
        return StewartOutput(
            hco3_calculated=0, hco3_used=0, hco3_source="",
            be_calculated=0, be_used=0, be_source="",
            sid_values=empty_sid, flags=["VALIDATION_FAILED"]
        ), validation
    
    # HCO3
    hco3_calculated = calculate_hco3(inp.ph, inp.pco2)
    flags = []
    warnings = []
    soft_warnings = []
    
    if inp.hco3 is not None:
        hco3_used, hco3_source = inp.hco3, "manual"
        is_consistent, diff = check_hco3_consistency(inp.hco3, hco3_calculated)
        if not is_consistent:
            warnings.append(f"{VALIDATION_MESSAGES['hco3_mismatch']} (Fark: {diff})")
            flags.append("HCO3_MISMATCH")
    else:
        hco3_used, hco3_source = hco3_calculated, "calculated"
        flags.append("HCO3_CALCULATED")
    
    # BE
    be_calculated = calculate_be(inp.ph, hco3_used)
    if inp.be is not None:
        be_input = -inp.be if inp.is_be_base_deficit else inp.be
        be_used, be_source = be_input, "manual"
        is_consistent, diff = check_be_consistency(be_input, be_calculated)
        if not is_consistent:
            warnings.append(f"{VALIDATION_MESSAGES['be_mismatch']} (Fark: {diff})")
            flags.append("BE_MISMATCH")
    else:
        be_used, be_source = be_calculated, "calculated"
        flags.append("BE_CALCULATED")
    
    # SID
    sid_values = calculate_all_sids(inp)
    albumin_gdl = inp.albumin_gl / 10 if inp.albumin_gl is not None else None

    if sid_values.sid_full_status != "complete":
        missing_list = ", ".join(sid_values.sid_full_missing)
        warnings.append(
            f"SID_full yaklaşık: Eksik parametreler ({missing_list}) nedeniyle hesaplama sınırlı"
        )
        flags.append("SID_FULL_APPROXIMATE")
        log_calculation_warning("sid_full_approximate", {"missing": sid_values.sid_full_missing})
    
    # Bileşen etkileri
    sid_effect = calculate_sid_effect(sid_values.sid_simple)
    albumin_effect = calculate_albumin_effect(albumin_gdl) if albumin_gdl is not None else None
    lactate_effect = calculate_lactate_effect(inp.lactate) if inp.lactate is not None else None
    residual_effect = calculate_residual_effect(be_used, sid_effect, albumin_effect, lactate_effect)
    respiratory_effect = calculate_respiratory_effect(inp.pco2)
    
    # AG
    ag = calculate_anion_gap(inp.na, inp.cl, hco3_used)
    ag_corrected = calculate_corrected_anion_gap(ag, albumin_gdl) if albumin_gdl is not None else None
    
    # Cl/Na
    cl_na_ratio = round(inp.cl / inp.na, 3) if inp.na > 0 else 0
    
    # Advanced mod
    sid_effective, sig, sig_reliability, sig_interpretation, atot = None, None, "unknown", "", None
    sig_warnings = []
    
    if mode == "advanced":
        sid_effective, sid_effective_missing = calculate_sid_effective(inp.ph, hco3_used, inp.albumin_gl, inp.po4)
        if sid_effective_missing:
            warnings.append(
                "SID_effective yaklaşık: Albümin/Fosfat eksikliği nedeniyle kesinlik azalır"
            )
            flags.append("SID_EFFECTIVE_APPROXIMATE")
            log_calculation_warning(
                "sid_effective_approximate", {"missing": sid_effective_missing}
            )
        if sid_values.sid_full is not None:
            sig = calculate_sig(sid_values.sid_full, sid_effective)
            sig_reliability, sig_warnings = assess_sig_reliability(inp.lactate, inp.ca, inp.mg, inp.albumin_gl)
            sig_interpretation = interpret_sig_categorical(sig)
            warnings.extend(sig_warnings)
            if sig_reliability == "approximate": flags.append("SIG_APPROXIMATE")
            elif sig_reliability == "underestimated": flags.append("SIG_UNDERESTIMATED")
            elif sig_reliability == "unreliable": flags.append("SIG_UNRELIABLE")
        atot = calculate_atot(inp.albumin_gl, inp.po4)
    
    # Kompanzasyon
    expected_pco2, expected_hco3, comp_status, comp_details, obs_exp_diff = assess_compensation(
        inp.ph, inp.pco2, hco3_used, be_used)
    
    # Contribution Breakdown
    contribution = generate_contribution_breakdown(
        sid_effect, albumin_effect, lactate_effect, residual_effect, inp.pco2, be_used)
    
    # Mechanism Analysis (contribution-based)
    mechanism_analysis = analyze_mechanisms(
        be_used, sid_effect, albumin_effect, lactate_effect, 
        residual_effect, sig, inp.pco2, comp_status)
    
    # Headline (refactored - mechanism-based)
    headline = generate_headline(mechanism_analysis, inp.ph, inp.pco2, be_used)
    
    # Classic Comparison
    classic_comparison = generate_classic_comparison(
        hco3_used, be_used, sid_effect, inp.albumin_gl, albumin_effect, ag, ag_corrected, sig)
    
    # CDS Notes
    cds_notes = generate_cds_notes(
        sid_values.sid_simple, sid_effect, sig, inp.albumin_gl, inp.lactate,
        inp.ph, be_used, hco3_used, inp.na, inp.cl)
    
    # Yorumlar
    interpretations = []
    ph_interp, _ = interpret_ph(inp.ph)
    if ph_interp != "Normal": interpretations.append(f"pH: {ph_interp}")
    pco2_interp, _ = interpret_pco2(inp.pco2)
    if pco2_interp != "Normal": interpretations.append(f"pCO₂: {pco2_interp}")
    
    if mode == "quick":
        sid_interp, _ = interpret_sid_effect(sid_effect)
        if sid_interp != "Normal": interpretations.append(f"{abs(sid_effect):.1f} mEq/L {sid_interp}")
        if albumin_effect is not None:
            alb_interp, _ = interpret_albumin_effect(albumin_effect)
            if alb_interp != "Normal": interpretations.append(f"{abs(albumin_effect):.1f} mEq/L {alb_interp}")
        if inp.lactate is not None and inp.lactate > LACTATE_THRESHOLD:
            interpretations.append(f"{inp.lactate:.1f} mmol/L laktat artışı (asidoz yönlü katkı)")
        if residual_effect is not None:
            res_interp, _ = interpret_residual(residual_effect)
            if res_interp != "Normal": interpretations.append(f"{abs(residual_effect):.1f} mEq/L {res_interp}")
    else:
        if sig is not None:
            sig_interp, _ = interpret_sig(sig)
            if sig_interp != "Normal": interpretations.append(f"SIG: {sig:.1f} - {sig_interp}")
    
    # Eksik parametreler (yumuşak dil)
    missing_params = []
    if inp.albumin_gl is None:
        missing_params.append("Albümin")
        soft_warnings.append(SOFT_MESSAGES["missing_albumin"])
    if inp.lactate is None:
        missing_params.append("Laktat")
        soft_warnings.append(SOFT_MESSAGES["missing_lactate"])
    if mode == "advanced":
        if inp.k is None: soft_warnings.append(SOFT_MESSAGES["missing_k"])
        if inp.ca is None: soft_warnings.append(SOFT_MESSAGES["missing_ca"])
        if inp.mg is None: soft_warnings.append(SOFT_MESSAGES["missing_mg"])
        if inp.po4 is None: soft_warnings.append(SOFT_MESSAGES["missing_po4"])
        missing_params.extend(sid_values.sid_full_missing)
    
    if missing_params: flags.append("INCOMPLETE_DATA")
    
    # Dominant disorder
    dominant, disorder_components = determine_dominant_disorder(
        inp.ph, inp.pco2, be_used, sid_effect, albumin_effect, inp.lactate, residual_effect, sig)
    
    return StewartOutput(
        hco3_calculated=hco3_calculated, hco3_used=hco3_used, hco3_source=hco3_source,
        be_calculated=be_calculated, be_used=be_used, be_source=be_source,
        sid_values=sid_values, sid_effective=sid_effective, sig=sig,
        sig_reliability=sig_reliability, sig_interpretation=sig_interpretation,
        atot=atot, cl_na_ratio=cl_na_ratio,
        sid_effect=sid_effect, albumin_effect=albumin_effect,
        lactate_effect=lactate_effect, residual_effect=residual_effect,
        respiratory_effect=respiratory_effect,
        anion_gap=ag, anion_gap_corrected=ag_corrected,
        expected_pco2=expected_pco2, expected_hco3=expected_hco3,
        compensation_status=comp_status, compensation_details=comp_details,
        observed_expected_diff=obs_exp_diff,
        contribution=contribution, mechanism_analysis=mechanism_analysis, headline=headline,
        classic_comparison=classic_comparison, cds_notes=cds_notes,
        flags=flags, warnings=warnings, soft_warnings=soft_warnings,
        interpretations=interpretations,
        dominant_disorder=dominant, disorder_components=disorder_components,
        missing_params=missing_params, assumed_params=[]
    ), validation


# === CSV EXPORT/IMPORT ===

def output_to_dict(inp: StewartInput, out: StewartOutput) -> Dict:
    return {
        "ph": inp.ph, "pco2": inp.pco2, "na": inp.na, "cl": inp.cl,
        "k": inp.k, "ca": inp.ca, "mg": inp.mg, "lactate": inp.lactate,
        "albumin_gl": inp.albumin_gl, "po4": inp.po4,
        "be_input": inp.be, "hco3_input": inp.hco3,
        "hco3_calculated": out.hco3_calculated, "hco3_used": out.hco3_used,
        "be_calculated": out.be_calculated, "be_used": out.be_used,
        "sid_simple": out.sid_values.sid_simple,
        "sid_basic": out.sid_values.sid_basic,
        "sid_full": out.sid_values.sid_full,
        "sid_effective": out.sid_effective, "sig": out.sig,
        "sig_reliability": out.sig_reliability,
        "cl_na_ratio": out.cl_na_ratio,
        "sid_effect": out.sid_effect, "albumin_effect": out.albumin_effect,
        "lactate_effect": out.lactate_effect, "residual_effect": out.residual_effect,
        "anion_gap": out.anion_gap, "anion_gap_corrected": out.anion_gap_corrected,
        "compensation_status": out.compensation_status,
        "headline_dominant": out.headline.dominant_mechanism if out.headline else "",
        "headline_significant": "|".join(out.headline.significant_mechanisms) if out.headline else "",
        "headline_contributing": "|".join(out.headline.contributing_mechanisms) if out.headline else "",
        "headline_respiratory": out.headline.respiratory_status if out.headline else "",
        "headline_pattern": out.headline.pattern_note if out.headline else "",
        "headline_confidence": out.headline.confidence if out.headline else "",
        "dominant_disorder": out.dominant_disorder,
        "disorder_components": ",".join(out.disorder_components),
        "flags": ",".join(out.flags),
        "warnings": "|".join(out.warnings),
        "soft_warnings": "|".join(out.soft_warnings),
        "missing_params": ",".join(out.missing_params),
        "cds_notes_count": len(out.cds_notes),
    }


def dict_to_input(d: Dict) -> StewartInput:
    def safe_float(val):
        if val is None or val == "" or (isinstance(val, float) and math.isnan(val)):
            return None
        return float(val)
    
    return StewartInput(
        ph=float(d.get("ph", 7.4)), pco2=float(d.get("pco2", 40)),
        na=float(d.get("na", 140)), cl=float(d.get("cl", 100)),
        hco3=safe_float(d.get("hco3") or d.get("hco3_input")),
        be=safe_float(d.get("be") or d.get("be_input")),
        k=safe_float(d.get("k")), ca=safe_float(d.get("ca")),
        mg=safe_float(d.get("mg")), lactate=safe_float(d.get("lactate")),
        albumin_gl=safe_float(d.get("albumin_gl")), po4=safe_float(d.get("po4")),
    )


def stewart_input_from_normalized(values: Dict[str, float]) -> StewartInput:
    """Construct StewartInput from normalized numeric dictionary"""
    return StewartInput(
        ph=values["ph"],
        pco2=values["pco2"],
        na=values["na"],
        cl=values["cl"],
        hco3=values.get("hco3"),
        be=values.get("be"),
        k=values.get("k"),
        ca=values.get("ca"),
        mg=values.get("mg"),
        lactate=values.get("lactate"),
        albumin_gl=values.get("albumin_gl"),
        po4=values.get("po4"),
        is_be_base_deficit=values.get("is_be_base_deficit", False),
    )


def normalize_input(data: Dict, mode: str = "quick") -> Tuple[Optional[StewartInput], Any]:
    """Single entry point for validation + normalization"""
    validation = validate_input_dict(data, mode=mode)
    if not validation.is_valid:
        return None, validation

    normalized = validation.normalized_values
    inp = stewart_input_from_normalized(normalized)
    return inp, validation
