"""
Streamlit arayüzünde cihaz BE'si: BD kutusu ve işaret denetimi.

1) BD kutusu: işaret çekirdekte YALNIZCA BİR KEZ çevrilmeli.
   Eski hata: arayüz işareti çevrilmiş BE'yi ve ayrıca BD bayrağını çekirdeğe gönderiyordu; çekirdek
   bayrağı bir kez daha uyguladığı için BD=5 girilen değer analizde +5.0 oluyordu (doğrusu −5.0).

2) İşaret denetimi yalnızca UYARIDIR (karar: Faruk). pH ile BE işareti çelişse bile analiz
   engellenmez; çünkü akut/kronik solunumsal bozuklukta bu birleşim fizyolojik olabilir
   (örn. KOAH alevlenmesi: pH 7.28, pCO₂ 68, BE +4).

Bu testler uygulamayı Streamlit'in kendi test aracıyla (AppTest) çalıştırır; sonuç ekranındaki
"BE" göstergesini okur.
"""

import logging
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _analiz(mod: str, ph: float, pco2: float, cihaz_be: float, bd: bool) -> AppTest:
    """Cihaz BE'sini girer ve analiz eder; çalışmış uygulamayı döndürür."""
    logging.disable(logging.CRITICAL)
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()

    if mod == "adv":
        at.sidebar.radio[0].set_value("Gelişmiş")
        at.run()
        on = "adv"
    else:
        on = "quick"

    at.number_input(key=f"{on}_ph").set_value(ph)
    at.number_input(key=f"{on}_pco2").set_value(pco2)
    at.run()
    at.checkbox(key=f"{on}_verify_mode").set_value(True)
    at.run()
    at.checkbox(key=f"{on}_be_verify").set_value(True)
    at.run()
    at.number_input(key=f"{on}_be_manual").set_value(cihaz_be)
    at.checkbox(key=f"{on}_is_bd").set_value(bd)
    at.run()

    dugme = next(b for b in at.button if "Analiz" in b.label)
    assert not dugme.disabled, "analiz düğmesi kapalı"
    dugme.click()
    at.run()
    assert not at.exception, at.exception
    return at


def _sonuc_be(at: AppTest) -> str:
    return next(m.value for m in at.metric if m.label == "BE")


@pytest.mark.parametrize("mod", ["quick", "adv"])
class TestBaseDeficitBoxIsAppliedOnce:
    def test_bd_with_positive_entry_is_negative_in_analysis(self, mod):
        """pH 7.20, cihaz 'baz açığı 5' (BD işaretli) -> analizde BE = −5.0."""
        assert _sonuc_be(_analiz(mod, 7.20, 31.0, 5.0, bd=True)) == "-5.0"

    def test_bd_gives_same_result_as_entering_the_negative_be_directly(self, mod):
        bd = _sonuc_be(_analiz(mod, 7.20, 31.0, 5.0, bd=True))
        dogrudan = _sonuc_be(_analiz(mod, 7.20, 31.0, -5.0, bd=False))
        assert bd == dogrudan


@pytest.mark.parametrize("mod", ["quick", "adv"])
class TestSignMismatchOnlyWarns:
    def test_copd_case_is_not_blocked_and_uses_the_entered_be(self, mod):
        """KOAH: pH 7.28, pCO₂ 68, BE +4.0 girilince uyarı çıkar, analiz YAPILIR ve BE +4.0 kullanılır."""
        at = _analiz(mod, 7.28, 68.0, 4.0, bd=False)
        assert _sonuc_be(at) == "+4.0"
        # "İşaret" Python'da lower() ile "işaret"e dönüşmez (Türkçe İ); harf büyüklüğünden bağımsız parça aranır
        assert any("hatası olabilir" in w.value for w in at.warning), "uyarı gösterilmedi"
        assert not any("analiz yapılamaz" in e.value.lower() for e in at.error), "analiz engelleniyor"
