"""
services.py testleri.

process_batch ve check_be_sign_error önceden app.py içindeydi ve hiçbir testi yoktu.
Bu testler, taşıma sonrası davranışın korunduğunu ve fonksiyonların Streamlit olmadan
çalıştığını gösterir.
"""

import pandas as pd
import pytest

from services import check_be_sign_error, process_batch


class TestCheckBeSignError:
    def test_acidemia_with_positive_be_is_flagged(self):
        r = check_be_sign_error(7.20, 5.0)
        assert r["has_error"] is True
        assert r["suggested_be"] == -5.0
        assert "pozitif" in r["message"]

    def test_alkalemia_with_negative_be_is_flagged(self):
        r = check_be_sign_error(7.50, -5.0)
        assert r["has_error"] is True
        assert r["suggested_be"] == 5.0
        assert "negatif" in r["message"]

    def test_consistent_values_are_not_flagged(self):
        r = check_be_sign_error(7.30, -6.0)
        assert r == {"has_error": False, "message": "", "suggested_be": -6.0}

    def test_normal_ph_is_never_flagged(self):
        assert check_be_sign_error(7.40, 8.0)["has_error"] is False
        assert check_be_sign_error(7.40, -8.0)["has_error"] is False

    def test_threshold_is_strictly_greater_than_two(self):
        assert check_be_sign_error(7.20, 2.0)["has_error"] is False
        assert check_be_sign_error(7.20, 2.1)["has_error"] is True


class TestProcessBatch:
    def test_valid_row_is_analyzed(self):
        df = pd.DataFrame([{"ph": 7.30, "pco2": 31, "na": 141, "cl": 114, "lactate": 2.8, "albumin_gl": 25}])
        results, errors = process_batch(df, "quick")
        assert errors == []
        assert len(results) == 1
        assert results[0]["status"] == "OK"
        assert results[0]["row"] == 1
        assert results[0]["be_used"] == pytest.approx(-10.4)

    def test_invalid_row_is_reported_and_does_not_stop_the_batch(self):
        df = pd.DataFrame([
            {"ph": 9.5, "pco2": 31, "na": 141, "cl": 114},
            {"ph": 7.30, "pco2": 31, "na": 141, "cl": 114},
        ])
        results, errors = process_batch(df, "quick")
        assert [r["status"] for r in results] == ["ERROR", "OK"]
        assert [r["row"] for r in results] == [1, 2]
        assert len(errors) == 1
        assert errors[0]["row"] == 1
        assert "pH" in errors[0]["errors"]

    def test_empty_dataframe_returns_nothing(self):
        df = pd.DataFrame(columns=["ph", "pco2", "na", "cl"])
        assert process_batch(df, "quick") == ([], [])
