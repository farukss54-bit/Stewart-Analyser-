# test_regression.py - Comprehensive Regression Tests for Critical Fixes
"""
Test vakalari master prompt'taki kritik sorunlari kontrol eder:
1. Primer respiratuvar bozukluklar taninip tanimlanmiyor mu?
2. SIG yanlis flaglenmiyor mu?
3. Celikili ciktilar var mi?
4. Kronik respiratuvar bozukluklar dogru tanimlanmiyor mu?
5. Mikst bozukluklar dogru tanimlanmiyor mu?
"""

import sys
sys.path.insert(0, '.')

from core import StewartInput, analyze_stewart

print("=" * 80)
print("REGRESSION TEST - KRITIK DUZELTMELERIN DOGRULANMASI")
print("=" * 80)

test_results = []

# === UTILITY FUNCTIONS ===

def run_test(test_name, inp, expected_dominant, should_have_sig_warning=None,
             should_have_respiratory=None, lactate_should_dominate=None,
             expected_components=None):
    """
    Test runner with structured assertions

    Args:
        test_name: Test adi
        inp: StewartInput
        expected_dominant: Beklenen dominant_disorder (str)
        should_have_sig_warning: SIG uyarisi olmali mi? (bool or None)
        should_have_respiratory: Respiratuvar bozukluk var mi? (str or None)
        lactate_should_dominate: Laktat dominant olmali mi? (bool or None)
        expected_components: Beklenen bozukluk bilesenleri (list or None)
    """
    print(f"\n[TEST] {test_name}")
    out, val = analyze_stewart(inp, 'quick')

    passed = True

    # Assertion 1: Dominant disorder kontrolu
    if expected_dominant:
        if out.dominant_disorder != expected_dominant:
            print(f"  FAIL: Expected dominant '{expected_dominant}', got '{out.dominant_disorder}'")
            passed = False
        else:
            print(f"  OK: Dominant disorder = {out.dominant_disorder}")

    # Assertion 2: SIG uyarisi kontrolu
    if should_have_sig_warning is not None:
        sig_warnings = [n for n in out.cds_notes if "olculmemin anyon" in n.note.lower() and n.category == "A"]
        has_sig_warning = len(sig_warnings) > 0

        if should_have_sig_warning and not has_sig_warning:
            print(f"  FAIL: SIG uyarisi bekleniyor ama YOK")
            passed = False
        elif not should_have_sig_warning and has_sig_warning:
            print(f"  FAIL: SIG uyarisi BEKLENMIYORDU ama VAR ({len(sig_warnings)} adet)")
            passed = False
        else:
            status = "var" if has_sig_warning else "yok"
            print(f"  OK: SIG uyarisi {status} (beklendigi gibi)")

    # Assertion 3: Respiratuvar bozukluk kontrolu
    if should_have_respiratory:
        if should_have_respiratory not in out.dominant_disorder:
            print(f"  FAIL: Expected respiratory '{should_have_respiratory}' in dominant, got '{out.dominant_disorder}'")
            passed = False
        else:
            print(f"  OK: Respiratuvar bozukluk '{should_have_respiratory}' dominant'ta bulundu")

    # Assertion 4: Laktat dominance kontrolu
    if lactate_should_dominate is not None:
        if out.mechanism_analysis and out.mechanism_analysis.dominant_mechanism:
            is_lactate_dominant = "laktat" in out.mechanism_analysis.dominant_mechanism.name.lower()
            if lactate_should_dominate and not is_lactate_dominant:
                print(f"  FAIL: Laktat dominant olmali ama degil (Dominant: {out.mechanism_analysis.dominant_mechanism.name})")
                passed = False
            elif not lactate_should_dominate and is_lactate_dominant:
                print(f"  FAIL: Laktat dominant OLMAMALI")
                passed = False
            else:
                print(f"  OK: Laktat dominance kontrolu basarili")

    # Assertion 5: Bozukluk bilesenleri kontrolu
    if expected_components:
        actual_components = set(out.disorder_components)
        expected_set = set(expected_components)

        if not expected_set.issubset(actual_components):
            missing = expected_set - actual_components
            print(f"  FAIL: Beklenen bilesenler eksik: {missing}")
            print(f"       Bulunan: {actual_components}")
            passed = False
        else:
            print(f"  OK: Tum beklenen bilesenler mevcut: {expected_components}")

    # Headline kontrolu (bilgilendirme)
    if out.headline:
        print(f"  INFO: Headline = {out.headline.dominant_mechanism}")

    test_results.append((test_name, passed))
    return passed


# === CATEGORY 1: PRIMER RESPIRATUVAR BOZUKLUKLAR ===

print("\n" + "=" * 80)
print("KATEGORI 1: PRIMER RESPIRATUVAR BOZUKLUKLAR")
print("=" * 80)

