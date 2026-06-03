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
from core import StewartInput, analyze_stewart


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
        assert "Primer Respiratuvar" in out.headline.dominant_mechanism

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
