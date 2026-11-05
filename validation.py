# validation.py
# Stewart Asit-Baz Analizi - Input Validation Module
# Centralized validation, unit normalization, and input sanitization

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Tuple, Union
import re
import math

from constants import (
    PH_MIN, PH_MAX, PCO2_MIN, PCO2_MAX,
    NA_MIN, NA_MAX, CL_MIN, CL_MAX, K_MIN, K_MAX,
    CA_MIN, CA_MAX, MG_MIN, MG_MAX,
    LACTATE_MIN, LACTATE_MAX,
    ALBUMIN_MIN_GL, ALBUMIN_MAX_GL,
    ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL,
    PO4_MIN, PO4_MAX,
    BE_MIN, BE_MAX,
    VALIDATION_MESSAGES,
    PHYSIOLOGIC_LIMITS,
    EXTREME_THRESHOLDS,
    CRITICAL_MESSAGES,
    SEVERITY_LEVELS,
)
from logger import log_calculation_warning, log_analysis_error


# =============================================================================
# VALIDATION RESULT
# =============================================================================

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_values: Dict[str, Any] = field(default_factory=dict)
    assumed_defaults: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# VALUE SANITIZATION
# =============================================================================

def sanitize_numeric(value: Any, allow_negative: bool = False) -> Optional[float]:
    """
    Sanitize and convert value to float.
    
    Handles:
    - String with comma decimal separator ("7,40" -> 7.40)
    - String with spaces ("140 " -> 140)
    - Empty strings -> None
    - Invalid values -> None
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        if math.isnan(value) or math.isinf(value):
            return None
        return float(value) if (allow_negative or value >= 0) else None
    
    if isinstance(value, str):
        # Strip whitespace
        value = value.strip()
        
        if not value or value.lower() in ("", "nan", "none", "null", "-", "n/a"):
            return None
        
        # Replace comma with dot for decimal
        value = value.replace(",", ".")
        
        # Remove any non-numeric characters except dot and minus
        value = re.sub(r"[^\d.\-]", "", value)
        
        try:
            result = float(value)
            if math.isnan(result) or math.isinf(result):
                return None
            return result if (allow_negative or result >= 0) else None
        except (ValueError, TypeError):
            return None
    
    return None


def normalize_unit(value: float, from_unit: str, to_unit: str) -> float:
    """
    Normalize units.
    
    Supported conversions:
    - Albumin: g/dL <-> g/L
    - Ca: mg/dL <-> mmol/L
    - Phosphate: mg/dL <-> mmol/L
    """
    conversions = {
        ("albumin_gdl", "albumin_gl"): lambda x: x * 10,
        ("albumin_gl", "albumin_gdl"): lambda x: x / 10,
        ("ca_mgdl", "ca_mmol"): lambda x: x / 4.0,  # Approximate
        ("ca_mmol", "ca_mgdl"): lambda x: x * 4.0,
        ("po4_mgdl", "po4_mmol"): lambda x: x / 3.1,
        ("po4_mmol", "po4_mgdl"): lambda x: x * 3.1,
    }
    
    key = (from_unit, to_unit)
    if key in conversions:
        return conversions[key](value)
    return value


def detect_albumin_unit(value: float) -> str:
    """
    Detect albumin unit based on value range.
    
    g/dL: typically 2-5
    g/L: typically 20-50
    """
    if value is None:
        return "unknown"
    if value < 10:
        return "g/dL"
    return "g/L"


def get_param_label(param: str) -> str:
    labels = {
        "ph": "pH",
        "pco2": "pCO₂",
        "na": "Na⁺",
        "cl": "Cl⁻",
        "k": "K⁺",
        "lactate": "Laktat",
        "be": "BE",
        "hco3": "HCO₃⁻",
    }
    return labels.get(param, param)


def assess_severity(param: str, value: float) -> Tuple[str, Optional[str]]:
    """
    Assess severity level and return (severity, critical_message).
    
    Severity levels: "normal", "mild", "moderate", "severe", "critical"
    
    Returns:
        Tuple of (severity_level, critical_message_key or None)
    """
    thresholds = EXTREME_THRESHOLDS.get(param, {})
    
    if not thresholds:
        return "normal", None
    
    # Check critical levels first (highest priority)
    if "critical_low" in thresholds and value <= thresholds["critical_low"]:
        return "critical", f"{param}_critical_low"
    if "critical_high" in thresholds and value >= thresholds["critical_high"]:
        return "critical", f"{param}_critical_high"
    
    # Check severe levels
    if "low" in thresholds and value < thresholds["low"]:
        return "severe", f"{param}_severe_low"
    if "high" in thresholds and value > thresholds["high"]:
        return "severe", f"{param}_severe_high"
    
    return "normal", None


def apply_three_tier_validation(param: str, value: float, result: ValidationResult) -> None:
    """
    Apply three-tier validation for a single parameter.
    
    Tiers:
        1. PHYSIOLOGIC_LIMITS - Hard reject (is_valid = False)
        2. EXTREME_THRESHOLDS (critical) - Accept + Critical warning
        3. EXTREME_THRESHOLDS (severe) - Accept + Severe warning
    """
    limits = PHYSIOLOGIC_LIMITS.get(param)
    label = get_param_label(param)

    # Tier 1: Hard physiologic limits - REJECT
    if limits:
        min_v, max_v = limits
        if value < min_v or value > max_v:
            result.is_valid = False
            result.errors.append(
                f"{label}: {value} fizyolojik sınırların dışında ({min_v}-{max_v})"
            )
            return

    # Tier 2 & 3: Extreme thresholds - WARN with severity
    severity, message_key = assess_severity(param, value)
    
    if severity == "critical":
        # Get critical message from constants
        critical_msg = CRITICAL_MESSAGES.get(message_key, "")
        if critical_msg:
            result.warnings.insert(0, critical_msg)  # Insert at beginning (high priority)
        else:
            result.warnings.insert(0, f"⚠️ KRİTİK: {label}={value} — Hayati tehlike!")
        log_calculation_warning("critical_value", {"param": param, "value": value, "severity": "critical"})
        
    elif severity == "severe":
        severe_msg = CRITICAL_MESSAGES.get(message_key, "")
        if severe_msg:
            result.warnings.append(severe_msg)
        else:
            result.warnings.append(
                f"🔴 {label}={value} → Ciddi değer — Klinik aciliyet yüksek."
            )
        log_calculation_warning("extreme_value", {"param": param, "value": value, "severity": "severe"})


# =============================================================================
# INPUT VALIDATION
# =============================================================================

def validate_range(value: float, min_val: float, max_val: float, 
                   param_name: str) -> Tuple[bool, Optional[str]]:
    """Validate that value is within expected range"""
    if value < min_val or value > max_val:
        return False, f"{param_name}: {value} aralık dışı ({min_val}-{max_val})"
    return True, None


def validate_input_dict(data: Dict[str, Any], mode: str = "quick") -> ValidationResult:
    """
    Validate input dictionary and return normalized values.
    
    This is the main validation entry point for CSV batch processing.
    
    Args:
        data: Dictionary with input values (may have string values from CSV)
        mode: "quick" or "advanced"
    
    Returns:
        ValidationResult with normalized values and any errors/warnings
    """
    result = ValidationResult()
    normalized = {}
    
    # Required parameters
    required = ["ph", "pco2", "na", "cl"]
    
    for param in required:
        raw_value = data.get(param)
        value = sanitize_numeric(raw_value, allow_negative=(param == "be"))
        
        if value is None:
            result.is_valid = False
            result.errors.append(f"{param.upper()} değeri eksik veya geçersiz")
            continue
        
        normalized[param] = value
    
    if not result.is_valid:
        return result
    
    # Apply three-tier validation for required params
    for param in required:
        apply_three_tier_validation(param, normalized[param], result)
    
    # Optional parameters with validation
    optional_params = {
        "k": (K_MIN, K_MAX, "K⁺"),
        "ca": (CA_MIN, CA_MAX, "Ca²⁺"),
        "mg": (MG_MIN, MG_MAX, "Mg²⁺"),
        "lactate": (LACTATE_MIN, LACTATE_MAX, "Laktat"),
        "po4": (PO4_MIN, PO4_MAX, "Fosfat"),
    }

    for param, (min_v, max_v, name) in optional_params.items():
        raw_value = data.get(param)
        value = sanitize_numeric(raw_value, allow_negative=False)

        if raw_value is not None and value is None and str(raw_value).strip() != "":
            result.is_valid = False
            result.errors.append(f"{name} değeri geçersiz")
            continue

        if value is not None:
            if param in PHYSIOLOGIC_LIMITS or param in EXTREME_THRESHOLDS:
                apply_three_tier_validation(param, value, result)
            else:
                is_valid, error = validate_range(value, min_v, max_v, name)
                if not is_valid:
                    result.warnings.append(error)
                    log_calculation_warning("out_of_range", {"param": param, "value": value})
            normalized[param] = value
    
    # BE (can be negative)
    be_raw = data.get("be")
    be_value = sanitize_numeric(be_raw, allow_negative=True)
    if be_value is not None:
        is_valid, error = validate_range(be_value, BE_MIN, BE_MAX, "BE")
        if not is_valid:
            result.warnings.append(error)
        else:
            normalized["be"] = be_value
    
    # HCO3 (optional, will be calculated if missing)
    hco3_raw = data.get("hco3")
    hco3_value = sanitize_numeric(hco3_raw, allow_negative=False)
    if hco3_value is not None:
        if 5 <= hco3_value <= 50:
            normalized["hco3"] = hco3_value
        else:
            result.warnings.append(f"HCO₃: {hco3_value} aralık dışı (5-50)")
    
    # Albumin (handle unit detection)
    albumin_raw = data.get("albumin") or data.get("albumin_gl") or data.get("albumin_gdl")
    albumin_value = sanitize_numeric(albumin_raw, allow_negative=False)
    
    if albumin_value is not None:
        detected_unit = detect_albumin_unit(albumin_value)
        
        if detected_unit == "g/dL":
            # Convert to g/L
            albumin_gl = albumin_value * 10
            result.warnings.append(f"Albümin değeri g/dL olarak algılandı, g/L'ye çevrildi: {albumin_gl:.1f}")
            log_calculation_warning("unit_conversion", {"albumin_gdl": albumin_value, "albumin_gl": albumin_gl})
        else:
            albumin_gl = albumin_value
        
        if ALBUMIN_MIN_GL <= albumin_gl <= ALBUMIN_MAX_GL:
            normalized["albumin_gl"] = albumin_gl
        else:
            result.warnings.append(f"Albümin: {albumin_gl} g/L aralık dışı ({ALBUMIN_MIN_GL}-{ALBUMIN_MAX_GL})")
    
    # Base deficit flag
    is_bd = data.get("is_base_deficit", False)
    if isinstance(is_bd, str):
        is_bd = is_bd.lower() in ("true", "1", "yes", "evet", "bd")
    normalized["is_be_base_deficit"] = bool(is_bd)
    
    result.normalized_values = normalized
    return result


# =============================================================================
# CSV ROW VALIDATION
# =============================================================================

NUMERIC_FIELDS = {
    "ph", "pco2", "hco3", "na", "cl", "k", "ca", "mg",
    "lactate", "albumin", "po4", "be",
}


def parse_maybe_number(value: Any, field: str) -> Optional[float]:
    """Sanitize CSV cell content to a float if possible.

    Special handling:
    - Excel date/datetime objects are rejected (treated as None)
    - Comma decimal separators are normalized
    - Negative values are only allowed for BE
    """
    if isinstance(value, (date, datetime)):
        return None

    allow_negative = field == "be"
    return sanitize_numeric(value, allow_negative=allow_negative)


def sanitize_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return a sanitized copy of a CSV row.

    - Normalizes keys to lowercase
    - Strips surrounding whitespace from string values
    - Parses numeric fields with locale-aware decimal support
    """
    sanitized: Dict[str, Any] = {}

    for key, value in row.items():
        key_lower = key.lower() if isinstance(key, str) else key

        if key_lower in NUMERIC_FIELDS:
            sanitized[key_lower] = parse_maybe_number(value, key_lower)
        elif isinstance(value, str):
            sanitized[key_lower] = value.strip()
        else:
            sanitized[key_lower] = value

    return sanitized


