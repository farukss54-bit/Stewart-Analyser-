"""
Toplu CSV analizi: yüklenen metni Streamlit'teki toplu analizle aynı yoldan geçirir.

CSV, Streamlit'te olduğu gibi pandas ile okunur ve services.process_batch'e verilir; yani
doğrulama, Na/Cl şüphesi ve analiz çekirdeği tek kopyadır. İndirilen sonuç dosyası da
Streamlit'in `pd.DataFrame(results).to_csv(index=False)` çıktısıyla aynı sütunlardadır.
"""

import io
import math

import pandas as pd

from api.schemas import BatchResponse, BatchRow
from services import process_batch

# API'nin kendi koruması (Streamlit'in yükleme sınırı yerine). Sınırı aşan dosya analiz edilmez.
MAX_CSV_CHARS = 2_000_000

# İndirilen CSV dosyaları UTF-8 BOM ile başlar: Türkçe Excel BOM'suz dosyayı ANSI sanıp Türkçe karakterleri
# bozar. pandas ve bu API BOM'u okurken atar, yani dosya toplu yüklemeye geri verilebilir.
CSV_BOM = "\ufeff"
MAX_ROWS = 5000


def _bos(errors: list[str]) -> BatchResponse:
    return BatchResponse(is_valid=False, errors=errors, total=0, ok=0, failed=0, rows=[], csv="")


def _sayi(value) -> float | None:
    """Tablo sütunları için: sayı değilse ya da sonlu değilse boş bırakılır (JSON NaN taşıyamaz)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


def _liste(value, ayirac: str) -> list[str]:
    """Sonuç dosyasında tek hücreye birleştirilmiş değerleri ("a|b") listeye ayırır."""
    return [parca for parca in value.split(ayirac) if parca] if isinstance(value, str) else []


def _satir(result: dict) -> BatchRow:
    return BatchRow(
        row=result["row"],
        status=result["status"],
        errors=result.get("errors"),
        warnings=_liste(result.get("warnings"), "|"),
        flags=_liste(result.get("flags"), ","),
        ph=_sayi(result.get("ph")),
        pco2=_sayi(result.get("pco2")),
        be_used=_sayi(result.get("be_used")),
        headline=result.get("headline_dominant") or None,
    )


def run_batch(csv_text: str, mode: str) -> BatchResponse:
    if len(csv_text) > MAX_CSV_CHARS:
        return _bos([f"Dosya çok büyük (en fazla {MAX_CSV_CHARS // 1_000_000} MB)."])

    try:
        df = pd.read_csv(io.StringIO(csv_text.lstrip(CSV_BOM)))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as err:
        return _bos([f"CSV okunamadı: {err}"])

    if len(df) == 0:
        return _bos(["CSV’de analiz edilecek satır yok."])
    if len(df) > MAX_ROWS:
        return _bos([f"En fazla {MAX_ROWS} satır analiz edilir; dosyada {len(df)} satır var."])

    results, errors = process_batch(df, mode)
    return BatchResponse(
        is_valid=True,
        errors=[],
        total=len(results),
        ok=len(results) - len(errors),
        failed=len(errors),
        rows=[_satir(r) for r in results],
        csv=CSV_BOM + pd.DataFrame(results).to_csv(index=False, lineterminator="\n"),
    )
