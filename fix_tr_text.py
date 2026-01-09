# fix_tr_text.py
from pathlib import Path

FILES = [
    "__init__.py"
    "constants.py",
    "validation.py",
    "ui_components.py",
    "core.py",
    "app.py",
    "visualization.py"
    "logger.py"
    "test_core.py"
    "test_validation.py"
   
]

# 1) Türkçe mojibake düzeltmeleri (en sık görülenler)
MOJIBAKE_MAP = {
    "Ã§": "ç", "Ã‡": "Ç",
    "ÄŸ": "ğ", "Äž": "Ğ",  # Äž bazen çıkar
    "Ä±": "ı", "Ä°": "İ",
    "Ã¶": "ö", "Ã–": "Ö",
    "ÅŸ": "ş", "Åž": "Ş",
    "Ã¼": "ü", "Ãœ": "Ü",

    # 2) Bilimsel sembol mojibake'ları -> ASCII
    "â‚‚": "2",   # subscript 2
    "â‚ƒ": "3",   # subscript 3
    "âº": "+",   # superscript plus
    "â»": "-",   # superscript minus
    "Â²": "2",    # superscript 2
    "Â³": "3",
    "Â°": "°",    # derece işareti bazen "Â°" olur
}

def repair_line(s: str) -> str:
    # Önce direkt harita değişimleri
    for bad, good in MOJIBAKE_MAP.items():
        s = s.replace(bad, good)

    # Bazı kontrol karakterleri (özellikle âº gibi parçalarda) kalabiliyor
    # Onları temizle (görünmez saçmalıklar)
    s = "".join(ch for ch in s if ch == "\n" or ch == "\t" or (ord(ch) >= 32 and ch != "\x7f"))
    return s

def process_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fixed = repair_line(text)
    if fixed != text:
        path.write_text(fixed, encoding="utf-8", newline="\n")
        print(f"fixed: {path.name}")
    else:
        print(f"no change: {path.name}")

if __name__ == "__main__":
    for fn in FILES:
        p = Path(fn)
        if p.exists():
            process_file(p)
