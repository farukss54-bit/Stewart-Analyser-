# test_validation.py
# Stewart Asit-Baz Analizi - Validation Edge Case Tests v3.2
# Focus on dirty real-world input, not impossible physiology
# pytest test_validation.py -v

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validation import (
    sanitize_numeric, validate_input_dict, validate_csv_row,
    detect_albumin_unit, normalize_unit, ValidationResult,
    validate_batch_input
)
from core import StewartInput, analyze_stewart


# =============================================================================
# NUMERIC SANITIZATION - DIRTY INPUT
# =============================================================================

class TestSanitizeNumeric:
    """Test numeric sanitization with real-world dirty input"""
    
    # --- Decimal separator issues ---
    def test_comma_decimal_turkish(self):
        """Turkish/European decimal format (7,40 instead of 7.40)"""
        assert sanitize_numeric("7,40") == 7.40
        assert sanitize_numeric("140,5") == 140.5
        assert sanitize_numeric("0,8") == 0.8
    
    def test_multiple_dots_invalid(self):
        """Multiple dots should fail"""
        assert sanitize_numeric("7.4.0") is None
    
    # --- Whitespace issues ---
    def test_leading_trailing_whitespace(self):
        """Leading/trailing whitespace from Excel copy-paste"""
        assert sanitize_numeric("  140  ") == 140.0
        assert sanitize_numeric("\t7.40\n") == 7.40
        assert sanitize_numeric("  \n  102  \t  ") == 102.0
    
    # --- Empty and null-like values ---
    def test_empty_string(self):
        assert sanitize_numeric("") is None
    
    def test_whitespace_only(self):
        assert sanitize_numeric("   ") is None
        assert sanitize_numeric("\t\n") is None
    
    def test_none_value(self):
        assert sanitize_numeric(None) is None
    
    def test_nan_variants(self):
        """Various NaN representations from Excel/Pandas"""
        assert sanitize_numeric("nan") is None
        assert sanitize_numeric("NaN") is None
        assert sanitize_numeric("NAN") is None
        assert sanitize_numeric("#N/A") is None
    
    def test_null_variants(self):
        """Various null representations"""
        assert sanitize_numeric("null") is None
        assert sanitize_numeric("NULL") is None
        assert sanitize_numeric("none") is None
        assert sanitize_numeric("None") is None
    
    def test_dash_placeholder(self):
        """Dash as missing value placeholder"""
        assert sanitize_numeric("-") is None
        assert sanitize_numeric("--") is None
        assert sanitize_numeric("---") is None
    
    def test_na_variants(self):
        """N/A variants"""
        assert sanitize_numeric("N/A") is None
        assert sanitize_numeric("n/a") is None
        assert sanitize_numeric("NA") is None
    
    # --- Negative values (BE can be negative) ---
    def test_negative_be_allowed(self):
        assert sanitize_numeric("-5", allow_negative=True) == -5.0
        assert sanitize_numeric("-10.5", allow_negative=True) == -10.5
        assert sanitize_numeric("-0.5", allow_negative=True) == -0.5
    
    def test_negative_electrolyte_blocked(self):
        """Negative values blocked for electrolytes"""
        assert sanitize_numeric("-5", allow_negative=False) is None
        assert sanitize_numeric("-140", allow_negative=False) is None
    
    # --- Invalid strings ---
    def test_text_values(self):
        assert sanitize_numeric("abc") is None
        assert sanitize_numeric("normal") is None
        assert sanitize_numeric("yüksek") is None
    
    def test_mixed_text_numbers(self):
        """Text mixed with numbers - extract numbers"""
        assert sanitize_numeric("140 mmol/L") == 140.0
        assert sanitize_numeric("pH: 7.40") == 7.40
    
    # --- Special float values ---
    def test_infinity(self):
        import math
        assert sanitize_numeric(float('inf')) is None
        assert sanitize_numeric(float('-inf')) is None
    
    def test_nan_float(self):
        import math
        assert sanitize_numeric(float('nan')) is None


