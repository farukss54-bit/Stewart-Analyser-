# test_regression.py - Comprehensive Regression Tests for Critical Fixes
"""
Test vakalari master prompt'taki kritik sorunlari kontrol eder:
1. Primer respiratuvar bozukluklar taninip tanimlanmiyor mu?
2. SIG yanlis flaglenmiyor mu?
3. Celikili ciktilar var mi?
4. Kronik respiratuvar bozukluklar dogru tanimlanmiyor mu?
5. Mikst bozukluklar dogru tanimlanmiyor mu?
"""

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
        assert "primer respiratuvar" in out.headline.dominant_mechanism.lower()

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
        assert out.compensation_code in _PRIMARY_RESP_HEADLINE
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
            expected = _RESP_STATUS_MAP[out.compensation_code]
            assert out.mechanism_analysis.respiratory_status == expected, (
                f"{key}: resp_status={out.mechanism_analysis.respiratory_status!r} "
                f"expected {expected!r} for compensation_code={out.compensation_code!r}"
            )
            if out.compensation_code in _PRIMARY_RESP_HEADLINE:
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
