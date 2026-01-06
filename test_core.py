# test_core.py
# Stewart Asit-Baz Analizi - Unit Tests v3.0
# pytest test_core.py -v

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    StewartInput, analyze_stewart,
    calculate_hco3, calculate_be,
    calculate_sid_simple, calculate_sid_basic, calculate_sid_full,
    calculate_sig, interpret_sig_categorical,
    generate_contribution_breakdown, generate_headline,
    generate_classic_comparison, generate_cds_notes,
    determine_dominant_disorder, validate_input,
    analyze_mechanisms, classify_contribution_level, interpret_sid_direction
)
from constants import (
    SID_NORMAL_SIMPLE, SIG_THRESHOLD, CLINICAL_SIGNIFICANCE_THRESHOLD,
    LACTATE_THRESHOLD, SAMPLE_CASES
)


class TestBasicCalculations:
    def test_hco3_normal(self):
        assert 23 <= calculate_hco3(7.40, 40) <= 25
    
    def test_be_normal(self):
        assert -2 <= calculate_be(7.40, 24) <= 2
    
    def test_sid_simple(self):
        assert calculate_sid_simple(140, 102) == 38


class TestSIDCalculations:
    def test_sid_basic_with_lactate(self):
        sid, status = calculate_sid_basic(140, 100, 2)
        assert sid == 38
        assert status == "measured"
    
    def test_sid_basic_no_lactate(self):
        sid, status = calculate_sid_basic(140, 100, None)
        assert sid is None
        assert status == "lactate_missing"
    
    def test_sid_full_complete(self):
        sid, status, missing = calculate_sid_full(140, 100, 4, 1.25, 0.5, 1)
        assert status == "complete"
        assert len(missing) == 0


class TestSIGInterpretation:
    def test_sig_positive(self):
        interp = interpret_sig_categorical(5.0)
        assert "anyon" in interp.lower()
    
    def test_sig_negative(self):
        interp = interpret_sig_categorical(-3.0)
        assert "katyon" in interp.lower() or "nadir" in interp.lower()
    
    def test_sig_normal(self):
        interp = interpret_sig_categorical(0.5)
        assert "normal" in interp.lower()


class TestContributionBreakdown:
    def test_acidosis_contributors(self):
        contrib = generate_contribution_breakdown(
            sid_effect=-5, albumin_effect=0, lactate_effect=-3,
            residual_effect=-2, pco2=40, be=-10
        )
        assert len(contrib.acidosis_contributors) >= 2
    
    def test_alkalosis_contributors(self):
        contrib = generate_contribution_breakdown(
            sid_effect=0, albumin_effect=4, lactate_effect=0,
            residual_effect=0, pco2=40, be=4
        )
        assert len(contrib.alkalosis_contributors) >= 1
    
    def test_mixed_effects(self):
        contrib = generate_contribution_breakdown(
            sid_effect=-5, albumin_effect=4, lactate_effect=-2,
            residual_effect=0, pco2=40, be=-3
        )
        assert len(contrib.acidosis_contributors) > 0
        assert len(contrib.alkalosis_contributors) > 0
        assert "karşıt" in contrib.summary.lower()


class TestHeadlineGeneration:
    def test_mechanism_based_headline(self):
        """Test that headline is mechanism-based, not presence-based"""
        # Case: BE = -10, but SID effect is dominant
        from core import analyze_mechanisms, generate_headline, MechanismAnalysis
        
        mechanism = analyze_mechanisms(
            be=-10, sid_effect=-8, albumin_effect=2, lactate_effect=-2,
            residual_effect=-2, sig=None, pco2=30, compensation_status="Uygun kompanzasyon"
        )
        
        headline = generate_headline(mechanism, 7.28, 30, -10)
        
        # Should identify SID as dominant (80% contribution), not lactate
        assert "SID" in headline.dominant_mechanism or "Güçlü iyon" in headline.dominant_mechanism
        assert "Laktik asidoz" not in headline.dominant_mechanism  # Should NOT label as "lactic acidosis"
    
    def test_lactate_contribution_levels(self):
        """Test lactate classification by contribution size"""
        from core import classify_contribution_level
        
        # <25% = contributing
        assert classify_contribution_level(20) == "contributing"
        # 25-50% = significant
        assert classify_contribution_level(35) == "significant"
        # >50% = dominant
        assert classify_contribution_level(60) == "dominant"


