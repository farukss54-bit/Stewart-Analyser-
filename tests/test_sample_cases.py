# test_sample_cases.py - Örnek vaka seti bütünlük testleri
import pytest
from constants import SAMPLE_CASES, REFERENCES, ACKNOWLEDGMENTS
from core import StewartInput, analyze_stewart


def test_references_akoglu_2024():
    assert "akoglu_2024" in REFERENCES


def test_acknowledgments_mevcut():
    assert ACKNOWLEDGMENTS is not None
    assert len(ACKNOWLEDGMENTS) > 0


def test_akoglu_vaka_sayisi():
    akoglu_cases = [k for k in SAMPLE_CASES.keys() if k.startswith('akoglu_')]
    assert len(akoglu_cases) == 5


class TestAkogluVakaYapisi:
    """Her akoglu vakasinin gerekli alanlari icerdigini dogrular."""

    @pytest.fixture(params=[k for k in SAMPLE_CASES.keys() if k.startswith('akoglu_')])
    def case_id(self, request):
        return request.param

    def test_classic_interpretation(self, case_id):
        assert "classic_interpretation" in SAMPLE_CASES[case_id]

    def test_stewart_findings(self, case_id):
        assert "stewart_findings" in SAMPLE_CASES[case_id]

    def test_values_k_and_be(self, case_id):
        values = SAMPLE_CASES[case_id]["values"]
        assert "k" in values
        assert "be" in values


class TestAkogluVakaAnalizleri:
    """Her akoglu vakasinin analyze_stewart ile basarili analiz edildigini dogrular."""

    @pytest.fixture(params=[k for k in SAMPLE_CASES.keys() if k.startswith('akoglu_')])
    def case_id(self, request):
        return request.param

    def test_analiz_gecerli(self, case_id):
        case = SAMPLE_CASES[case_id]
        inp = StewartInput(
            ph=case['values']['ph'],
            pco2=case['values']['pco2'],
            na=case['values']['na'],
            cl=case['values']['cl'],
            k=case['values'].get('k'),
            lactate=case['values'].get('lactate'),
            albumin_gl=case['values'].get('albumin_gl'),
            be=case['values'].get('be')
        )
        out, val = analyze_stewart(inp, 'quick')
        assert val.is_valid, f"{case_id} validasyon basarisiz"
