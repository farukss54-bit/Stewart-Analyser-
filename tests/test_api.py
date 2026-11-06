"""
HTTP API testleri.

Temel güvence: API çekirdekten farklı bir sonuç ÜRETMEZ. Altın testler, aynı girdi için
API yanıtının doğrudan analyze_stewart çıktısıyla birebir aynı olduğunu doğrular.

Bu testler fastapi ve httpx2 gerektirir (api/requirements.txt). Kurulu değilse atlanmaz,
toplama aşamasında hata verir; böylece test sayısı sessizce düşmez.
"""

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.main import app
from constants import (
    CA_NORMAL,
    CLINICAL_SIGNIFICANCE_THRESHOLD,
    MG_NORMAL,
    PHYSIOLOGIC_LIMITS,
    PO4_NORMAL,
    SAMPLE_CASES,
)
from core import StewartInput, StewartOutput, analyze_stewart, calculate_be, calculate_hco3
from scripts.export_openapi import SCHEMA_PATH, render_schema
from services import check_be_sign_error

client = TestClient(app)
output_adapter = TypeAdapter(StewartOutput)


def _root_version() -> str:
    path = Path(__file__).resolve().parent.parent / "__init__.py"
    spec = importlib.util.spec_from_file_location("root_init", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__


def _direct(inp: StewartInput, mode: str) -> dict:
    out, _ = analyze_stewart(inp, mode)
    return output_adapter.dump_python(out, mode="json")


class TestHealthAndMeta:
    def test_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_meta_version_comes_from_root_init(self):
        assert client.get("/api/meta").json()["version"] == _root_version()

    def test_meta_limits_match_constants(self):
        limits = client.get("/api/meta").json()["limits"]
        for name, (lo, hi) in PHYSIOLOGIC_LIMITS.items():
            assert limits[name] == {"min": lo, "max": hi}
        assert {"hco3", "be", "albumin_gl", "albumin_gdl"} <= set(limits)

    def test_meta_threshold_and_reference_ranges(self):
        body = client.get("/api/meta").json()
        assert body["clinical_significance_threshold"] == CLINICAL_SIGNIFICANCE_THRESHOLD
        assert body["reference_ranges"]["ph"] == {"low": 7.35, "high": 7.45}

    def test_meta_has_display_ranges_for_hco3_and_be(self):
        """Sonuç ekranı HCO3 ve BE için de normal bant çizer (Streamlit göstergesiyle aynı değerler)."""
        ranges = client.get("/api/meta").json()["reference_ranges"]
        assert ranges["hco3"] == {"low": 22.0, "high": 26.0}
        assert ranges["be"] == {"low": -CLINICAL_SIGNIFICANCE_THRESHOLD, "high": CLINICAL_SIGNIFICANCE_THRESHOLD}

    def test_openapi_schema_is_typed(self):
        """Tip üretimi için şema alan tiplerini taşımalı (düz dict olmamalı)."""
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        assert {"be_used", "headline", "mechanism_analysis", "cds_notes"} <= set(schemas["StewartOutput"]["properties"])
        assert {"version", "limits", "reference_ranges"} <= set(schemas["MetaResponse"]["properties"])


class TestCommittedSchema:
    def test_committed_openapi_schema_is_current(self):
        """web/openapi.json (arayüz tiplerinin kaynağı) API'nin gerçek şemasıyla aynı olmalı."""
        assert SCHEMA_PATH.read_text(encoding="utf-8") == render_schema(), (
            "API şeması değişti. Güncelle: python scripts/export_openapi.py, "
            "ardından web klasöründe npm run api:tipleri"
        )


class TestDerived:
    def test_matches_core_calculation(self):
        body = client.post("/api/derived", json={"ph": 7.30, "pco2": 31}).json()
        hco3 = calculate_hco3(7.30, 31)
        assert body["hco3_calculated"] == hco3
        assert body["be_calculated"] == calculate_be(7.30, hco3)
        assert body["hco3_check"] is None and body["be_check"] is None and body["sign_check"] is None

    def test_hco3_device_value_is_checked(self):
        calc = calculate_hco3(7.30, 31)
        ok = client.post("/api/derived", json={"ph": 7.30, "pco2": 31, "hco3_device": calc + 1.0}).json()
        bad = client.post("/api/derived", json={"ph": 7.30, "pco2": 31, "hco3_device": calc + 5.0}).json()
        assert ok["hco3_check"]["consistent"] is True
        assert bad["hco3_check"]["consistent"] is False
        assert bad["hco3_check"]["diff"] == 5.0

    def test_be_sign_error_is_reported_like_services(self):
        body = client.post("/api/derived", json={"ph": 7.20, "pco2": 31, "be_device": 5.0}).json()
        assert body["sign_check"] == check_be_sign_error(7.20, 5.0)
        assert body["sign_check"]["has_error"] is True
        assert body["be_effective"] == 5.0

    def test_base_deficit_flag_flips_the_sign(self):
        body = client.post(
            "/api/derived", json={"ph": 7.20, "pco2": 31, "be_device": 5.0, "is_base_deficit": True}
        ).json()
        assert body["be_effective"] == -5.0
        assert body["sign_check"]["has_error"] is False

    @pytest.mark.parametrize("payload", [
        {"ph": 9.0, "pco2": 31},
        {"ph": 7.30, "pco2": 0.0},
        {"ph": 7.30, "pco2": 31, "be_device": 99.0},
    ])
    def test_out_of_range_is_rejected(self, payload):
        assert client.post("/api/derived", json=payload).status_code == 422


class TestAnalyzeGolden:
    """API çıktısı = çekirdek çıktısı (tüm hazır vakalar, hızlı mod)."""

    @pytest.mark.parametrize("case_id", sorted(SAMPLE_CASES))
    def test_sample_case_matches_core(self, case_id):
        values = dict(SAMPLE_CASES[case_id]["values"])
        request = {k: v for k, v in values.items() if k != "albumin_gl"}
        if "albumin_gl" in values:
            request["albumin"] = values["albumin_gl"]
        r = client.post("/api/analyze", json=request)
        assert r.status_code == 200
        body = r.json()
        assert body["is_valid"] is True
        assert body["result"] == _direct(StewartInput(**values), "quick")

    def test_advanced_mode_matches_core(self):
        values = dict(ph=7.30, pco2=31.0, na=141.0, cl=114.0, k=4.1, ca=CA_NORMAL, mg=MG_NORMAL,
                      po4=PO4_NORMAL, lactate=2.8, albumin_gl=25.0)
        request = {k: v for k, v in values.items() if k != "albumin_gl"}
        request.update(albumin=25.0, mode="advanced")
        body = client.post("/api/analyze", json=request).json()
        assert body["is_valid"] is True
        assert body["result"] == _direct(StewartInput(**values), "advanced")

    def test_albumin_in_gdl_is_converted(self):
        base = dict(ph=7.30, pco2=31.0, na=141.0, cl=114.0, lactate=2.8)
        in_gl = client.post("/api/analyze", json={**base, "albumin": 25.0, "albumin_unit": "g/L"}).json()
        in_gdl = client.post("/api/analyze", json={**base, "albumin": 2.5, "albumin_unit": "g/dL"}).json()
        assert in_gdl["result"] == in_gl["result"]

    def test_example_values_used_in_the_design_mockup(self):
        """Tasarım örneği (kurgusal vaka) çekirdekle tutarlı: BE -10.4, SID_simple 27.0."""
        r = client.post("/api/analyze", json={
            "ph": 7.30, "pco2": 31, "na": 141, "cl": 114, "lactate": 2.8, "albumin": 25,
        }).json()["result"]
        assert r["be_used"] == pytest.approx(-10.4)
        assert r["sid_values"]["sid_simple"] == pytest.approx(27.0)


class TestAnalyzeValidation:
    def test_out_of_range_input_returns_errors_not_a_crash(self):
        r = client.post("/api/analyze", json={"ph": 9.5, "pco2": 31, "na": 141, "cl": 114})
        assert r.status_code == 200
        body = r.json()
        assert body["is_valid"] is False
        assert body["result"] is None
        assert any("pH" in e for e in body["errors"])

    def test_missing_required_field_is_422(self):
        assert client.post("/api/analyze", json={"ph": 7.30, "pco2": 31, "na": 141}).status_code == 422

    @pytest.mark.parametrize("extra", [
        {"hco3": 1e308},
        {"hco3": -500},
        {"hco3": 4.9},
        {"hco3": 50.1},
        {"be": -9999},
        {"be": 30.1},
        {"be": -30.1},
    ])
    def test_absurd_hco3_or_be_is_rejected(self, extra):
        """Çekirdek HCO3/BE aralığını denetlemez; API sınır dışı değeri 422 ile reddetmeli."""
        payload = {"ph": 7.30, "pco2": 31, "na": 141, "cl": 114, **extra}
        assert client.post("/api/analyze", json=payload).status_code == 422

    @pytest.mark.parametrize("extra", [
        {"hco3": 5.0},
        {"hco3": 50.0},
        {"be": -30.0},
        {"be": 30.0},
    ])
    def test_hco3_and_be_boundaries_are_accepted(self, extra):
        payload = {"ph": 7.30, "pco2": 31, "na": 141, "cl": 114, **extra}
        r = client.post("/api/analyze", json=payload)
        assert r.status_code == 200
        assert r.json()["is_valid"] is True

    def test_base_deficit_flag_is_applied_once(self):
        """Ham BE + BD bayrağı gönderilir; işaret çekirdekte yalnızca bir kez çevrilir.

        Arayüz hesaplanmış (işareti çevrilmiş) değeri DEĞİL ham girişi gönderir. Aksi halde
        işaret iki kez çevrilir ve analiz ters işaretli BE ile çalışır.
        """
        base = {"ph": 7.20, "pco2": 31, "na": 141, "cl": 114}
        bd = client.post("/api/analyze", json={**base, "be": 5.0, "is_be_base_deficit": True}).json()
        plain = client.post("/api/analyze", json={**base, "be": -5.0}).json()
        assert bd["result"]["be_used"] == -5.0
        assert bd["result"] == plain["result"]

    def test_unknown_mode_is_422(self):
        payload = {"ph": 7.30, "pco2": 31, "na": 141, "cl": 114, "mode": "turbo"}
        assert client.post("/api/analyze", json=payload).status_code == 422


class TestCases:
    def test_lists_all_sample_cases(self):
        body = client.get("/api/cases").json()
        assert [c["id"] for c in body] == list(SAMPLE_CASES)
        first = body[0]
        source = SAMPLE_CASES[first["id"]]
        assert first["name"] == source["name"]
        assert first["values"] == source["values"]
        assert first["teaching_point"] == source["teaching_point"]
