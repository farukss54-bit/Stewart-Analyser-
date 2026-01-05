# test_core.py
# Stewart Asit-Baz Analizi - Unit Tests
# pytest ile çalıştır: pytest test_core.py -v

import pytest
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    StewartInput, StewartOutput, ValidationResult, SIDValues,
    validate_input, analyze_stewart,
    calculate_hco3, calculate_be,
    calculate_sid_simple, calculate_sid_basic, calculate_sid_full, calculate_all_sids,
    calculate_sid_effective, calculate_sig, assess_sig_reliability,
    calculate_atot, calculate_anion_gap, calculate_corrected_anion_gap,
    calculate_sid_effect, calculate_albumin_effect, calculate_lactate_effect, calculate_residual_effect,
    calculate_expected_pco2_metabolic_acidosis, calculate_expected_pco2_metabolic_alkalosis,
    calculate_expected_hco3_respiratory_acidosis, calculate_expected_hco3_respiratory_alkalosis,
    check_hco3_consistency, check_be_consistency,
    interpret_ph, interpret_pco2, interpret_sid_effect, interpret_albumin_effect,
    interpret_lactate, interpret_sig, interpret_residual,
    determine_dominant_disorder,
    output_to_dict, dict_to_input
)
from constants import (
    PH_NORMAL_LOW, PH_NORMAL_HIGH,
    PCO2_NORMAL_LOW, PCO2_NORMAL_HIGH,
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL,
    SIG_THRESHOLD, CLINICAL_SIGNIFICANCE_THRESHOLD,
    LACTATE_THRESHOLD, HCO3_MISMATCH_THRESHOLD, BE_MISMATCH_THRESHOLD
)


# === TEMEL HESAPLAMA TESTLERİ ===

class TestBasicCalculations:
    """Temel hesaplama fonksiyonları testleri"""
    
    def test_calculate_hco3_normal(self):
        """Normal pH ve pCO2 için HCO3 hesabı"""
        hco3 = calculate_hco3(ph=7.40, pco2=40)
        assert 23 <= hco3 <= 25
    
    def test_calculate_hco3_acidosis(self):
        """Asidoz durumunda HCO3 hesabı"""
        hco3 = calculate_hco3(ph=7.20, pco2=30)
        assert hco3 < 20
    
    def test_calculate_hco3_alkalosis(self):
        """Alkaloz durumunda HCO3 hesabı"""
        hco3 = calculate_hco3(ph=7.50, pco2=40)
        assert hco3 > 26
    
    def test_calculate_be_normal(self):
        """Normal değerler için BE hesabı"""
        be = calculate_be(ph=7.40, hco3=24)
        assert -2 <= be <= 2
    
    def test_calculate_be_acidosis(self):
        """Metabolik asidoz için BE hesabı"""
        be = calculate_be(ph=7.30, hco3=18)
        assert be < -2
    
    def test_calculate_be_alkalosis(self):
        """Metabolik alkaloz için BE hesabı"""
        be = calculate_be(ph=7.50, hco3=30)
        assert be > 2


class TestConsistencyChecks:
    """Tutarlılık kontrol testleri"""
    
    def test_hco3_consistent(self):
        """HCO3 tutarlı"""
        is_consistent, diff = check_hco3_consistency(24.0, 24.5)
        assert is_consistent
        assert diff <= HCO3_MISMATCH_THRESHOLD
    
    def test_hco3_inconsistent(self):
        """HCO3 tutarsız"""
        is_consistent, diff = check_hco3_consistency(24.0, 28.0)
        assert not is_consistent
        assert diff > HCO3_MISMATCH_THRESHOLD
    
    def test_be_consistent(self):
        """BE tutarlı"""
        is_consistent, diff = check_be_consistency(0.0, 1.0)
        assert is_consistent
    
    def test_be_inconsistent(self):
        """BE tutarsız"""
        is_consistent, diff = check_be_consistency(0.0, 5.0)
        assert not is_consistent


