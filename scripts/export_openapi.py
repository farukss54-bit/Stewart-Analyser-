"""
API şemasını web/openapi.json dosyasına yazar.

Arayüz tipleri bu dosyadan üretilir (web: npm run api:tipleri). API modelleri
değiştiğinde bu betik, ardından o komut çalıştırılmalıdır; güncel olup olmadığını
tests/test_api.py::test_committed_openapi_schema_is_current denetler.

Kullanım (depo kökünden):
    python scripts/export_openapi.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402

SCHEMA_PATH = ROOT / "web" / "openapi.json"


def render_schema() -> str:
    """Şemanın dosyaya yazılan biçimi (testler de aynı biçimi kullanır)."""
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    SCHEMA_PATH.write_text(render_schema(), encoding="utf-8", newline="\n")
    print(f"Yazıldı: {SCHEMA_PATH.relative_to(ROOT)}")
