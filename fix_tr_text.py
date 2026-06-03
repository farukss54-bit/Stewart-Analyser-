# fix_tr_text.py
from pathlib import Path

FILES = [
    "__init__.py",
    "constants.py",
    "validation.py",
    "ui_components.py",
    "core.py",
    "app.py",
    "visualization.py",
    "logger.py",
    "test_core.py",
    "test_validation.py",
    "test_regression.py",
    "test_regression_fixed.py",
    "test_simple.py",
    "test_sprint4.py",
]

# 1) Türkçe mojibake düzeltmeleri (en sık görülenler)
# Mojibake: UTF-8 baytlarının Latin-1/CP1252 olarak yanlış okunması sonucu oluşan bozuk karakterler.
MOJIBAKE_MAP = {
    "\xc3\xa7": "ç",  # Ã§ -> ç
    "\xc3\x87": "Ç",  # Ã‡ -> Ç
    "\xc4\x9f": "ğ",  # ÄŸ -> ğ
    "\xc4\x9e": "Ğ",  # Äž -> Ğ
    "\xc4\xb1": "ı",  # Ä± -> ı
    "\xc4\xb0": "İ",  # Ä° -> İ
    "\xc3\xb6": "ö",  # Ã¶ -> ö
    "\xc3\x96": "Ö",  # Ã– -> Ö
    "\xc5\x9f": "ş",  # ÅŸ -> ş
    "\xc5\x9e": "Ş",  # Åž -> Ş
    "\xc3\xbc": "ü",  # Ã¼ -> ü
    "\xc3\x9c": "Ü",  # Ãœ -> Ü

    # 2) Bilimsel sembol mojibake'ları -> ASCII
    "\xe2\x82\x82": "2",   # subscript 2
    "\xe2\x82\x83": "3",   # subscript 3
    "\xe2\x81\xba": "+",   # superscript plus
    "\xe2\x81\xbb": "-",   # superscript minus
    "\xc2\xb2": "2",       # superscript 2
    "\xc2\xb3": "3",       # superscript 3
    "\xc2\xb0": "°",       # derece işareti
    "\xc2\xb1": "±",       # artı-eksi işareti
    "Â±": "±",              # artı-eksi işareti (çift karakter mojibake)

    # 3) Emoji mojibake'ları
    "\xe2\x9a\xa0\xef\xb8\x8f": "⚠️",   # uyarı emojisi
    "âš ï¸": "⚠️",          # uyarı emojisi (çift karakter mojibake)
}

def repair_line(s: str) -> str:
    # Önce direkt harita değişimleri
    for bad, good in MOJIBAKE_MAP.items():
        s = s.replace(bad, good)

    # Görünmez kontrol karakterlerini temizle (printable olmayan ASCII)
    s = "".join(ch for ch in s if ch == "\n" or ch == "\t" or (ord(ch) >= 32 and ch != "\x7f"))
    return s

def process_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
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