class TestThreeLayerSID:
    """3 katmanlı SID testleri"""
    
    def test_sid_simple(self):
        """SID simple hesabı"""
        sid = calculate_sid_simple(na=140, cl=102)
        assert sid == 38
    
    def test_sid_basic_with_lactate(self):
        """SID basic - laktat var"""
        sid, status = calculate_sid_basic(na=140, cl=100, lactate=2)
        assert sid == 38  # 140 - 100 - 2
        assert status == "measured"
    
    def test_sid_basic_without_lactate(self):
        """SID basic - laktat yok"""
        sid, status = calculate_sid_basic(na=140, cl=100, lactate=None)
        assert sid is None
        assert status == "lactate_missing"
    
    def test_sid_full_complete(self):
        """SID full - tam veri"""
        sid, status, missing = calculate_sid_full(
            na=140, cl=100, k=4, ca=1.25, mg=0.5, lactate=1
        )
        assert status == "complete"
        assert len(missing) == 0
        # (140 + 4 + 1.25 + 0.5) - (100 + 1) = 44.75
        assert 44 <= sid <= 46
    
    def test_sid_full_partial(self):
        """SID full - kısmi veri"""
        sid, status, missing = calculate_sid_full(
            na=140, cl=100, k=4, ca=None, mg=None, lactate=1
        )
        assert status == "partial"
        assert "Ca²⁺" in missing
        assert "Mg²⁺" in missing
    
    def test_calculate_all_sids(self):
        """Tüm SID'leri hesapla"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            k=4, ca=1.25, mg=0.5, lactate=1
        )
        sid_values = calculate_all_sids(inp)
        
        assert sid_values.sid_simple == 40  # Na - Cl
        assert sid_values.sid_basic == 39   # Na - Cl - Lac
        assert sid_values.sid_full is not None


class TestSIGReliability:
    """SIG güvenilirlik testleri"""
    
    def test_sig_reliable(self):
        """Tam veri - güvenilir SIG"""
        reliability, warnings = assess_sig_reliability(
            lactate=1, ca=1.25, mg=0.5, albumin_gl=40
        )
        assert reliability == "reliable"
        assert len(warnings) == 0
    
    def test_sig_no_lactate(self):
        """Laktat yok - underestimated"""
        reliability, warnings = assess_sig_reliability(
            lactate=None, ca=1.25, mg=0.5, albumin_gl=40
        )
        assert reliability == "underestimated"
        assert len(warnings) > 0
    
    def test_sig_no_albumin(self):
        """Albümin yok - unreliable"""
        reliability, warnings = assess_sig_reliability(
            lactate=1, ca=1.25, mg=0.5, albumin_gl=None
        )
        assert reliability == "unreliable"
    
    def test_sig_no_ca_mg(self):
        """Ca/Mg yok - approximate"""
        reliability, warnings = assess_sig_reliability(
            lactate=1, ca=None, mg=None, albumin_gl=40
        )
        assert reliability == "approximate"


class TestCompensation:
    """Kompanzasyon testleri (genişletilmiş)"""
    
    def test_winters_formula(self):
        """Winter's formülü - metabolik asidoz"""
        expected = calculate_expected_pco2_metabolic_acidosis(hco3=15)
        assert 28 <= expected <= 32  # 1.5 × 15 + 8 = 30.5
    
    def test_metabolic_alkalosis_compensation(self):
        """Metabolik alkaloz kompanzasyonu"""
        expected = calculate_expected_pco2_metabolic_alkalosis(hco3=35)
        assert 42 <= expected <= 48  # 0.7 × 35 + 21 = 45.5
    
    def test_respiratory_acidosis_acute(self):
        """Akut respiratuvar asidoz"""
        expected = calculate_expected_hco3_respiratory_acidosis(pco2=60, is_chronic=False)
        # Normal 24 + 0.1 × (60-40) = 24 + 2 = 26
        assert 25 <= expected <= 27
    
    def test_respiratory_acidosis_chronic(self):
        """Kronik respiratuvar asidoz"""
        expected = calculate_expected_hco3_respiratory_acidosis(pco2=60, is_chronic=True)
        # Normal 24 + 0.35 × (60-40) = 24 + 7 = 31
        assert 30 <= expected <= 32
    
    def test_respiratory_alkalosis_acute(self):
        """Akut respiratuvar alkaloz"""
        expected = calculate_expected_hco3_respiratory_alkalosis(pco2=25, is_chronic=False)
        # Normal 24 - 0.2 × (40-25) = 24 - 3 = 21
        assert 20 <= expected <= 22
    
    def test_respiratory_alkalosis_chronic(self):
        """Kronik respiratuvar alkaloz"""
        expected = calculate_expected_hco3_respiratory_alkalosis(pco2=25, is_chronic=True)
        # Normal 24 - 0.5 × (40-25) = 24 - 7.5 = 16.5
        assert 15 <= expected <= 18


