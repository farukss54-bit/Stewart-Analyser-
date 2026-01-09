from constants import SAMPLE_CASES, ACKNOWLEDGMENTS
from core import StewartInput, analyze_stewart

print("Test 1: ACKNOWLEDGMENTS var mi:", ACKNOWLEDGMENTS is not None)
print("Test 2: Akoglu vakasi sayisi:", len([k for k in SAMPLE_CASES.keys() if k.startswith("akoglu_")]))

case = SAMPLE_CASES["akoglu_triple"]
inp = StewartInput(ph=7.48, pco2=60.2, na=132, cl=76, k=3.8, lactate=1.9, albumin_gl=18, be=7.6)
out, val = analyze_stewart(inp, "quick")
print("Test 3: Vaka analizi:", "BASARILI" if val.is_valid else "BASARISIZ")
print("Test 4: classic_interpretation var mi:", "classic_interpretation" in case)
print("Test 5: stewart_findings var mi:", "stewart_findings" in case)
print("
Tum testler basarili\!")
