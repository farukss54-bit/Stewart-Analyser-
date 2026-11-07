"""
Stewart Asit-Baz Analizi - HTTP API (ince katman)

Bu katman hesaplama yapmaz: core.py, validation.py ve services.py'yi çağırır, sonucu JSON
olarak sunar. Durumsuzdur: girilen değerleri saklamaz.

Çalıştırma (depo kökünden):
    uvicorn api.main:app --port 8000
"""

import csv
import importlib.util
import io
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response

from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchRequest,
    BatchResponse,
    Case,
    Consistency,
    DerivedRequest,
    DerivedResponse,
    HealthResponse,
    Limit,
    MetaResponse,
    ReferenceRange,
    SignCheck,
)
from constants import (
    AG_HIGH_THRESHOLD,
    AG_NORMAL_HIGH,
    ALBUMIN_MAX_GDL,
    ALBUMIN_MAX_GL,
    ALBUMIN_MIN_GDL,
    ALBUMIN_MIN_GL,
    BE_MAX,
    BE_MIN,
    CA_MAX,
    CA_MIN,
    CLINICAL_SIGNIFICANCE_THRESHOLD,
    HCO3_MAX,
    HCO3_MIN,
    MG_MAX,
    MG_MIN,
    PHYSIOLOGIC_LIMITS,
    PO4_MAX,
    PO4_MIN,
    REFERENCE_RANGES,
    SAMPLE_CASES,
    SID_NORMAL_BASIC,
    SID_NORMAL_FULL,
    SID_NORMAL_RANGE,
    SID_NORMAL_SIMPLE,
)
from core import (
    StewartInput,
    analyze_stewart,
    calculate_be,
    calculate_hco3,
    check_be_consistency,
    check_hco3_consistency,
    output_to_dict,
)
from api.batch import run_batch
from services import check_be_sign_error

ROOT = Path(__file__).resolve().parent.parent

# g/dL -> g/L çarpanı (app.py'deki albümin dönüşümüyle aynı: alb * 10)
ALBUMIN_GDL_TO_GL = 10.0

# Sonuç ekranında normal bant olarak gösterilen iki aralık. Streamlit arayüzündeki göstergeyle
# aynıdır (ui_components.get_value_indicator: HCO3 22-26, BE ±2). constants.py'de karşılıkları
# olmadığı için burada tutulur; oraya taşınana kadar tek kopya bu dosyadadır.
HCO3_REFERENCE_RANGE = (22.0, 26.0)
BE_REFERENCE_RANGE = (-CLINICAL_SIGNIFICANCE_THRESHOLD, CLINICAL_SIGNIFICANCE_THRESHOLD)

# Gelişmiş modun SID merdiveninde her katmanın normal değeri çizilir (constants.py'deki normal
# değer ± SID_NORMAL_RANGE). Anyon açığının alt normal sınırı constants.py'de yoktur; AG_NORMAL_HIGH
# yorumundaki "3-11" aralığının alt ucu burada tutulur.
SID_REFERENCE_RANGES = {
    "sid_simple": SID_NORMAL_SIMPLE,
    "sid_basic": SID_NORMAL_BASIC,
    "sid_full": SID_NORMAL_FULL,
}
ANION_GAP_REFERENCE_RANGE = (3.0, AG_NORMAL_HIGH)