class TestDominantDisorder:
    """Dominant disorder testi"""
    
    def test_normal(self):
        """Normal durum"""
        dominant, components = determine_dominant_disorder(
            ph=7.40, pco2=40, be=0,
            sid_effect=0, albumin_effect=0, lactate=1, residual_effect=0, sig=0
        )
        assert dominant == "normal"
        assert len(components) == 0
    
    def test_lactic_acidosis(self):
        """Laktik asidoz"""
        dominant, components = determine_dominant_disorder(
            ph=7.30, pco2=30, be=-10,
            sid_effect=0, albumin_effect=0, lactate=8, residual_effect=0, sig=0
        )
        assert "lactic_acidosis" in components
    
    def test_hyperchloremic_acidosis(self):
        """Hiperkloremik asidoz"""
        dominant, components = determine_dominant_disorder(
            ph=7.28, pco2=30, be=-8,
            sid_effect=-8, albumin_effect=0, lactate=1, residual_effect=0, sig=0
        )
        assert "hyperchloremic_acidosis" in components
    
    def test_mixed_disorder(self):
        """Miks bozukluk"""
        dominant, components = determine_dominant_disorder(
            ph=7.35, pco2=50, be=-5,
            sid_effect=-5, albumin_effect=3, lactate=1, residual_effect=0, sig=0
        )
        assert len(components) >= 2


# === VALİDASYON TESTLERİ ===

