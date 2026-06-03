from constants import SAMPLE_CASES, ACKNOWLEDGMENTS
from core import StewartInput, analyze_stewart


def test_acknowledgments_var():
    assert ACKNOWLEDGMENTS is not None


def test_akoglu_vaka_sayisi():
    akoglu_vakalari = [k for k in SAMPLE_CASES.keys() if k.startswith("akoglu_")]
    assert len(akoglu_vakalari) == 5


def test_akoglu_triple_analiz():
    case = SAMPLE_CASES["akoglu_triple"]
    inp = StewartInput(
        ph=7.48, pco2=60.2, na=132, cl=76,
        k=3.8, lactate=1.9, albumin_gl=18, be=7.6
    )
    out, val = analyze_stewart(inp, "quick")
    assert val.is_valid
    assert "classic_interpretation" in case
    assert "stewart_findings" in case
