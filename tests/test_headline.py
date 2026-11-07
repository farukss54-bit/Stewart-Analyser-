"""
Başlık cümlesi, klasik karşılaştırma kapanışı ve hızlı moddaki SID uyarısı (Faruk kararları, 2026-11-06).

- Başlıkta yüzde yok; etkiler alttaki çubuklarla aynı birimde (mEq/L) yazılır.
- Baz açığının en büyük payı açıklanamayan kalan ise başlık bunu söyler (temkinli dille).
- Klasik karşılaştırmanın "Stewart ortaya çıkardı" kapanış cümlesi yazılmaz.
- Hızlı modda "SID_full yaklaşık" teknik uyarısı yerine yönlendirici cümle çıkar.
"""

import pytest

from constants import SAMPLE_CASES
from core import StewartInput, analyze_stewart

EKSI = "−"


def _case_input(case_id: str) -> StewartInput:
    v = SAMPLE_CASES[case_id]["values"]
    return StewartInput(
        ph=v["ph"], pco2=v["pco2"], na=v["na"], cl=v["cl"], k=v.get("k"),
        lactate=v.get("lactate"), albumin_gl=v.get("albumin_gl"), be=v.get("be"),
    )


def _all_headline_texts(out) -> list[str]:
    h = out.headline
    return [h.dominant_mechanism, *h.significant_mechanisms, *h.contributing_mechanisms]


class TestHeadlineUsesMeqNotPercent:
    DESIGN_EXAMPLE = StewartInput(ph=7.30, pco2=31, na=141, cl=114, lactate=2.8, albumin_gl=25)

    def test_design_example_headline(self):
        out, _ = analyze_stewart(self.DESIGN_EXAMPLE, "quick")
        assert out.headline.dominant_mechanism == f"Güçlü iyon (SID) aracılı metabolik asidoz ({EKSI}11.0 mEq/L)"
        assert out.headline.significant_mechanisms == ["Zayıf asit azalması (hipoalbüminemi) etkisi (+4.2 mEq/L)"]
        assert out.headline.contributing_mechanisms == [f"Laktat aracılı etki ({EKSI}2.8 mEq/L)"]

    @pytest.mark.parametrize("case_id", list(SAMPLE_CASES))
    def test_no_percent_in_any_sample_case_headline(self, case_id):
        out, _ = analyze_stewart(_case_input(case_id), "quick")
        assert not any("%" in t for t in _all_headline_texts(out))

    def test_alkalosis_effect_is_signed(self):
        out, _ = analyze_stewart(_case_input("vomiting"), "quick")
        assert "(+12.0 mEq/L)" in out.headline.dominant_mechanism

    def test_normal_case_is_unchanged(self):
        out, _ = analyze_stewart(_case_input("normal"), "quick")
        assert out.headline.dominant_mechanism == "Normal asit-baz dengesi"


