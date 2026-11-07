"""
POST /api/batch testleri.

Temel güvence: toplu analiz, Streamlit'teki yolla (pd.read_csv -> services.process_batch)
birebir aynı sonucu verir. Bu yüzden beklenen değerler aynı iki fonksiyonla üretilir.
"""

import csv
import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.batch import MAX_CSV_CHARS, MAX_ROWS
from api.main import app
from services import process_batch

client = TestClient(app)

# Streamlit'teki "Örnek CSV İndir" ile aynı içerik
SAMPLE_CSV = """ph,pco2,na,cl,k,lactate,albumin_gl,be
7.40,40,140,102,4.0,1.0,40,0
7.30,30,138,108,4.5,3.0,35,-6
7.25,25,136,100,5.0,8.0,28,-12"""


def _post(text: str, mode: str = "quick"):
    return client.post("/api/batch", json={"csv": text, "mode": mode})


class TestBatchMatchesStreamlitPath:
    def test_result_file_equals_streamlit_dataframe_csv(self):
        body = _post(SAMPLE_CSV).json()
        results, _ = process_batch(pd.read_csv(io.StringIO(SAMPLE_CSV)), "quick")
        expected = pd.DataFrame(results).to_csv(index=False)
        assert body["csv"].splitlines() == expected.splitlines()

    def test_advanced_mode_is_passed_through(self):
        text = "ph,pco2,na,cl,k,ca,mg,po4,lactate,albumin_gl\n7.30,31,141,114,4.1,1.2,0.8,1.1,2.8,25"
        body = _post(text, "advanced").json()
        results, _ = process_batch(pd.read_csv(io.StringIO(text)), "advanced")
        assert body["csv"].splitlines() == pd.DataFrame(results).to_csv(index=False).splitlines()
        # Gelişmiş modda SIG hesaplanır; hızlı modda hesaplanmaz
        advanced = list(csv.DictReader(io.StringIO(body["csv"])))[0]
        quick = list(csv.DictReader(io.StringIO(_post(text, "quick").json()["csv"])))[0]
        assert advanced["sig"] != quick["sig"]

    def test_counts_and_rows(self):
        body = _post(SAMPLE_CSV).json()
        assert body["is_valid"] is True
        assert (body["total"], body["ok"], body["failed"]) == (3, 3, 0)
        assert [r["row"] for r in body["rows"]] == [1, 2, 3]
        assert all(r["status"] == "OK" for r in body["rows"])
        first = body["rows"][0]
        assert first["ph"] == pytest.approx(7.40)
        assert first["be_used"] == pytest.approx(0.0)
        assert first["headline"]

    def test_result_file_has_no_bom_and_can_be_read_back(self):
        body = _post(SAMPLE_CSV).json()
        assert body["csv"].startswith("ph,")
        assert len(list(csv.DictReader(io.StringIO(body["csv"])))) == 3


class TestBatchRowErrors:
    TEXT = "ph,pco2,na,cl\n9.5,31,141,114\n7.30,31,141,114"

    def test_invalid_row_does_not_stop_the_others(self):
        body = _post(self.TEXT).json()
        assert (body["total"], body["ok"], body["failed"]) == (2, 1, 1)
        bad, good = body["rows"]
        assert bad["status"] == "ERROR"
        assert "pH" in bad["errors"]
        assert bad["ph"] is None
        assert good["status"] == "OK"
        assert good["errors"] is None

    def test_missing_column_is_reported_per_row(self):
        body = _post("ph,pco2,na\n7.30,31,141").json()
        assert body["is_valid"] is True
        assert body["failed"] == 1
        assert body["rows"][0]["status"] == "ERROR"

    def test_flags_are_split_into_a_list(self):
        # Girilen BE, pH ve pCO2'den hesaplanan BE'den >2 farklıysa BE_MISMATCH işareti çıkar
        body = _post("ph,pco2,na,cl,be\n7.30,31,141,114,5").json()
        row = body["rows"][0]
        assert "BE_MISMATCH" in row["flags"]
        assert all("," not in f for f in row["flags"])
        # Streamlit'teki toplu analiz gibi: "warnings" sütunu doğrulama uyarılarıdır, bu satırda boştur
        assert row["warnings"] == []


class TestBatchUnreadableInput:
    @pytest.mark.parametrize("text", ["", "ph,pco2,na,cl", "\n\n"])
    def test_empty_or_header_only_file_is_rejected_with_a_reason(self, text):
        body = _post(text).json()
        assert body["is_valid"] is False
        assert body["errors"]
        assert body["rows"] == []
        assert body["csv"] == ""

    def test_too_many_rows(self):
        text = "ph,pco2,na,cl\n" + "7.30,31,141,114\n" * (MAX_ROWS + 1)
        body = _post(text).json()
        assert body["is_valid"] is False
        assert str(MAX_ROWS) in body["errors"][0]

    def test_too_large_file(self):
        body = _post("a" * (MAX_CSV_CHARS + 1)).json()
        assert body["is_valid"] is False
        assert "büyük" in body["errors"][0]

    def test_bom_is_ignored(self):
        body = _post("﻿" + SAMPLE_CSV).json()
        assert body["ok"] == 3

    def test_malformed_request_is_422(self):
        assert client.post("/api/batch", json={"mode": "quick"}).status_code == 422
        assert client.post("/api/batch", json={"csv": SAMPLE_CSV, "mode": "x"}).status_code == 422