# Test 1: Akut Respiratuvar Alkaloz
run_test(
    "Akut Respiratuvar Alkaloz",
    StewartInput(ph=7.60, pco2=23.0, na=140.0, cl=102.0, hco3=21.8, be=0.3,
                 lactate=0.5, albumin_gl=40.0),
    expected_dominant="respiratory_alkalosis",
    should_have_sig_warning=False,
    should_have_respiratory="respiratory_alkalosis",
    expected_components=["respiratory_alkalosis"]
)

# Test 2: Izole Respiratuvar Asidoz (Akut)
run_test(
    "Akut Respiratuvar Asidoz",
    StewartInput(ph=7.29, pco2=55.0, na=140.0, cl=102.0, hco3=25.8, be=0.0),
    expected_dominant="respiratory_acidosis",
    should_have_sig_warning=False,
    should_have_respiratory="respiratory_acidosis",
    expected_components=["respiratory_acidosis"]
)

# Test 3: Kronik Respiratuvar Asidoz (KOAH)
print("\n[TEST] Kronik Respiratuvar Asidoz (KOAH)")
print("pH 7.35 | pCO2 65 | HCO3 35 | BE +8 (renal kompansasyon)")
run_test(
    "Kronik Respiratuvar Asidoz",
    StewartInput(ph=7.35, pco2=65.0, na=140.0, cl=98.0, hco3=35.0, be=8.0),
    expected_dominant="mixed_disorder",  # Renal kompansasyon = metabolik alkaloz + resp asidoz
    should_have_sig_warning=False,
    expected_components=["respiratory_acidosis"]
)

# Test 4: Kronik Respiratuvar Asidoz + Metabolik Asidoz (Mikst)
print("\n[TEST] Kronik Resp Asidoz + Metabolik Asidoz")
print("pH 7.25 | pCO2 60 | HCO3 26 | BE -3 (yetersiz kompansasyon)")
run_test(
    "Kronik Resp Asidoz + Met Asidoz",
    StewartInput(ph=7.25, pco2=60.0, na=140.0, cl=110.0, hco3=26.0, be=-3.0),
    expected_dominant="mixed_disorder",
    should_have_sig_warning=False,
    expected_components=["respiratory_acidosis", "hyperchloremic_acidosis"]
)

# === CATEGORY 2: METABOLIK BOZUKLUKLAR ===

print("\n" + "=" * 80)
print("KATEGORI 2: PRIMER METABOLIK BOZUKLUKLAR")
print("=" * 80)

# Test 5: Laktik Asidoz (laktat dominant, SIG yorumlanmamali)
run_test(
    "Laktik Asidoz",
    StewartInput(ph=7.33, pco2=30.0, na=140.0, cl=102.0, hco3=20.0, be=-4.7,
                 lactate=6.6, albumin_gl=40.0),
    expected_dominant="lactic_acidosis",
    should_have_sig_warning=False,  # Laktat aciklayici, SIG yorumlanmamali
    lactate_should_dominate=True
)

# Test 6: Metabolik Alkaloz (kusma, diuretik)
print("\n[TEST] Metabolik Alkaloz")
print("pH 7.52 | pCO2 48 | HCO3 38 | BE +12 | Cl 88 (hipokloremik)")
run_test(
    "Metabolik Alkaloz",
    StewartInput(ph=7.52, pco2=48.0, na=138.0, cl=88.0, hco3=38.0, be=12.0,
                 k=2.8, lactate=1.5, albumin_gl=44.0),
    expected_dominant="hypochloremic_alkalosis",
    should_have_sig_warning=False,
    expected_components=["hypochloremic_alkalosis"]
)

# === CATEGORY 3: MIKST BOZUKLUKLAR ===

print("\n" + "=" * 80)
print("KATEGORI 3: MIKST BOZUKLUKLAR")
print("=" * 80)

# Test 7: Metabolik Alkaloz + Respiratuvar Asidoz (Normal pH)
print("\n[TEST] Metabolik Alkaloz + Respiratuvar Asidoz (pH normal)")
print("pH 7.40 | pCO2 60 | HCO3 36 | BE +10 | Cl 90")
run_test(
    "Met Alkaloz + Resp Asidoz",
    StewartInput(ph=7.40, pco2=60.0, na=138.0, cl=90.0, hco3=36.0, be=10.0),
    expected_dominant="mixed_disorder",
    should_have_sig_warning=False,
    expected_components=["respiratory_acidosis", "hypochloremic_alkalosis"]
)