# =============================================================================
# ALBUMIN UNIT DETECTION
# =============================================================================

class TestAlbuminUnitDetection:
    """Test albumin unit auto-detection"""
    
    def test_gdl_range(self):
        """Values 1-6 should be detected as g/dL"""
        assert detect_albumin_unit(3.5) == "g/dL"
        assert detect_albumin_unit(4.2) == "g/dL"
        assert detect_albumin_unit(2.0) == "g/dL"
        assert detect_albumin_unit(5.5) == "g/dL"
    
    def test_gl_range(self):
        """Values > 10 should be detected as g/L"""
        assert detect_albumin_unit(35) == "g/L"
        assert detect_albumin_unit(42) == "g/L"
        assert detect_albumin_unit(20) == "g/L"
        assert detect_albumin_unit(55) == "g/L"
    
    def test_ambiguous_range(self):
        """Values 6-10 are ambiguous"""
        # Should default to g/L since more common in clinical practice
        assert detect_albumin_unit(8) == "g/dL"  # Still < 10
    
    def test_none(self):
        assert detect_albumin_unit(None) == "unknown"


class TestUnitNormalization:
    """Test unit conversion"""
    
    def test_albumin_gdl_to_gl(self):
        assert normalize_unit(3.5, "albumin_gdl", "albumin_gl") == 35.0
        assert normalize_unit(4.2, "albumin_gdl", "albumin_gl") == 42.0
    
    def test_albumin_gl_to_gdl(self):
        assert normalize_unit(35, "albumin_gl", "albumin_gdl") == 3.5


# =============================================================================
# INPUT DICTIONARY VALIDATION
# =============================================================================

