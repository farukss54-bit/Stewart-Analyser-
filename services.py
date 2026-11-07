"""
Çerçeveden bağımsız servis fonksiyonları (Streamlit içermez).

Bu fonksiyonlar önceden app.py içindeydi; hem Streamlit arayüzü hem de HTTP API
tarafından kullanılabilsin diye buraya taşındı. Gövdeleri değiştirilmeden taşınmıştır.
"""

from core import analyze_stewart, output_to_dict, stewart_input_from_normalized
from validation import validate_csv_row
from constants import PH_NORMAL_LOW, PH_NORMAL_HIGH
from logger import log_analysis_error, log_batch_progress


def process_batch(df, mode):
    """Process batch CSV data"""
    results = []
    errors = []
    total = max(len(df), 1)

    for idx, row in df.iterrows():
        _progress = min((idx + 1) / total, 1.0)
        log_batch_progress(idx + 1, total, "processing")

        row_dict = row.to_dict()
        validation = validate_csv_row(row_dict, idx)

        if not validation.is_valid:
            error_msg = "; ".join(validation.errors)
            results.append({"row": idx + 1, "status": "ERROR", "errors": error_msg})
            errors.append({"row": idx + 1, "errors": error_msg})
            continue

        try:
            inp = stewart_input_from_normalized(validation.normalized_values)
            out, val = analyze_stewart(inp, mode)

            if val.is_valid:
                result = output_to_dict(inp, out)
                # Satır doğrulamasının uyarıları (örn. Na/Cl kolon yer değiştirme şüphesi) da sonuca girer;
                # aksi halde şüpheli satır uyarısız analiz edilmiş görünürdü
                result.update({
                    "row": idx + 1,
                    "status": "OK",
                    "warnings": "|".join(validation.warnings + val.warnings),
                })
                results.append(result)
            else:
                error_text = "; ".join(val.errors)
                results.append({"row": idx + 1, "status": "ERROR", "errors": error_text})
                errors.append({"row": idx + 1, "errors": error_text})
        except Exception as e:
            err = str(e)
            results.append({"row": idx + 1, "status": "ERROR", "errors": err})
            errors.append({"row": idx + 1, "errors": err})
            log_analysis_error("batch_row_failed", {"row": idx, "error": err})

    log_batch_progress(total, total, "complete")
    return results, errors


def check_be_sign_error(ph: float, be: float) -> dict:
    """
    BE işaret hatası kontrolü.
    
    Returns:
        dict with keys:
        - has_error: bool
        - message: str
        - suggested_be: float (işaret düzeltilmiş)
    """
    # pH asidemi gösteriyor ama BE pozitif (alkaloz)
    if ph < PH_NORMAL_LOW and be > 2:
        return {
            "has_error": True,
            "message": f"⚠️ pH ({ph:.2f}) asidemi gösteriyor ama BE ({be:+.1f}) pozitif. İşaret hatası olabilir!",
            "suggested_be": -be
        }
    
    # pH alkalemi gösteriyor ama BE negatif (asidoz)
    if ph > PH_NORMAL_HIGH and be < -2:
        return {
            "has_error": True,
            "message": f"⚠️ pH ({ph:.2f}) alkalemi gösteriyor ama BE ({be:+.1f}) negatif. İşaret hatası olabilir!",
            "suggested_be": -be
        }
    
    return {"has_error": False, "message": "", "suggested_be": be}