@dataclass
class SwapSuspicion:
    """Na/Cl swap şüphesi analiz sonucu - KULLANICIYA ŞEFFAF BİLDİRİM İÇİN"""
    is_suspicious: bool = False
    confidence: str = "none"  # "none", "low", "medium", "high"
    reason: str = ""
    original_na: Optional[float] = None
    original_cl: Optional[float] = None
    suggested_na: Optional[float] = None  # Takas sonrası önerilen
    suggested_cl: Optional[float] = None
    user_action_required: bool = False  # True = kullanıcı karar vermeli


def analyze_na_cl_swap_suspicion(na: Optional[float], cl: Optional[float]) -> SwapSuspicion:
    """
    Na/Cl kolonlarının yer değiştirmiş olabileceğini ŞÜPHE OLARAK analiz et.
    
    ⚠️ ÖNEMLİ: Bu fonksiyon HİÇBİR ZAMAN otomatik düzeltme yapmaz.
    Sadece şüpheyi raporlar ve kullanıcının karar vermesini bekler.
    
    Kriterler (çok katı - sadece bariz durumlar):
    1. YÜKSEK GÜVEN: Na tipik Cl aralığında (95-110) VE Cl tipik Na aralığında (135-145)
    2. YÜKSEK GÜVEN: Na < 100 VE Cl > 135 VE fark > 35
    3. ORTA GÜVEN: Na < 115 VE Cl > 125 VE Cl > Na
    
    Returns:
        SwapSuspicion with analysis results
    """
    if na is None or cl is None:
        return SwapSuspicion()
    
    # Kriter 1: YÜKSEK GÜVEN - Değerler tam ters aralıklarda
    # Na tipik Cl aralığında (95-110) VE Cl tipik Na aralığında (135-145)
    na_in_cl_range = 95 <= na <= 110
    cl_in_na_range = 135 <= cl <= 145
    
    if na_in_cl_range and cl_in_na_range:
        return SwapSuspicion(
            is_suspicious=True,
            confidence="high",
            reason=(
                f"Na ({na}) tipik Cl aralığında (95-110), "
                f"Cl ({cl}) tipik Na aralığında (135-145). "
                f"Kolonlar yer değiştirmiş olabilir."
            ),
            original_na=na,
            original_cl=cl,
            suggested_na=cl,
            suggested_cl=na,
            user_action_required=True
        )
    
    # Kriter 2: YÜKSEK GÜVEN - Aşırı düşük Na + Aşırı yüksek Cl + Büyük fark
    if na < 100 and cl > 135 and (cl - na) > 35:
        return SwapSuspicion(
            is_suspicious=True,
            confidence="high",
            reason=(
                f"Na ({na}) fizyolojik olarak çok düşük, "
                f"Cl ({cl}) fizyolojik olarak çok yüksek, "
                f"fark ({cl - na:.0f}) anormal büyük. "
                f"Kolonlar yer değiştirmiş olabilir."
            ),
            original_na=na,
            original_cl=cl,
            suggested_na=cl,
            suggested_cl=na,
            user_action_required=True
        )
    
    # Kriter 3: ORTA GÜVEN - Şüpheli ama kesin değil
    if na < 115 and cl > 125 and cl > na and (cl - na) > 20:
        return SwapSuspicion(
            is_suspicious=True,
            confidence="medium",
            reason=(
                f"Na ({na}) düşük, Cl ({cl}) yüksek. "
                f"Kolon hatası olabilir ama kesin değil."
            ),
            original_na=na,
            original_cl=cl,
            suggested_na=cl,
            suggested_cl=na,
            user_action_required=True
        )
    
    # Kriter 4: DÜŞÜK GÜVEN - Sadece uyarı, aksiyon gerektirmez
    if na < cl and cl > 120:
        return SwapSuspicion(
            is_suspicious=True,
            confidence="low",
            reason=f"Na ({na}) < Cl ({cl}) - olağandışı ama mümkün.",
            original_na=na,
            original_cl=cl,
            suggested_na=cl,
            suggested_cl=na,
            user_action_required=False  # Sadece bilgi, aksiyon gerektirmez
        )
    
    return SwapSuspicion()


