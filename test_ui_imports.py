"""UI modülleri için import-düzeyi smoke testleri.

Kapsam: import-zamanı hatalarını yakalar (syntax, modül düzeyi
tanımsız isim, bozuk import). NOT: Fonksiyon GÖVDESİ içindeki
çalışma-zamanı hatalarını (ör. kaldırılmış bir alana referans)
yakalamaz — onun için ileride streamlit AppTest gerekir.
"""

import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")


def test_ui_components_imports():
    import ui_components  # noqa: F401


def test_visualization_imports():
    import visualization  # noqa: F401