class TestMechanismAnalysis:
    def test_contribution_percent_calculation(self):
        """Test contribution percentage calculation"""
        from core import calculate_contribution_percent
        
        # SID effect -8 mEq/L out of BE -10 = 80%
        assert calculate_contribution_percent(-8, -10) == 80.0
        
        # Lactate -2 mEq/L out of BE -10 = 20%
        assert calculate_contribution_percent(-2, -10) == 20.0
    
    def test_sid_interpretation(self):
        """Test SID direction interpretation"""
        # Low SID = acidosis direction
        interp = interpret_sid_direction(32, "simple")
        assert "asidoz" in interp.lower()
        
        # High SID = alkalosis direction
        interp = interpret_sid_direction(46, "simple")
        assert "alkaloz" in interp.lower()
        
        # Normal SID = neutral
        interp = interpret_sid_direction(38, "simple")
        assert "normal" in interp.lower() or "nötr" in interp.lower()
    
    def test_mechanism_analysis_non_diagnostic(self):
        """Test that mechanism analysis uses non-diagnostic language"""
        mechanism = analyze_mechanisms(
            be=-10, sid_effect=-5, albumin_effect=0, lactate_effect=-3,
            residual_effect=-2, sig=3, pco2=30, compensation_status=""
        )
        
        # Should NOT contain diagnostic terms like "ketoasidoz"
        assert "ketoasidoz" not in mechanism.pattern_description.lower()
        
        # Should contain physiology-focused language
        if mechanism.dominant_mechanism:
            assert "aracılı" in mechanism.dominant_mechanism.description.lower()


class TestClassicComparison:
    def test_sid_low_hco3_normal(self):
        comparison = generate_classic_comparison(
            hco3=24, be=0, sid_effect=-5, albumin_gl=40,
            albumin_effect=0, anion_gap=12, anion_gap_corrected=12, sig=0
        )
        assert len(comparison.differences) > 0
    
    def test_albumin_masking(self):
        comparison = generate_classic_comparison(
            hco3=22, be=-2, sid_effect=-3, albumin_gl=25,
            albumin_effect=4, anion_gap=12, anion_gap_corrected=16, sig=2
        )
        assert len(comparison.missed_by_classic) > 0


class TestCDSNotes:
    def test_sid_low_note(self):
        notes = generate_cds_notes(
            sid_simple=32, sid_effect=-6, sig=None, albumin_gl=40,
            lactate=1, ph=7.30, be=-6, hco3=18, na=140, cl=108
        )
        assert any(n.category == "A" for n in notes)
    
    def test_albumin_low_note(self):
        notes = generate_cds_notes(
            sid_simple=38, sid_effect=0, sig=None, albumin_gl=25,
            lactate=1, ph=7.40, be=0, hco3=24, na=140, cl=102
        )
        assert any("albümin" in n.note.lower() for n in notes)
    
    def test_masking_pattern_note(self):
        notes = generate_cds_notes(
            sid_simple=32, sid_effect=-6, sig=None, albumin_gl=None,
            lactate=None, ph=7.38, be=-2, hco3=22, na=140, cl=108
        )
        # Normal pH + düşük SID = maskelenme paterni
        assert any(n.category == "B" for n in notes)


class TestSampleCases:
    def test_all_cases_valid(self):
        for case_id, case in SAMPLE_CASES.items():
            inp = StewartInput(
                ph=case["values"]["ph"],
                pco2=case["values"]["pco2"],
                na=case["values"]["na"],
                cl=case["values"]["cl"],
                k=case["values"].get("k"),
                lactate=case["values"].get("lactate"),
                albumin_gl=case["values"].get("albumin_gl"),
                be=case["values"].get("be")
            )
            out, val = analyze_stewart(inp, "quick")
            assert val.is_valid, f"Case {case_id} failed validation"
    
    def test_sepsis_case_has_masking(self):
        case = SAMPLE_CASES["sepsis_hipoalb"]
        inp = StewartInput(
            ph=case["values"]["ph"], pco2=case["values"]["pco2"],
            na=case["values"]["na"], cl=case["values"]["cl"],
            lactate=case["values"].get("lactate"),
            albumin_gl=case["values"].get("albumin_gl"),
            be=case["values"].get("be")
        )
        out, _ = analyze_stewart(inp, "quick")
        # Hipoalbüminemi etkisi olmalı
        assert out.albumin_effect is not None
        assert out.albumin_effect > CLINICAL_SIGNIFICANCE_THRESHOLD


class TestFullAnalysis:
    def test_normal_case(self):
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=102, lactate=1, albumin_gl=40)
        out, val = analyze_stewart(inp, "quick")
        assert val.is_valid
        assert out.headline.dominant_mechanism == "Normal asit-baz dengesi"
    
    def test_contributions_present(self):
        inp = StewartInput(ph=7.30, pco2=30, na=138, cl=110, lactate=3, albumin_gl=25)
        out, val = analyze_stewart(inp, "quick")
        assert out.contribution is not None
        assert out.contribution.net_metabolic != 0
    
    def test_cds_notes_generated(self):
        inp = StewartInput(ph=7.28, pco2=28, na=140, cl=115, lactate=2, albumin_gl=30)
        out, val = analyze_stewart(inp, "quick")
        assert len(out.cds_notes) > 0
    
    def test_classic_comparison_generated(self):
        inp = StewartInput(ph=7.38, pco2=38, na=140, cl=108, lactate=2, albumin_gl=25)
        out, val = analyze_stewart(inp, "quick")
        assert out.classic_comparison is not None


class TestValidation:
    def test_invalid_ph(self):
        inp = StewartInput(ph=6.5, pco2=40, na=140, cl=100)
        val = validate_input(inp)
        assert not val.is_valid
    
    def test_valid_with_optional_missing(self):
        inp = StewartInput(ph=7.40, pco2=40, na=140, cl=100)
        val = validate_input(inp)
        assert val.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