def _read_version() -> str:
    """Sürümü kökteki __init__.py'den okur (tek kaynak)."""
    spec = importlib.util.spec_from_file_location("stewart_version", ROOT / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__


app = FastAPI(title="Stewart Asit-Baz Analizi API", version=_read_version())


@app.get("/api/health")
def health() -> HealthResponse:
    """Sunucunun ayakta olduğunu bildirir."""
    return HealthResponse(status="ok")


@app.get("/api/meta")
def meta() -> MetaResponse:
    """Arayüzün ihtiyaç duyduğu sürüm, fizyolojik sınırlar ve referans aralıkları.

    Değerlerin hepsi constants.py'den gelir; burada yeni eşik tanımlanmaz.
    """
    limits = {name: Limit(min=lo, max=hi) for name, (lo, hi) in PHYSIOLOGIC_LIMITS.items()}
    limits["hco3"] = Limit(min=HCO3_MIN, max=HCO3_MAX)
    limits["be"] = Limit(min=BE_MIN, max=BE_MAX)
    limits["albumin_gl"] = Limit(min=ALBUMIN_MIN_GL, max=ALBUMIN_MAX_GL)
    limits["albumin_gdl"] = Limit(min=ALBUMIN_MIN_GDL, max=ALBUMIN_MAX_GDL)
    # PHYSIOLOGIC_LIMITS'te yok; core.validate_input bu üçünü doğrudan constants.py sınırlarıyla denetler
    limits["ca"] = Limit(min=CA_MIN, max=CA_MAX)
    limits["mg"] = Limit(min=MG_MIN, max=MG_MAX)
    limits["po4"] = Limit(min=PO4_MIN, max=PO4_MAX)

    ranges = {
        **REFERENCE_RANGES,
        "hco3": HCO3_REFERENCE_RANGE,
        "be": BE_REFERENCE_RANGE,
        "anion_gap": ANION_GAP_REFERENCE_RANGE,
        **{ad: (normal - SID_NORMAL_RANGE, normal + SID_NORMAL_RANGE) for ad, normal in SID_REFERENCE_RANGES.items()},
    }
    reference_ranges = {name: ReferenceRange(low=lo, high=hi) for name, (lo, hi) in ranges.items()}

    return MetaResponse(
        version=app.version,
        limits=limits,
        reference_ranges=reference_ranges,
        clinical_significance_threshold=CLINICAL_SIGNIFICANCE_THRESHOLD,
        anion_gap_screening_threshold=AG_HIGH_THRESHOLD,
    )


@app.post("/api/derived")
def derived(req: DerivedRequest) -> DerivedResponse:
    """pH ve pCO2'den HCO3 ve BE'yi hesaplar; cihaz değerleri verilmişse tutarlılığı denetler.

    Mantık, Streamlit arayüzündeki "türetilmiş değerler" bölümüyle aynıdır (BE işaret
    hatası denetimi dahil). Analizi engellemek arayüzün işidir; bu uç yalnızca bildirir.
    """
    hco3_calc = calculate_hco3(req.ph, req.pco2)
    be_calc = calculate_be(req.ph, hco3_calc)
    response = DerivedResponse(hco3_calculated=hco3_calc, be_calculated=be_calc)

    if req.hco3_device is not None:
        consistent, diff = check_hco3_consistency(req.hco3_device, hco3_calc)
        response.hco3_check = Consistency(consistent=consistent, diff=diff)

    if req.be_device is not None:
        be_effective = -req.be_device if req.is_base_deficit else req.be_device
        consistent, diff = check_be_consistency(be_effective, be_calc)
        response.be_effective = be_effective
        response.be_check = Consistency(consistent=consistent, diff=diff)
        response.sign_check = SignCheck(**check_be_sign_error(req.ph, be_effective))

    return response


def _run_analysis(req: AnalyzeRequest):
    """İsteği çekirdeğe uygun girdiye çevirir ve analizi çalıştırır (analyze ve csv ortak yolu)."""
    albumin_gl = req.albumin
    if albumin_gl is not None and req.albumin_unit == "g/dL":
        albumin_gl = albumin_gl * ALBUMIN_GDL_TO_GL

    inp = StewartInput(
        ph=req.ph,
        pco2=req.pco2,
        na=req.na,
        cl=req.cl,
        hco3=req.hco3,
        be=req.be,
        k=req.k,
        ca=req.ca,
        mg=req.mg,
        lactate=req.lactate,
        albumin_gl=albumin_gl,
        po4=req.po4,
        is_be_base_deficit=req.is_be_base_deficit,
    )
    out, validation = analyze_stewart(inp, req.mode)
    return inp, out, validation


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Stewart analizini çalıştırır.

    Girdi doğrulamayı geçmezse 200 döner, is_valid=False olur ve hatalar listelenir
    (istek biçimi bozuksa FastAPI 422 verir).
    """
    _, out, validation = _run_analysis(req)
    return AnalyzeResponse(
        is_valid=validation.is_valid,
        errors=validation.errors,
        warnings=validation.warnings,
        result=out if validation.is_valid else None,
    )


@app.post(
    "/api/analyze/csv",
    response_class=Response,
    responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}},
)
def analyze_csv(req: AnalyzeRequest) -> Response:
    """Tek analizin sonucunu CSV olarak döndürür (başlık satırı + tek satır).

    Sütunlar ve değerler Streamlit'teki "Sonucu İndir (CSV)" ile aynıdır: core.output_to_dict.
    Girdi doğrulamayı geçmezse indirilecek sonuç yoktur; 422 ve hata listesi döner.
    """
    inp, out, validation = _run_analysis(req)
    if not validation.is_valid:
        raise HTTPException(status_code=422, detail=validation.errors)

    row = output_to_dict(inp, out)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(row), lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return Response(
        content=buffer.getvalue().encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="stewart_result.csv"'},
    )


@app.post("/api/batch")
def batch(req: BatchRequest) -> BatchResponse:
    """CSV metnindeki her satırı analiz eder (Streamlit'teki toplu analizle aynı yol).

    Geçersiz satır diğerlerini durdurmaz; satırın durumu ERROR olur ve nedeni yazılır.
    Dosya okunamazsa ya da sınırı aşarsa 200 döner, is_valid=False olur.
    """
    return run_batch(req.csv, req.mode)


@app.get("/api/cases")
def cases() -> list[Case]:
    """Hazır (eğitim amaçlı) vakalar."""
    return [
        Case(
            id=case_id,
            name=case["name"],
            description=case["description"],
            values=case["values"],
            teaching_point=case["teaching_point"],
        )
        for case_id, case in SAMPLE_CASES.items()
    ]