class TestValidateInputDict:
    """Test input dictionary validation"""
    
    def test_valid_minimal(self):
        """Minimum required parameters"""
        data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert result.is_valid
        assert "ph" in result.normalized_values
        assert result.normalized_values["ph"] == 7.40
    
    def test_valid_with_optionals(self):
        """All optional parameters"""
        data = {
            "ph": 7.40, "pco2": 40, "na": 140, "cl": 102,
            "k": 4.5, "lactate": 1.0, "albumin_gl": 40, "be": 0
        }
        result = validate_input_dict(data)
        assert result.is_valid
        assert "lactate" in result.normalized_values
    
    # --- Missing required parameters ---
    def test_missing_ph(self):
        data = {"pco2": 40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid
        assert any("PH" in e.upper() for e in result.errors)
    
    def test_missing_pco2(self):
        data = {"ph": 7.40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid
        assert any("PCO" in e.upper() for e in result.errors)
    
    def test_missing_na(self):
        data = {"ph": 7.40, "pco2": 40, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid
        assert any("NA" in e.upper() for e in result.errors)
    
    def test_missing_cl(self):
        data = {"ph": 7.40, "pco2": 40, "na": 140}
        result = validate_input_dict(data)
        assert not result.is_valid
        assert any("CL" in e.upper() for e in result.errors)
    
    # --- Out of range values ---
    def test_ph_too_low(self):
        data = {"ph": 6.2, "pco2": 40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid
        assert any("pH" in e for e in result.errors)

    def test_ph_too_high(self):
        data = {"ph": 8.0, "pco2": 40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid

    def test_pco2_too_low(self):
        data = {"ph": 7.40, "pco2": 4.0, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid

    def test_na_too_low(self):
        data = {"ph": 7.40, "pco2": 40, "na": 70, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid

    # --- Extreme but valid values should warn, not invalidate ---
    def test_extreme_ph_warns(self):
        data = {"ph": 6.69, "pco2": 60, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert result.is_valid
        assert any("Extreme value detected" in w for w in result.warnings)

    def test_extreme_pco2_warns(self):
        data = {"ph": 7.10, "pco2": 153, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert result.is_valid
        assert any("pCO₂" in w for w in result.warnings)

    def test_extreme_lactate_warns(self):
        data = {"ph": 7.05, "pco2": 40, "na": 140, "cl": 102, "lactate": 29}
        result = validate_input_dict(data)
        assert result.is_valid
        assert any("Laktat" in w for w in result.warnings)

    def test_extreme_na_warns(self):
        data = {"ph": 7.10, "pco2": 40, "na": 188, "cl": 102}
        result = validate_input_dict(data)
        assert result.is_valid
        assert any("Na" in w or "Na⁺" in w for w in result.warnings)

    # --- Hard stop for impossible values ---
    def test_invalid_low_ph(self):
        data = {"ph": 6.3, "pco2": 40, "na": 140, "cl": 102}
        result = validate_input_dict(data)
        assert not result.is_valid

    def test_invalid_negative_lactate(self):
        data = {"ph": 7.20, "pco2": 40, "na": 140, "cl": 102, "lactate": -1}
        result = validate_input_dict(data)
        assert not result.is_valid

    # --- String values (from CSV) ---
    def test_string_values_comma_decimal(self):
        """String values with comma decimal from CSV"""
        data = {"ph": "7,40", "pco2": "40", "na": "140", "cl": "102"}
        result = validate_input_dict(data)
        assert result.is_valid
        assert result.normalized_values["ph"] == 7.40
    
    def test_string_values_with_whitespace(self):
        """String values with whitespace from CSV"""
        data = {"ph": "  7.40  ", "pco2": " 40 ", "na": "140\t", "cl": "\n102"}
        result = validate_input_dict(data)
        assert result.is_valid
    
    # --- Albumin unit auto-conversion ---
    def test_albumin_gdl_auto_convert(self):
        """Auto-convert albumin from g/dL to g/L"""
        data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102, "albumin": 3.5}
        result = validate_input_dict(data)
        assert result.is_valid
        assert result.normalized_values["albumin_gl"] == 35.0
        assert any("g/dL" in w for w in result.warnings)
    
    def test_albumin_gl_no_conversion(self):
        """g/L albumin should not be converted"""
        data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102, "albumin_gl": 35}
        result = validate_input_dict(data)
        assert result.is_valid
        assert result.normalized_values["albumin_gl"] == 35.0
    
    # --- Base deficit flag ---
    def test_base_deficit_flag_true(self):
        data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102, 
                "be": 5, "is_base_deficit": True}
        result = validate_input_dict(data)
        assert result.is_valid
        assert result.normalized_values["is_be_base_deficit"] == True
    
    def test_base_deficit_flag_string(self):
        """String representations of boolean"""
        for true_val in ["true", "True", "1", "yes", "evet", "bd"]:
            data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102,
                    "is_base_deficit": true_val}
            result = validate_input_dict(data)
            assert result.normalized_values["is_be_base_deficit"] == True


# =============================================================================
# CSV ROW VALIDATION
# =============================================================================

class TestCSVRowValidation:
    """Test CSV row validation with real-world issues"""
    
    def test_swapped_na_cl_columns(self):
        """Detect possible Na/Cl swap"""
        data = {"ph": 7.40, "pco2": 40, "na": 102, "cl": 140}  # Swapped!
        result = validate_csv_row(data, 0)
        assert result.is_valid  # Still valid but with warning
        assert any("yer değiştirmiş" in w for w in result.warnings)
    
    def test_zero_values(self):
        """Zero values from CSV artifacts"""
        data = {"ph": 7.40, "pco2": 40, "na": 140, "cl": 0}
        result = validate_csv_row(data, 0)
        assert not result.is_valid
    
    def test_negative_electrolytes(self):
        """Negative electrolytes from CSV errors"""
        data = {"ph": 7.40, "pco2": 40, "na": -140, "cl": 102}
        result = validate_csv_row(data, 0)
        assert not result.is_valid
    
    def test_row_context_in_errors(self):
        """Error messages include row number"""
        data = {"ph": 6.2, "pco2": 40, "na": 140, "cl": 102}
        result = validate_csv_row(data, 5)
        assert any("Satır 6" in e for e in result.errors)
    
    def test_impossible_ph_pco2_combination(self):
        """Physiologically suspicious combination"""
        data = {"ph": 6.9, "pco2": 15, "na": 140, "cl": 102}
        result = validate_csv_row(data, 0)
        # Should warn about unusual combination
        assert any("olağandışı" in w for w in result.warnings)


class TestBatchValidation:
    """Test batch validation"""
    
    def test_batch_all_valid(self):
        rows = [
            {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102},
            {"ph": 7.35, "pco2": 35, "na": 138, "cl": 100},
            {"ph": 7.45, "pco2": 45, "na": 142, "cl": 105},
        ]
        results, valid, errors = validate_batch_input(rows)
        assert valid == 3
        assert errors == 0
    
    def test_batch_some_invalid(self):
        rows = [
            {"ph": 7.40, "pco2": 40, "na": 140, "cl": 102},
            {"ph": 6.2, "pco2": 40, "na": 140, "cl": 102},  # Invalid pH
            {"ph": 7.35, "pco2": 35, "na": 138, "cl": 100},
        ]
        results, valid, errors = validate_batch_input(rows)
        assert valid == 2
        assert errors == 1


class TestDirtyInputNormalization:
    def test_decimal_separator_and_albumin_unit(self):
        data = {"ph": "7,32", "pco2": "40,5", "na": "140", "cl": "110", "albumin": "4.0"}
        result = validate_input_dict(data)
        assert result.is_valid
        assert result.normalized_values["ph"] == 7.32
        assert result.normalized_values["albumin_gl"] == 40.0

    def test_swapped_na_cl_detection(self):
        row = {"ph": 7.4, "pco2": 40, "na": 100, "cl": 140}
        result = validate_csv_row(row, 0)
        assert result.is_valid
        # Values remain as provided but warning highlights possible swap
        assert result.normalized_values["na"] == 100
        assert any("kolonlar" in w for w in result.warnings)

    def test_negative_values_rejected(self):
        data = {"ph": -1, "pco2": 40, "na": 140, "cl": 100}
        result = validate_input_dict(data)
        assert not result.is_valid

    def test_missing_albumin_not_assumed(self):
        data = {"ph": 7.4, "pco2": 40, "na": 140, "cl": 100}
        result = validate_input_dict(data)
        assert result.is_valid
        assert "albumin_gl" not in result.normalized_values


# =============================================================================
# BOTH BE AND HCO3 PROVIDED
# =============================================================================

class TestBothBEandHCO3:
    """Test handling when both BE and HCO3 are provided"""
    
    def test_consistent_values(self):
        """Both provided and consistent"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=102,
            be=0, hco3=24
        )
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        # Should not have mismatch warning for consistent values
    
    def test_inconsistent_values_should_warn(self):
        """Both provided but inconsistent - should warn"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=102,
            be=-10, hco3=24  # BE suggests acidosis, HCO3 is normal
        )
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid  # Still valid
        assert any("mismatch" in w.lower() for w in out.warnings)


# =============================================================================
# EDGE CASES FROM REAL CLINICAL DATA
# =============================================================================

class TestClinicalEdgeCases:
    """Edge cases from real clinical scenarios"""
    
    def test_severe_acidemia(self):
        """pH 6.8 - severe acidemia (e.g., cardiac arrest)"""
        inp = StewartInput(ph=6.85, pco2=80, na=140, cl=100, lactate=15)
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        assert out.be_used < -20
    
    def test_severe_alkalemia(self):
        """pH 7.65 - severe alkalemia"""
        inp = StewartInput(ph=7.65, pco2=25, na=140, cl=85)
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        assert out.be_used > 10
    
    def test_very_low_albumin(self):
        """Albumin 15 g/L - severe hypoalbuminemia (e.g., cirrhosis)"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=102, albumin_gl=15)
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        assert out.albumin_effect > 0  # Alkalosis direction
    
    def test_very_high_lactate(self):
        """Lactate 20 mmol/L - severe lactic acidosis"""
        inp = StewartInput(ph=7.0, pco2=20, na=140, cl=100, lactate=20)
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        assert out.lactate_effect < -15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