# Test 8: Metabolik Alkaloz + Kompansatuar Respiratuvar (yuksek pCO2 uygun)
print("\n[TEST] Metabolik Alkaloz + Uygun Kompansasyon")
print("pH 7.50 | pCO2 50 | HCO3 38 | BE +12 | Cl 88")
run_test(
    "Met Alkaloz + Uygun Komp",
    StewartInput(ph=7.50, pco2=50.0, na=138.0, cl=88.0, hco3=38.0, be=12.0),
    expected_dominant="hypochloremic_alkalosis",  # Kompansasyon mikst degil
    should_have_sig_warning=False
)

# Test 9: Triple Disorder (Met Asidoz + Met Alkaloz + Resp Asidoz)
print("\n[TEST] Triple Disorder")
print("pH 7.38 | pCO2 55 | BE -5 | Lac 3.0 | Alb 25 | Cl 105")
print("(Laktat asidoz + hipoalbumin alkaloz + resp asidoz)")
run_test(
    "Triple Disorder",
    StewartInput(ph=7.38, pco2=55.0, na=140.0, cl=105.0, hco3=32.0, be=-5.0,
                 lactate=3.0, albumin_gl=25.0),
    expected_dominant="mixed_disorder",
    should_have_sig_warning=False,
    expected_components=["respiratory_acidosis"]
)

# Test 10: Mikst Metabolik Asidoz (NAGMA + HAGMA)
print("\n[TEST] Mikst Metabolik Asidoz (NAGMA + HAGMA)")
print("pH 7.25 | pCO2 28 | BE -12 | Cl 110 | Lac 1.5")
run_test(
    "NAGMA + HAGMA (mikst met asidoz)",
    StewartInput(ph=7.25, pco2=28.0, na=140.0, cl=110.0, hco3=16.0, be=-12.0,
                 lactate=1.5, albumin_gl=40.0),
    expected_dominant="hyperchloremic_acidosis",  # NAGMA dominant
    should_have_sig_warning=False,  # Residual varsa yorumlanabilir ama ciddi asidozda
    expected_components=["hyperchloremic_acidosis"]
)

# === CATEGORY 4: SIG YORUMLAMA KURALLARI ===

print("\n" + "=" * 80)
print("KATEGORI 4: SIG YORUMLAMA KURALLARI")
print("=" * 80)

# Test 11: SIG pozitif ANCAK BE normal (SIG yorumlanmamali)
print("\n[TEST] SIG Pozitif ANCAK BE Normal")
print("pH 7.38 | BE +1 | SIG teorik olarak yuksek ama metabolik asidoz yok")
run_test(
    "SIG pozitif ama BE normal",
    StewartInput(ph=7.38, pco2=40.0, na=140.0, cl=102.0, hco3=24.0, be=1.0,
                 albumin_gl=40.0),
    expected_dominant="normal",
    should_have_sig_warning=False  # BE normal, SIG yorumlanmamali
)

# Test 12: SIG pozitif + Metabolik Asidoz + Laktat YUKSEK (SIG yorumlanmamali)
print("\n[TEST] SIG Pozitif + Laktat Yuksek")
print("Laktat aciklayici oldugu icin SIG yorumlanmamali")
run_test(
    "SIG + Yuksek Laktat",
    StewartInput(ph=7.28, pco2=30.0, na=140.0, cl=100.0, hco3=18.0, be=-8.0,
                 lactate=5.5, albumin_gl=40.0),
    expected_dominant="lactic_acidosis",
    should_have_sig_warning=False,  # Laktat aciklayici
    lactate_should_dominate=True
)

# === SONUC ===

print("\n" + "=" * 80)
print("TEST SONUCLARI")
print("=" * 80)

total_tests = len(test_results)
passed_tests = sum(1 for _, passed in test_results if passed)
failed_tests = total_tests - passed_tests

print(f"\nToplam Test: {total_tests}")
print(f"Basarili: {passed_tests}")
print(f"Basarisiz: {failed_tests}")

if failed_tests > 0:
    print("\nFAIL Basarisiz Testler:")
    for name, passed in test_results:
        if not passed:
            print(f"  - {name}")

print("\n" + "=" * 80)

if failed_tests == 0:
    print("OK TUM REGRESSION TESTLERI BASARILI!")
    print("\nDogrulamalar:")
    print("  + Primer respiratuvar bozukluklar taniniypr")
    print("  + Kronik respiratuvar bozukluklar dogru tanimlaniyor")
    print("  + SIG yanlis flaglenmiyor")
    print("  + Laktat varsa SIG yorumlanmiyor")
    print("  + Mikst bozukluklar dogru tespit ediliyor")
    print("  + Metabolik alkaloz + resp asidoz birlikte tanimlaniyor")
else:
    print("FAIL BAZI REGRESSION TESTLER BASARISIZ!")

print("=" * 80)

# Exit with proper code
sys.exit(0 if failed_tests == 0 else 1)
