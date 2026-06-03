# test_regression.py - Comprehensive Regression Tests for Critical Fixes
"""
Test vakalari master prompt'taki kritik sorunlari kontrol eder:
1. Primer respiratuvar bozukluklar taninip tanimlanmiyor mu?
2. SIG yanlis flaglenmiyor mu?
3. Celikili ciktilar var mi?
4. Kronik respiratuvar bozukluklar dogru tanimlanmiyor mu?
5. Mikst bozukluklar dogru tanimlanmiyor mu?
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


class TestPrimerRespiratuvarBozukluklar:
    """Kategori 1: Primer respiratuvar bozukluklar"""

    def test_akut_respiratuvar_alkaloz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.60, pco2=23.0, na=140.0, cl=102.0,
                hco3=21.8, be=0.3, lactate=0.5, albumin_gl=40.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "respiratory_alkalosis"
        assert "respiratory_alkalosis" in out.dominant_disorder
        assert "respiratory_alkalosis" in out.disorder_components
        assert not _has_sig_warning(out.cds_notes)
        assert "Primer Respiratuvar" in out.headline.dominant_mechanism

    def test_akut_respiratuvar_asidoz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.29, pco2=55.0, na=140.0, cl=102.0,
                hco3=25.8, be=0.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "respiratory_acidosis"
        assert "respiratory_acidosis" in out.dominant_disorder
        assert "respiratory_acidosis" in out.disorder_components
        assert not _has_sig_warning(out.cds_notes)

    def test_kronik_respiratuvar_asidoz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.35, pco2=65.0, na=140.0, cl=98.0,
                hco3=35.0, be=8.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "mixed_disorder"
        assert not _has_sig_warning(out.cds_notes)
        assert "respiratory_acidosis" in out.disorder_components

    def test_kronik_resp_asidoz_plus_met_asidoz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.25, pco2=60.0, na=140.0, cl=110.0,
                hco3=26.0, be=-3.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "mixed_disorder"
        assert not _has_sig_warning(out.cds_notes)
        assert "respiratory_acidosis" in out.disorder_components
        assert "hyperchloremic_acidosis" in out.disorder_components


class TestPrimerMetabolikBozukluklar:
    """Kategori 2: Primer metabolik bozukluklar"""

    def test_laktik_asidoz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.33, pco2=30.0, na=140.0, cl=102.0,
                hco3=20.0, be=-4.7, lactate=6.6, albumin_gl=40.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "lactic_acidosis"
        assert not _has_sig_warning(out.cds_notes)
        assert out.mechanism_analysis.dominant_mechanism is not None
        assert "laktat" in out.mechanism_analysis.dominant_mechanism.name.lower()

    def test_metabolik_alkaloz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.52, pco2=48.0, na=138.0, cl=88.0,
                hco3=38.0, be=12.0, k=2.8, lactate=1.5, albumin_gl=44.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "hypochloremic_alkalosis"
        assert not _has_sig_warning(out.cds_notes)
        assert "hypochloremic_alkalosis" in out.disorder_components


class TestMikstBozukluklar:
    """Kategori 3: Mikst bozukluklar"""

    def test_met_alkaloz_plus_resp_asidoz(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.40, pco2=60.0, na=138.0, cl=90.0,
                hco3=36.0, be=10.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "mixed_disorder"
        assert not _has_sig_warning(out.cds_notes)
        assert "respiratory_acidosis" in out.disorder_components
        assert "hypochloremic_alkalosis" in out.disorder_components

    def test_met_alkaloz_plus_uygun_kompansasyon(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.50, pco2=50.0, na=138.0, cl=88.0,
                hco3=38.0, be=12.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "hypochloremic_alkalosis"
        assert not _has_sig_warning(out.cds_notes)

    def test_triple_disorder(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.38, pco2=55.0, na=140.0, cl=105.0,
                hco3=32.0, be=-5.0, lactate=3.0, albumin_gl=25.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "mixed_disorder"
        assert not _has_sig_warning(out.cds_notes)
        assert "respiratory_acidosis" in out.disorder_components

    def test_nagma_plus_hagma(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.25, pco2=28.0, na=140.0, cl=110.0,
                hco3=16.0, be=-12.0, lactate=1.5, albumin_gl=40.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "hyperchloremic_acidosis"
        assert not _has_sig_warning(out.cds_notes)
        assert "hyperchloremic_acidosis" in out.disorder_components


class TestSIGYorumlamaKurallari:
    """Kategori 4: SIG yorumlama kurallari"""

    def test_sig_pozitif_ama_be_normal(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.38, pco2=40.0, na=140.0, cl=102.0,
                hco3=24.0, be=1.0, albumin_gl=40.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "normal"
        assert not _has_sig_warning(out.cds_notes)

    def test_sig_plus_yuksek_laktat(self):
        out, val = analyze_stewart(
            StewartInput(
                ph=7.28, pco2=30.0, na=140.0, cl=100.0,
                hco3=18.0, be=-8.0, lactate=5.5, albumin_gl=40.0
            ),
            'quick'
        )
        assert out.dominant_disorder == "lactic_acidosis"
        assert not _has_sig_warning(out.cds_notes)
        assert out.mechanism_analysis.dominant_mechanism is not None
        assert "laktat" in out.mechanism_analysis.dominant_mechanism.name.lower()

    def test_sig_uyarisi_gercekten_var(self):
        """SIG > 2, BE negatif, laktat normal -> ölçülmemiş anyon uyarisi gelmeli"""
        out, val = analyze_stewart(
            StewartInput(
                ph=7.20, pco2=30.0, na=140.0, cl=105.0,
                k=4.0, ca=2.3, mg=0.9,
                lactate=1.0, albumin_gl=40.0
            ),
            'advanced'
        )
        assert out.sig is not None
        assert out.sig > 2
        assert _has_sig_warning(out.cds_notes)
