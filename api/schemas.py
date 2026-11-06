"""
API istek ve yanıt modelleri.

Analiz çıktısı için yeni bir model yazılmaz: core.py'deki StewartOutput dataclass'ı
doğrudan yanıt modeli olarak kullanılır. Böylece OpenAPI şeması çekirdekle birebir
aynı kalır ve arayüz tipleri bu şemadan üretilebilir.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from constants import (
    BE_MAX,
    BE_MIN,
    HCO3_MAX,
    HCO3_MIN,
    PCO2_MAX,
    PCO2_MIN,
    PH_MAX,
    PH_MIN,
)
from core import StewartOutput

# NaN ve sonsuz değerler JSON'da taşınamaz ve hesabı bozar
Sayi = Annotated[float, Field(allow_inf_nan=False)]

# core.validate_input HCO3 ve BE'nin aralığını denetlemez (Streamlit'te giriş kutuları
# sınırlıydı). API'de bu sınır istek modelinde uygulanır; değerler constants.py'den gelir.
Hco3Sinirli = Annotated[float, Field(ge=HCO3_MIN, le=HCO3_MAX, allow_inf_nan=False)]
BeSinirli = Annotated[float, Field(ge=BE_MIN, le=BE_MAX, allow_inf_nan=False)]


# === /api/health, /api/meta ===

class HealthResponse(BaseModel):
    status: Literal["ok"]


class Limit(BaseModel):
    min: float
    max: float


class ReferenceRange(BaseModel):
    low: float
    high: float


class MetaResponse(BaseModel):
    version: str
    limits: dict[str, Limit]
    reference_ranges: dict[str, ReferenceRange]
    clinical_significance_threshold: float
    anion_gap_screening_threshold: float


# === /api/analyze ===

class AnalyzeRequest(BaseModel):
    """Analiz girdisi.

    pH, pCO2, Na, Cl, K, Ca, Mg, laktat, albümin ve fosfatın aralık denetimi çekirdekteki
    doğrulamada yapılır (is_valid=False döner). HCO3 ve BE'nin denetimi çekirdekte olmadığı
    için istek modelinde yapılır (sınır dışı değer 422 verir).
    """

    ph: Sayi
    pco2: Sayi
    na: Sayi
    cl: Sayi
    hco3: Hco3Sinirli | None = None
    be: BeSinirli | None = None
    is_be_base_deficit: bool = False
    k: Sayi | None = None
    ca: Sayi | None = None
    mg: Sayi | None = None
    lactate: Sayi | None = None
    po4: Sayi | None = None
    albumin: Sayi | None = None
    albumin_unit: Literal["g/L", "g/dL"] = "g/L"
    mode: Literal["quick", "advanced"] = "quick"


class AnalyzeResponse(BaseModel):
    """Doğrulama geçmezse is_valid=False olur ve result boş kalır."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    result: StewartOutput | None


# === /api/derived ===

class DerivedRequest(BaseModel):
    """HCO3 ve BE önizlemesi. Fizyolojik sınır dışı değerler 422 ile reddedilir."""

    ph: Annotated[float, Field(ge=PH_MIN, le=PH_MAX, allow_inf_nan=False)]
    pco2: Annotated[float, Field(ge=PCO2_MIN, le=PCO2_MAX, allow_inf_nan=False)]
    hco3_device: Hco3Sinirli | None = None
    be_device: BeSinirli | None = None
    is_base_deficit: bool = False


class Consistency(BaseModel):
    consistent: bool
    diff: float


class SignCheck(BaseModel):
    has_error: bool
    message: str
    suggested_be: float


class DerivedResponse(BaseModel):
    hco3_calculated: float
    be_calculated: float
    hco3_check: Consistency | None = None
    be_effective: float | None = None
    be_check: Consistency | None = None
    sign_check: SignCheck | None = None


# === /api/cases ===

class Case(BaseModel):
    id: str
    name: str
    description: str
    values: dict[str, float]
    teaching_point: str