class TestValidation:
    """Girdi validasyon testleri (genişletilmiş)"""
    
    def test_valid_input(self):
        """Geçerli girdi"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100)
        result = validate_input(inp)
        assert result.is_valid
    
    def test_invalid_ph(self):
        """Geçersiz pH"""
        inp = StewartInput(ph=6.5, pco2=40, na=140, cl=100)
        result = validate_input(inp)
        assert not result.is_valid
    
    def test_invalid_k(self):
        """Geçersiz K"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100, k=10)
        result = validate_input(inp)
        assert not result.is_valid
    
    def test_invalid_ca(self):
        """Geçersiz Ca"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100, ca=5)
        result = validate_input(inp)
        assert not result.is_valid
    
    def test_invalid_albumin(self):
        """Geçersiz Albümin"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100, albumin_gl=100)
        result = validate_input(inp)
        assert not result.is_valid
    
    def test_missing_params_warning(self):
        """Eksik parametre uyarısı"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100)
        result = validate_input(inp)
        assert result.is_valid
        assert len(result.warnings) > 0  # Albümin ve laktat eksik


# === KLİNİK SENARYO TESTLERİ ===

class TestClinicalScenarios:
    """Gerçekçi klinik senaryo testleri"""
    
    def test_normal_case_quick(self):
        """Normal hasta - hızlı mod"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            lactate=1.0, albumin_gl=40
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
        assert out.dominant_disorder == "normal"
    
    def test_hyperchloremic_acidosis_quick(self):
        """Hiperkloremik asidoz - hızlı mod"""
        inp = StewartInput(
            ph=7.28, pco2=30, na=138, cl=115,
            lactate=1.5, albumin_gl=40
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
        assert out.sid_effect < -CLINICAL_SIGNIFICANCE_THRESHOLD
    
    def test_lactic_acidosis_quick(self):
        """Laktik asidoz - hızlı mod"""
        inp = StewartInput(
            ph=7.25, pco2=28, na=140, cl=100,
            lactate=8, albumin_gl=40
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
        assert "lactic_acidosis" in out.disorder_components
    
    def test_hypoalbuminemia_masking(self):
        """Hipoalbüminemi maskeleyen alkaloz"""
        inp = StewartInput(
            ph=7.38, pco2=38, na=140, cl=100,
            lactate=1, albumin_gl=20
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
        assert out.albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD
    
    def test_advanced_mode_sig(self):
        """Gelişmiş mod - SIG hesabı"""
        inp = StewartInput(
            ph=7.30, pco2=30, na=140, cl=100,
            k=4.5, ca=1.2, mg=0.5, lactate=2, albumin_gl=40, po4=1.2
        )
        out, val = analyze_stewart(inp, mode="advanced")
        
        assert val.is_valid
        assert out.sig is not None
        assert out.sig_reliability == "reliable"
    
    def test_be_calculated_flag(self):
        """BE hesaplama flag'i"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            be=None  # BE girilmedi
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert "BE_CALCULATED" in out.flags
        assert out.be_source == "calculated"
    
    def test_be_mismatch_flag(self):
        """BE uyumsuzluk flag'i"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            be=10  # Uyumsuz BE
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert "BE_MISMATCH" in out.flags
    
    def test_hco3_mismatch_flag(self):
        """HCO3 uyumsuzluk flag'i"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            hco3=30  # Uyumsuz HCO3 (hesaplanan ~24)
        )
        out, val = analyze_stewart(inp, mode="quick")
        
        assert "HCO3_MISMATCH" in out.flags
    
    def test_sig_unreliable_no_albumin(self):
        """SIG güvenilmez - albümin yok"""
        inp = StewartInput(
            ph=7.30, pco2=30, na=140, cl=100,
            k=4.5, ca=1.2, mg=0.5, lactate=2,
            albumin_gl=None  # Albümin yok
        )
        out, val = analyze_stewart(inp, mode="advanced")
        
        # SIG hesaplanabilir ama güvenilir değil
        if out.sig is not None:
            assert out.sig_reliability != "reliable"


# === CSV EXPORT/IMPORT TESTLERİ ===

class TestCSVOperations:
    """CSV export/import testleri"""
    
    def test_output_to_dict_complete(self):
        """Tam output -> Dict"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            lactate=1, albumin_gl=40
        )
        out, _ = analyze_stewart(inp, mode="quick")
        
        d = output_to_dict(inp, out)
        
        # Tüm önemli alanlar mevcut olmalı
        assert "sid_simple" in d
        assert "sid_basic" in d
        assert "sid_full" in d
        assert "dominant_disorder" in d
        assert "flags" in d
        assert "missing_params" in d
        assert "assumed_params" in d
    
    def test_dict_to_input_safe_float(self):
        """Dict -> Input - NaN handling"""
        d = {
            "ph": 7.40,
            "pco2": 40,
            "na": 140,
            "cl": 100,
            "lactate": "",  # Boş string
            "albumin_gl": float('nan')  # NaN
        }
        
        inp = dict_to_input(d)
        
        assert inp.lactate is None
        assert inp.albumin_gl is None
    
    def test_roundtrip(self):
        """Input -> Output -> Dict -> Input roundtrip"""
        inp_original = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            lactate=1.5, albumin_gl=38
        )
        out, _ = analyze_stewart(inp_original, mode="quick")
        
        d = output_to_dict(inp_original, out)
        inp_restored = dict_to_input(d)
        
        assert inp_restored.ph == inp_original.ph
        assert inp_restored.na == inp_original.na


# === EDGE CASE TESTLERİ ===

class TestEdgeCases:
    """Sınır değer testleri"""
    
    def test_extreme_acidemia(self):
        """Ekstrem asidemi"""
        inp = StewartInput(ph=6.90, pco2=80, na=140, cl=100)
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
    
    def test_all_optional_missing(self):
        """Tüm opsiyonel parametreler eksik"""
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100)
        out, val = analyze_stewart(inp, mode="quick")
        
        assert val.is_valid
        assert "INCOMPLETE_DATA" in out.flags
        assert out.assumed_params == []  # Artık varsayım yok
    
    def test_no_assumptions_made(self):
        """Varsayım yapılmadığını doğrula"""
        inp = StewartInput(
            ph=7.40, pco2=40, na=140, cl=100,
            ca=None, mg=None, po4=None  # Eksik ama varsayım yok
        )
        out, val = analyze_stewart(inp, mode="advanced")
        
        assert len(out.assumed_params) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
