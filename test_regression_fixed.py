# test_regression_fixed.py - Regression Tests for Critical Fixes
"""
Test vakalari master prompt'taki kritik sorunlari kontrol eder:
1. Primer respiratuvar bozukluklar taniniyor mu?
2. SIG yanlis flaglenmiyor mu?
3. Celiskili ciktilar var mi?
"""

import sys
sys.path.insert(0, '.')

import pytest
from core import (
    StewartInput,
    analyze_stewart,
    _RESP_STATUS_MAP,
    _PRIMARY_RESP_HEADLINE,
)
from constants import SAMPLE_CASES


def _has_sig_warning(cds_notes):
    """CDS notlari icinde SIG/ölçülmemiş anyon uyarisi var mi?"""
    return any(
        n.category == "A" and "ölçülmemiş anyon" in n.note.lower()
        for n in cds_notes
    )


class TestVaka1AkutRespiratuvarAlkaloz:
    """Vaka 1: Akut Respiratuvar Alkaloz"""

    @pytest.fixture
    def out(self):
        inp = StewartInput(
            ph=7.60, pco2=23.0, na=140.0, cl=102.0,
            hco3=21.8, be=0.3, lactate=0.5, albumin_gl=40.0
        )
        out, _ = analyze_stewart(inp, 'quick')
        return out

    def test_respiratuvar_alkaloz_taninir(self, out):
        assert "respiratory_alkalosis" in out.dominant_disorder.lower()

    def test_headline_respiratuvar_alkaloz(self, out):
        assert "primer respiratuvar" in out.headline.dominant_mechanism.lower()

    def test_sig_uyarisi_yok(self, out):
        assert not _has_sig_warning(out.cds_notes)


class TestVaka2IzoleRespiratuvarAsidoz:
    """Vaka 2: Izole Respiratuvar Asidoz"""

    @pytest.fixture
    def out(self):
        inp = StewartInput(
            ph=7.29, pco2=55.0, na=140.0, cl=102.0,
            hco3=25.8, be=0.0
        )
        out, _ = analyze_stewart(inp, 'quick')
        return out

    def test_respiratuvar_asidoz_taninir(self, out):
        assert "respiratory_acidosis" in out.dominant_disorder.lower()

    def test_sig_uyarisi_yok(self, out):
        assert not _has_sig_warning(out.cds_notes)


class TestVaka3LaktikAsidoz:
    """Vaka 3: Laktik Asidoz - Laktat varsa SIG yorumlanmamali"""

    @pytest.fixture
    def out(self):
        inp = StewartInput(
            ph=7.33, pco2=30.0, na=140.0, cl=102.0,
            hco3=20.0, be=-4.7, lactate=6.6, albumin_gl=40.0
        )
        out, _ = analyze_stewart(inp, 'quick')
        return out

    def test_laktat_dominant(self, out):
        assert out.mechanism_analysis.dominant_mechanism is not None
        assert "laktat" in out.mechanism_analysis.dominant_mechanism.name.lower()

    def test_sig_uyarisi_yok(self, out):
        assert not _has_sig_warning(out.cds_notes)


class TestRespiratoryVerdictCompensation:
    """Solunumsal verdict'in comp_status ile tutarlılığı (master fix)."""

    @staticmethod
    def _analyze(**kwargs):
        inp = StewartInput(**kwargs)
        mode = "advanced" if kwargs.get("ca") is not None else "quick"
        out, _ = analyze_stewart(inp, mode)
        return out

    def test_vaka_a_primer_respiratuvar_asidoz_kompense(self):
        out = self._analyze(
            ph=7.28,
            pco2=68.0,
            na=140.0,
            cl=98.0,
            hco3=30.9,
            be=4.4,
            k=4.5,
            lactate=1.0,
            albumin_gl=36.0,
            ca=0.50,
            mg=0.30,
            po4=0.30,
        )
        assert out.compensation_status in _PRIMARY_RESP_HEADLINE
        assert out.headline.respiratory_status == "Primer respiratuvar asidoz mevcut"
        assert "respiratuvar asidoz" in out.headline.dominant_mechanism.lower()
        assert "metabolik alkaloz" not in out.headline.dominant_mechanism.lower()

    def test_vaka_b_metabolik_asidoz_ek_respiratuvar_asidoz(self):
        out = self._analyze(
            ph=7.10,
            pco2=35.0,
            na=146.0,
            cl=129.0,
            hco3=10.5,
            be=-17.0,
            k=3.2,
            lactate=4.9,
            albumin_gl=38.0,
        )
        assert out.headline.respiratory_status == "Eklenmiş respiratuvar asidoz bileşeni"
        assert out.headline.respiratory_status != "Solunumsal bileşen normal"
        assert "asidoz" in out.headline.dominant_mechanism.lower()

    def test_all_sample_cases_resp_status_consistency(self):
        for key, case in SAMPLE_CASES.items():
            inp = StewartInput(**case["values"])
            out, _ = analyze_stewart(inp, "quick")
            assert out.mechanism_analysis is not None, f"{key}: mechanism_analysis None"
            expected = _RESP_STATUS_MAP[out.compensation_status]
            assert out.mechanism_analysis.respiratory_status == expected, (
                f"{key}: resp_status={out.mechanism_analysis.respiratory_status!r} "
                f"expected {expected!r} for comp_status={out.compensation_status!r}"
            )
            if out.compensation_status in _PRIMARY_RESP_HEADLINE:
                assert out.headline.dominant_mechanism.lower().startswith(
                    "primer respiratuvar"
                ), (
                    f"{key}: primer respiratuvar manşeti bekleniyordu, "
                    f"got {out.headline.dominant_mechanism!r}"
                )
            else:
                assert not out.headline.dominant_mechanism.lower().startswith(
                    "primer respiratuvar"
                ), (
                    f"{key}: beklenmeyen primer respiratuvar manşeti: "
                    f"{out.headline.dominant_mechanism!r}"
                )
