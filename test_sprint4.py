# test_sprint4.py - Sprint 4 Test Script
import sys
sys.path.insert(0, '.')

from constants import SAMPLE_CASES, REFERENCES, ACKNOWLEDGMENTS
from core import StewartInput, analyze_stewart

print("=" * 60)
print("SPRINT 4: PDF VAKA ENTEGRASYONU - TEST RAPORU")
print("=" * 60)

# Test 1: REFERENCES
print("\n[TEST 1] REFERENCES Kontrolu")
print(f"  - Toplam referans: {len(REFERENCES)}")
print(f"  - Akoglu referansi: {'OK' if 'akoglu_2024' in REFERENCES else 'FAIL'}")

# Test 2: ACKNOWLEDGMENTS
print("\n[TEST 2] ACKNOWLEDGMENTS Kontrolu")
print(f"  - ACKNOWLEDGMENTS mevcut: {'OK' if ACKNOWLEDGMENTS else 'FAIL'}")
print(f"  - Kategori sayisi: {len(ACKNOWLEDGMENTS)}")

# Test 3: Akoğlu Vakaları
print("\n[TEST 3] Akoglu Vakalari")
akoglu_cases = [k for k in SAMPLE_CASES.keys() if k.startswith('akoglu_')]
print(f"  - Toplam vaka: {len(akoglu_cases)}")
print(f"  - Beklenen: 5")
print(f"  - Durum: {'OK' if len(akoglu_cases) == 5 else 'FAIL'}")

# Test 4: Vaka Yapısı
print("\n[TEST 4] Vaka Yapisi Kontrolu")
for case_id in akoglu_cases:
    case = SAMPLE_CASES[case_id]
    has_classic = 'classic_interpretation' in case
    has_stewart = 'stewart_findings' in case
    has_values = 'values' in case and 'k' in case['values'] and 'be' in case['values']
    status = 'OK' if (has_classic and has_stewart and has_values) else 'FAIL'
    print(f"  - {case_id}: {status}")

# Test 5: Vaka Analizi
print("\n[TEST 5] Vaka Analizleri")
test_count = 0
pass_count = 0

for case_id in akoglu_cases:
    test_count += 1
    case = SAMPLE_CASES[case_id]
    try:
        inp = StewartInput(
            ph=case['values']['ph'],
            pco2=case['values']['pco2'],
            na=case['values']['na'],
            cl=case['values']['cl'],
            k=case['values'].get('k'),
            lactate=case['values'].get('lactate'),
            albumin_gl=case['values'].get('albumin_gl'),
            be=case['values'].get('be')
        )
        out, val = analyze_stewart(inp, 'quick')
        if val.is_valid:
            pass_count += 1
            print(f"  - {case_id}: OK (BE={out.be_used}, SID={out.sid_values.sid_simple})")
        else:
            print(f"  - {case_id}: FAIL (Validasyon hatasi)")
    except Exception as e:
        print(f"  - {case_id}: ERROR ({str(e)})")

# Sonuç
print("\n" + "=" * 60)
print("SONUC")
print("=" * 60)
print(f"Toplam test: {test_count}")
print(f"Basarili: {pass_count}")
print(f"Basarisiz: {test_count - pass_count}")
print(f"\nGENEL DURUM: {'TUM TESTLER BASARILI' if pass_count == test_count else 'BAZI TESTLER BASARISIZ'}")
print("=" * 60)
