"""
Stewart Asit-Baz Analizi - HTTP API (ince katman)

Bu katman hesaplama yapmaz: core.py ve validation.py'yi çağırır, sonucu JSON olarak sunar.
Durumsuzdur: girilen değerleri saklamaz.

Çalıştırma (depo kökünden):
    uvicorn api.main:app --port 8000
"""

import importlib.util
from pathlib import Path

from fastapi import FastAPI

from constants import (
    ALBUMIN_MAX_GDL,
    ALBUMIN_MAX_GL,
    ALBUMIN_MIN_GDL,
    ALBUMIN_MIN_GL,
    BE_MAX,
    BE_MIN,
    CLINICAL_SIGNIFICANCE_THRESHOLD,
    HCO3_MAX,
    HCO3_MIN,
    PHYSIOLOGIC_LIMITS,
    REFERENCE_RANGES,
)

ROOT = Path(__file__).resolve().parent.parent


def _read_version() -> str:
    """Sürümü kökteki __init__.py'den okur (tek kaynak)."""
    spec = importlib.util.spec_from_file_location("stewart_version", ROOT / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__


app = FastAPI(title="Stewart Asit-Baz Analizi API", version=_read_version())


@app.get("/api/health")
def health() -> dict:
    """Sunucunun ayakta olduğunu bildirir."""
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict:
    """Arayüzün ihtiyaç duyduğu sürüm, fizyolojik sınırlar ve referans aralıkları.

    Değerlerin hepsi constants.py'den gelir; burada yeni eşik tanımlanmaz.
    """
    limits = {name: {"min": lo, "max": hi} for name, (lo, hi) in PHYSIOLOGIC_LIMITS.items()}
    limits["hco3"] = {"min": HCO3_MIN, "max": HCO3_MAX}
    limits["be"] = {"min": BE_MIN, "max": BE_MAX}
    limits["albumin_gl"] = {"min": ALBUMIN_MIN_GL, "max": ALBUMIN_MAX_GL}
    limits["albumin_gdl"] = {"min": ALBUMIN_MIN_GDL, "max": ALBUMIN_MAX_GDL}

    reference_ranges = {name: {"low": lo, "high": hi} for name, (lo, hi) in REFERENCE_RANGES.items()}

    return {
        "version": app.version,
        "limits": limits,
        "reference_ranges": reference_ranges,
        "clinical_significance_threshold": CLINICAL_SIGNIFICANCE_THRESHOLD,
    }
