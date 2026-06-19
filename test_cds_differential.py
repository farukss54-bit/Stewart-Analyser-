"""test_cds_differential.py

Deterministik CDS diferansiyel modülünün birim testleri.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from cds_differential import (
    DIFFERENTIAL_KNOWLEDGE,
    VERIFIED_REFS,
    evaluate_differentials,
)
from constants import (
    CLINICAL_SIGNIFICANCE_THRESHOLD,
    LACTATE_THRESHOLD,
    SAMPLE_CASES,
    SID_HIGH_THRESHOLD,
    SID_LOW_THRESHOLD,
)


@dataclass
class MockCoreOutput:
    """StewartOutput'un minimal mock'u — yalnızca trigger için gerekli alanlar."""

    dominant_disorder: Optional[str] = None
    disorder_components: List[str] = field(default_factory=list)
    anion_gap: float = 0.0
    anion_gap_corrected: Optional[float] = None
    sig: Optional[float] = None
    lactate_effect: Optional[float] = None
    albumin_effect: Optional[float] = None
    cl_na_ratio: float = 0.0
    be_used: float = 0.0


class TestDifferentialMatching:
    def test_respiratory_acidosis_matches(self):
        out = MockCoreOutput(
            dominant_disorder="respiratory_acidosis",
            disorder_components=["respiratory_acidosis"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "respiratory_acidosis_etiology" in keys

    def test_respiratory_acidosis_in_mixed_disorder(self):
        out = MockCoreOutput(
            dominant_disorder="mixed_disorder",
            disorder_components=["respiratory_acidosis", "metabolic_acidosis"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "respiratory_acidosis_etiology" in keys

    def test_respiratory_alkalosis_matches(self):
        out = MockCoreOutput(
            dominant_disorder="respiratory_alkalosis",
            disorder_components=["respiratory_alkalosis"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "respiratory_alkalosis_etiology" in keys

    def test_metabolic_alkalosis_matches(self):
        out = MockCoreOutput(
            disorder_components=["hypochloremic_alkalosis"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "metabolic_alkalosis_subtypes" in keys
        entry = next(r for r in evaluate_differentials(out) if r["key"] == "metabolic_alkalosis_subtypes")
        assert len(entry["suggested_tests"]) == 1
        assert "İdrar klorürü" in entry["suggested_tests"][0]["consider"]

    def test_nagma_matches(self):
        out = MockCoreOutput(
            disorder_components=["hyperchloremic_acidosis"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "nagma_pattern" in keys
        assert "hagma_cat_mud_piles" not in keys

    def test_nagma_suggested_tests_present(self):
        out = MockCoreOutput(
            disorder_components=["hyperchloremic_acidosis"],
        )
        entry = next(r for r in evaluate_differentials(out) if r["key"] == "nagma_pattern")
        assert len(entry["suggested_tests"]) == 2
        texts = " ".join(str(t) for t in entry["suggested_tests"])
        assert "İdrar anyon gap" in texts
        assert "İdrar pH" in texts

    def test_hagma_matches(self):
        out = MockCoreOutput(
            disorder_components=["hagma"],
        )
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "hagma_cat_mud_piles" in keys
        assert "osmol_gap_toxic_alcohol" in keys
        assert "nagma_pattern" not in keys

    def test_hagma_cat_mud_piles_content(self):
        out = MockCoreOutput(
            disorder_components=["hagma"],
        )
        entry = next(r for r in evaluate_differentials(out) if r["key"] == "hagma_cat_mud_piles")
        diffs = "\n".join(entry["differentials"])
        assert "Methanol" in diffs
        assert "Diabetic ketoacidosis" in diffs
        assert "Lactic acidosis" in diffs

    def test_lactic_acidosis_matches_high_lactate(self):
        out = MockCoreOutput(lactate_effect=-(LACTATE_THRESHOLD + 0.5))
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "lactic_acidosis_classification" in keys

    def test_lactic_acidosis_does_not_match_low_lactate(self):
        out = MockCoreOutput(lactate_effect=-(LACTATE_THRESHOLD - 0.5))
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "lactic_acidosis_classification" not in keys

    def test_normal_output_returns_empty(self):
        out = MockCoreOutput(
            dominant_disorder="normal",
            disorder_components=[],
        )
        assert evaluate_differentials(out) == []


class TestDeterminismAndIntegrity:
    def test_evaluate_is_pure_function(self):
        out = MockCoreOutput(
            disorder_components=["hagma"],
        )
        first = evaluate_differentials(out)
        second = evaluate_differentials(out)
        assert first == second
        assert first is not second  # yeni listeler döndürmeli

    def test_all_refs_exist(self):
        for key, entry in DIFFERENTIAL_KNOWLEDGE.items():
            for ref in entry.get("refs", []):
                assert ref in VERIFIED_REFS, f"{key} has unknown ref {ref}"

    def test_verified_refs_are_nonempty(self):
        assert VERIFIED_REFS
        for ref, text in VERIFIED_REFS.items():
            assert isinstance(text, str) and text.strip()

    def test_suggested_tests_only_for_non_computable_params(self):
        for key, entry in DIFFERENTIAL_KNOWLEDGE.items():
            if entry.get("suggested_tests"):
                assert key in {
                    "nagma_pattern",
                    "metabolic_alkalosis_subtypes",
                    "osmol_gap_toxic_alcohol",
                }, f"{key} beklenmedik suggested_tests içeriyor"


class TestRealPipelineIntegration:
    """Gerçek core.py hesaplama zinciri üzerinden entegrasyon testleri."""

    @staticmethod
    def _analyze_case(case_name: str):
        from core import StewartInput, analyze_stewart

        vals = SAMPLE_CASES[case_name]["values"]
        inp = StewartInput(
            ph=vals["ph"],
            pco2=vals["pco2"],
            na=vals["na"],
            cl=vals["cl"],
            be=vals.get("be"),
            k=vals.get("k"),
            lactate=vals.get("lactate"),
            albumin_gl=vals.get("albumin_gl"),
        )
        out, _ = analyze_stewart(inp)
        return out

    def test_nacl_infusion_triggers_nagma(self):
        out = self._analyze_case("nacl_infusion")
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "nagma_pattern" in keys, f"components={out.disorder_components}, keys={keys}"

    def test_dka_triggers_hagma(self):
        out = self._analyze_case("dka")
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "hagma_cat_mud_piles" in keys, f"components={out.disorder_components}, keys={keys}"

    def test_vomiting_triggers_metabolic_alkalosis(self):
        out = self._analyze_case("vomiting")
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "metabolic_alkalosis_subtypes" in keys, f"components={out.disorder_components}, keys={keys}"

    def test_lactic_acidosis_triggers_lactic_classification(self):
        out = self._analyze_case("lactic_acidosis")
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "lactic_acidosis_classification" in keys, f"components={out.disorder_components}, keys={keys}"

    def test_copd_acute_triggers_respiratory_acidosis(self):
        out = self._analyze_case("copd_acute")
        keys = [r["key"] for r in evaluate_differentials(out)]
        assert "respiratory_acidosis_etiology" in keys, f"components={out.disorder_components}, keys={keys}"


class TestConstantsUnchanged:
    """Mevcut sabitlerin dokunulmadığını dolaylı doğrula."""

    def test_ag_normal_unchanged(self):
        from constants import AG_NORMAL

        assert AG_NORMAL == 12.0

    def test_sid_thresholds_unchanged(self):
        assert SID_LOW_THRESHOLD == 38.0
        assert SID_HIGH_THRESHOLD == 44.0

    def test_lactate_threshold_unchanged(self):
        assert LACTATE_THRESHOLD == 2.0

    def test_clinical_significance_threshold_unchanged(self):
        assert CLINICAL_SIGNIFICANCE_THRESHOLD == 2.0