def validate_csv_row(row: Dict[str, Any], row_index: int) -> ValidationResult:
    """
    Validate a single CSV row.
    
    ⚠️ ÖNEMLİ: Bu fonksiyon HİÇBİR ZAMAN otomatik Na/Cl swap yapmaz.
    Şüpheli durumları raporlar ama orijinal değerleri korur.
    Kullanıcı kararı gerektiğinde bunu açıkça belirtir.
    
    Handles common CSV issues:
    - Na/Cl swap DETECTION (not correction!)
    - Comma decimal separators
    - Missing values
    - Unit inconsistencies
    """
    row = sanitize_csv_row(row)
    result = validate_input_dict(row, mode="quick")
    
    # Na/Cl swap şüphesi analizi - ASLA OTOMATİK DÜZELTME YOK
    na_val = row.get("na")
    cl_val = row.get("cl")
    swap_suspicion = analyze_na_cl_swap_suspicion(na_val, cl_val)
    
    if swap_suspicion.is_suspicious:
        if swap_suspicion.confidence == "high":
            # YÜKSEK GÜVEN: Belirgin uyarı
            result.warnings.insert(0, 
                f"⚠️ KOLON HATASI ŞÜPHESİ (Satır {row_index + 1}): "
                f"{swap_suspicion.reason} "
                f"→ Orijinal değerler korundu, düzeltme YAPILMADI. "
                f"Lütfen kontrol edin!"
            )
            log_calculation_warning(
                "swap_suspicion_high",
                {"row": row_index, "na": na_val, "cl": cl_val, "confidence": "high"}
            )
        elif swap_suspicion.confidence == "medium":
            # ORTA GÜVEN: Normal uyarı
            result.warnings.append(
                f"⚠️ Satır {row_index + 1}: {swap_suspicion.reason} "
                f"Orijinal değerler kullanıldı."
            )
            log_calculation_warning(
                "swap_suspicion_medium",
                {"row": row_index, "na": na_val, "cl": cl_val, "confidence": "medium"}
            )
        elif swap_suspicion.confidence == "low":
            # DÜŞÜK GÜVEN: Sadece bilgi
            result.warnings.append(
                f"ℹ️ Satır {row_index + 1}: {swap_suspicion.reason}"
            )
    
    if not result.is_valid:
        # Add row context to errors
        result.errors = [f"Satır {row_index + 1}: {e}" for e in result.errors]
        log_analysis_error("csv_row_validation_failed", {"row": row_index, "errors": result.errors})
        return result
    
    # Check for physiologically impossible combinations
    normalized = result.normalized_values
    ph = normalized.get("ph", 7.4)
    pco2 = normalized.get("pco2", 40)
    
    # Very low pH with very low pCO2 suggests error
    if ph < 7.0 and pco2 < 20:
        result.warnings.append(f"Satır {row_index + 1}: pH ve pCO₂ kombinasyonu olağandışı")
    
    return result


# =============================================================================
# BATCH VALIDATION
# =============================================================================

def validate_batch_input(rows: List[Dict[str, Any]]) -> Tuple[List[ValidationResult], int, int]:
    """
    Validate batch input data.
    
    Returns:
        Tuple of (validation_results, valid_count, error_count)
    """
    results = []
    valid_count = 0
    error_count = 0
    
    for i, row in enumerate(rows):
        result = validate_csv_row(row, i)
        results.append(result)
        
        if result.is_valid:
            valid_count += 1
        else:
            error_count += 1
    
    return results, valid_count, error_count


# =============================================================================
# QUICK VALIDATORS
# =============================================================================

def is_valid_ph(ph: Any) -> bool:
    """Quick check if pH is valid"""
    value = sanitize_numeric(ph)
    return value is not None and PH_MIN <= value <= PH_MAX


def is_valid_electrolyte(value: Any, min_v: float, max_v: float) -> bool:
    """Quick check if electrolyte value is valid"""
    v = sanitize_numeric(value)
    return v is not None and min_v <= v <= max_v