class TestLargestShareIsTheResidual:
    def test_dka_case_headline_is_the_approved_sentence(self):
        out, _ = analyze_stewart(_case_input("dka"), "quick")
        assert out.headline.dominant_mechanism == (
            f"Baz açığının en büyük payı açıklanamayan kalan ({EKSI}11.8 mEq/L); "
            "ölçülmemiş anyonlarla uyumlu olabilir."
        )

    def test_headline_never_states_a_diagnosis(self):
        out, _ = analyze_stewart(_case_input("dka"), "quick")
        text = " ".join(_all_headline_texts(out) + [out.headline.pattern_note]).lower()
        assert "ketoasidoz" not in text and "dka" not in text

    def test_conflicting_pattern_sentence_is_dropped(self):
        """Başlık artığı söylerken "hiperkloremik güçlü iyon" paterni çelişirdi."""
        out, _ = analyze_stewart(_case_input("dka"), "quick")
        assert "Patern" not in out.headline.pattern_note

    def test_masking_note_is_kept(self):
        out, _ = analyze_stewart(_case_input("lactic_acidosis"), "quick")
        assert out.headline.pattern_note == "Karşıt yönlü metabolik etkiler birbirini kısmen maskeleyebilir."

    def test_displaced_dominant_mechanism_moves_to_significant(self):
        """Laktik asidoz vakasında laktat (−8.5) başlıktan düşmemeli, anlamlı mekanizmalara taşınmalı."""
        out, _ = analyze_stewart(_case_input("lactic_acidosis"), "quick")
        assert out.headline.dominant_mechanism.startswith("Baz açığının en büyük payı açıklanamayan kalan")
        assert any("Laktat" in t and f"{EKSI}8.5 mEq/L" in t for t in out.headline.significant_mechanisms)

    def test_opposing_effect_is_not_a_share(self):
        """Albümin +4.2 baz yönünde; baz açığının payı sayılmaz, başlık SID'i söyler."""
        out, _ = analyze_stewart(TestHeadlineUsesMeqNotPercent.DESIGN_EXAMPLE, "quick")
        assert "en büyük payı" not in out.headline.dominant_mechanism

    def test_missing_lactate_names_the_missing_value_instead_of_unmeasured_anions(self):
        """Laktat girilmediyse kalan onun payını da içerir: "ölçülmemiş anyon" denmez."""
        inp = StewartInput(ph=7.30, pco2=31, na=140, cl=104, albumin_gl=40, be=-10)
        out, _ = analyze_stewart(inp, "quick")
        assert out.headline.dominant_mechanism.endswith("girilmeyen laktat etkisini de içerir.")
        assert "ölçülmemiş" not in out.headline.dominant_mechanism

    def test_both_missing_are_named(self):
        inp = StewartInput(ph=7.30, pco2=31, na=140, cl=104, be=-10)
        out, _ = analyze_stewart(inp, "quick")
        assert "girilmeyen laktat ve albümin etkisini de içerir" in out.headline.dominant_mechanism

    def test_base_excess_wording_for_alkalosis(self):
        inp = StewartInput(ph=7.52, pco2=40, na=140, cl=104, lactate=1.0, albumin_gl=40, be=10)
        out, _ = analyze_stewart(inp, "quick")
        assert out.headline.dominant_mechanism.startswith("Baz fazlasının en büyük payı açıklanamayan kalan (+")
        assert "katyonlarla" in out.headline.dominant_mechanism

    def test_mechanism_analysis_itself_is_unchanged(self):
        """Yalnızca başlık metni değişir; mekanizma listesi ve etkiler aynı kalır."""
        out, _ = analyze_stewart(_case_input("dka"), "quick")
        assert out.residual_effect == pytest.approx(-11.8)
        assert {m.identifier for m in out.mechanism_analysis.all_mechanisms} == {"sid", "lactate"}


class TestClassicComparisonClosing:
    def test_no_closing_sentence_when_differences_exist(self):
        out, _ = analyze_stewart(_case_input("sepsis_hipoalb"), "quick")
        assert out.classic_comparison.differences
        assert out.classic_comparison.stewart_advantage == ""

    def test_neutral_sentence_stays_when_there_is_no_difference(self):
        out, _ = analyze_stewart(_case_input("normal"), "quick")
        assert not out.classic_comparison.differences
        assert out.classic_comparison.stewart_advantage == "Bu vakada klasik ve Stewart yaklaşımları benzer sonuç veriyor."


class TestQuickModeSidWarning:
    def test_quick_mode_uses_the_friendly_sentence(self):
        inp = StewartInput(ph=7.30, pco2=31, na=141, cl=114, lactate=2.8, albumin_gl=25)
        out, _ = analyze_stewart(inp, "quick")
        assert "K⁺, Ca²⁺ ve Mg²⁺ girilmedi; ileri analiz için Gelişmiş mod gerekir." in out.warnings
        assert not any("SID_full yaklaşık" in w for w in out.warnings)
        assert "SID_FULL_APPROXIMATE" in out.flags

    def test_only_the_missing_ions_are_named(self):
        inp = StewartInput(ph=7.30, pco2=31, na=141, cl=114, k=4.1, lactate=2.8, albumin_gl=25)
        out, _ = analyze_stewart(inp, "quick")
        assert "Ca²⁺ ve Mg²⁺ girilmedi; ileri analiz için Gelişmiş mod gerekir." in out.warnings

    def test_advanced_mode_keeps_the_technical_text(self):
        inp = StewartInput(ph=7.30, pco2=31, na=141, cl=114, lactate=2.8, albumin_gl=25)
        out, _ = analyze_stewart(inp, "advanced")
        assert any(w.startswith("SID_full yaklaşık: Eksik parametreler") for w in out.warnings)
        assert not any("Gelişmiş mod gerekir" in w for w in out.warnings)
