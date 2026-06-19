"""cds_differential.py
Deterministik CDS diferansiyel modülü.

Bu modül, mevcut CDS_NOTES'te yer alan Stewart mekanizma notlarını
TEKRARLAMAZ. Amacı, hesaplanan asit-baz paternine göre etiyolojik
diferansiyel listeleri ve hesaplanamayan parametrelere dayalı önerilen
tetkikleri (ör. idrar anyon gap, idrar Cl, osmol gap) sunmaktır.

Tüm çıktılar non-diagnostiktir: "... ile uyumlu olabilir", "... düşünülebilir".
"""

from typing import Any, Dict, List, Optional

from constants import (
    AG_NORMAL,
    LACTATE_THRESHOLD,
)

# =============================================================================
# VERIFIED_REFS — references.md'deki teyitli referanslar (birebir)
# =============================================================================
VERIFIED_REFS = {
    "R1": (
        "Figge J, Jabor A, Kazda A, Fencl V. Anion gap and hypoalbuminemia. "
        "Crit Care Med. 1998;26(11):1807-10. PMID:9824071. "
        "doi:10.1097/00003246-199811000-00019"
    ),
    "R2": (
        "Fencl V, Jabor A, Kazda A, Figge J. Diagnosis of metabolic acid-base "
        "disturbances in critically ill patients. Am J Respir Crit Care Med. "
        "2000;162(6):2246-51. PMID:11112147. doi:10.1164/ajrccm.162.6.9904099"
    ),
    "R3": (
        "Kraut JA, Madias NE. Serum anion gap: its uses and limitations in "
        "clinical medicine. Clin J Am Soc Nephrol. 2007;2(1):162-74. "
        "PMID:17699401. doi:10.2215/CJN.03020906"
    ),
    "R4": (
        "Chawla LS, Shih S, Davison D, Junker C, Seneff MG. Anion gap, anion "
        "gap corrected for albumin, base deficit and unmeasured anions in "
        "critically ill patients. BMC Emerg Med. 2008;8:18. PMID:19087326. "
        "doi:10.1186/1471-227X-8-18"
    ),
    "R5": (
        "Lynd LD, Richardson KJ, Purssell RA, Abu-Laban RB, Brubacher JR, "
        "Lepik KJ, Sivilotti MLA. An evaluation of the osmole gap as a screening "
        "test for toxic alcohol poisoning. BMC Emerg Med. 2008;8:5. "
        "PMID:18442409. doi:10.1186/1471-227X-8-5"
    ),
    "R6": (
        "Krasowski MD, Wilcoxon RM, Miron J. A retrospective analysis of glycol "
        "and toxic alcohol ingestion: utility of anion and osmolal gaps. "
        "BMC Clin Pathol. 2012;12:1. PMID:22240170. doi:10.1186/1472-6890-12-1"
    ),
    "R7": (
        "Khajuria A, Krahn J. Osmolality revisited — deriving and validating "
        "the best formula for calculated osmolality. Clin Biochem. "
        "2005;38(6):514-9. PMID:15885229. doi:10.1016/j.clinbiochem.2005.03.001"
    ),
    "R-LITFL": (
        "CATMUDPILES. Life in the Fast Lane (LITFL). "
        "[web; https://litfl.com/catmudpile/]"
    ),
}


# =============================================================================
# Diferansiyel bilgi tabanı
# =============================================================================
DIFFERENTIAL_KNOWLEDGE = {
    "respiratory_acidosis_etiology": {
        "trigger": {
            "match": "any",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "respiratory_acidosis"},
                {"param": "disorder_components", "op": "contains", "value": "respiratory_acidosis"},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Solunumsal asidoz yönünde patern (hipoventilasyon)",
        "differentials": [
            "Kronik akciğer hastalıkları (KOAH, kronik pnömoni, interstisyel akciğer hastalığı, idiyopatik pulmoner fibroz)",
            "Akut pulmoner hastalıklar (pnömoni, pulmoner ödem, aspirasyon pnömoniti, astım alevlenmesi)",
            "Havayolu obstrüksiyonu",
            "Nöromusküler hastalıklar (ALS, Guillain-Barre sendromu, miyastenia gravis, musküler distrofiler)",
            "Toraks duvarı / plevra bozuklukları (pnömotoraks, flail chest, toraks travması)",
            "Santral solunum depresyonu (opiyat, barbitürat, benzodiazepin, intrakraniyal patoloji)",
            "Obezite-hipoventilasyon (Pickwickian) sendromu",
            "Hipodinamik şok / doku hipoksisi (uzun süreli veya şiddetli)",
        ],
        "suggested_tests": [],
        "refs": [],
        "factcheck_status": "confirmed",
    },
    "respiratory_alkalosis_etiology": {
        "trigger": {
            "match": "any",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "respiratory_alkalosis"},
                {"param": "disorder_components", "op": "contains", "value": "respiratory_alkalosis"},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Solunumsal alkaloz yönünde patern (hiperventilasyon)",
        "differentials": [
            "Hipoksemi (pnömoni, pulmoner ödem, pulmoner emboli, ciddi anemi, ventilasyon-perfüzyon uyumsuzluğu)",
            "Santral hiperventilasyon (KİBAS, intrakraniyal kanama, travma, SVO)",
            "Hepatik ensefalopati",
            "Sepsis",
            "Gebelik",
            "Salisilat intoksikasyonu",
            "Katekolaminler, kafein, nikotin",
            "Yüksek rakım / hipoksiye bağlı hiperventilasyon",
            "İstemli veya psikojenik hiperventilasyon",
        ],
        "suggested_tests": [],
        "refs": [],
        "factcheck_status": "confirmed",
    },
    "metabolic_alkalosis_subtypes": {
        "trigger": {
            "match": "any",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "metabolic_alkalosis"},
                {"param": "disorder_components", "op": "contains", "value": "metabolic_alkalosis"},
            ],
        },
        "paradigm": "stewart",
        "mechanism": "Güçlü iyon (SID) artışına bağlı metabolik alkaloz yönünde patern",
        "differentials": [
            "Klor-yanıtlı metabolik alkaloz: kusma, GİS drenaj, diüretik kullanımı sonrası, kontraksiyon alkalozu, post-hiperkapni",
            "Klor-dirençli metabolik alkaloz: primer/sekonder hiperaldosteronizm, Cushing sendromu, Bartter sendromu, Liddle sendromu, eksojen kortikosteroid kullanımı",
            "Eksojen sodyum yüklenmesi: sodyum asetat, sodyum sitrat, Ringer laktat, masif kan transfüzyonu, plazma hacim genişleticileri",
        ],
        "suggested_tests": [
            {
                "consider": "İdrar klorürü",
                "to_differentiate": "Klor-yanıtlı vs klor-dirençli metabolik alkaloz",
                "note": (
                    "İdrar Cl < 10 mEq/L hacim yetersizliği/kusma ile uyumlu olabilir; "
                    "> 20 mEq/L mineralokortikoid fazlalığı ile uyumlu olabilir."
                ),
            },
        ],
        "refs": ["R2"],
        "factcheck_status": "confirmed",
    },
    "nagma_pattern": {
        "trigger": {
            "match": "all",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "metabolic_acidosis"},
                {"param": "anion_gap", "op": "lte", "value": AG_NORMAL},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Normal anyon gap'li (hiperkloremik) metabolik asidoz ile uyumlu patern",
        "differentials": [
            "Renal tübüler asidoz (Tip 1 distal, Tip 2 proksimal, Tip 4 hiperkalemik)",
            "GİS bikarbonat kaybı (diyare, pankreatit, üreterostomi, ileostomi, kolostomi, enterik fistül)",
            "Salin infüzyonu / dilüsyonel asidoz",
            "İyon değiştirici reçineler",
            "TPN komplikasyonları",
        ],
        "suggested_tests": [
            {
                "consider": "İdrar anyon gap (Na + K − Cl)",
                "to_differentiate": "RTA vs GİS bikarbonat kaybı",
                "note": (
                    "Pozitif idrar AG düşük NH4+ atılımı (RTA) ile, negatif idrar AG "
                    "artmış NH4+ atılımı (GİS kaybı) ile uyumlu olabilir."
                ),
            },
            {
                "consider": "İdrar pH",
                "to_differentiate": "Distal vs proksimal RTA",
                "note": (
                    "Distal RTA'da metabolik asidoza rağmen idrar pH > 5,5 kalabilir. "
                    "Proksimal RTA'da idrar asidik (< 5,5) olabilir; ancak bikarbonat "
                    "yüklemesi sonrası > 7,5'e çıkabilir."
                ),
            },
        ],
        "refs": ["R3"],
        "factcheck_status": "confirmed",
    },
    "lactic_acidosis_classification": {
        "trigger": {
            "match": "all",
            "conditions": [
                {"param": "lactate_effect", "op": "lt", "value": -LACTATE_THRESHOLD},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Laktat artışına bağlı asidoz yükü ile uyumlu patern",
        "differentials": [
            "Tip A (doku hipoksisi/hipoperfüzyon): şok, iskemi, ciddi hipoksemi, doku hipoksisi",
            "Tip B (hipoksisiz): sistemik hastalık, ilaçlar/toksinler (metformin, salisilat, alkol), kalıtsal metabolik bozukluklar",
            "Karaciğer yetmezliğine bağlı laktat atılımında bozulma (bazı kaynaklarda Tip B1 altında)",
        ],
        "suggested_tests": [],
        "refs": [],
        "factcheck_status": "confirmed",
    },
    "hagma_cat_mud_piles": {
        "trigger": {
            "match": "all",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "metabolic_acidosis"},
                {"param": "anion_gap", "op": "gt", "value": AG_NORMAL},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Yüksek anyon gap'li metabolik asidoz ile uyumlu patern",
        "differentials": [
            "C — Cyanide, carbon monoxide, congenital heart disease",
            "A — Alcoholic ketoacidosis",
            "T — Toluene, theophylline",
            "M — Methanol, metformin",
            "U — Uraemia (üremi / böbrek yetmezliği)",
            "D — Diabetic ketoacidosis",
            "P — Phenformin, pyroglutamic acid, paraldehyde, propylene glycol, paracetamol",
            "I — Iron, isoniazid, inborn errors of metabolism",
            "L — Lactic acidosis",
            "E — Ethanol, ethylene glycol",
            "S — Salicylates",
        ],
        "suggested_tests": [],
        "refs": ["R-LITFL"],
        "factcheck_status": "confirmed",
    },
    "osmol_gap_toxic_alcohol": {
        "trigger": {
            "match": "all",
            "conditions": [
                {"param": "dominant_disorder", "op": "eq", "value": "metabolic_acidosis"},
                {"param": "anion_gap", "op": "gt", "value": AG_NORMAL},
            ],
        },
        "paradigm": "classical",
        "mechanism": "Yüksek anyon gap'li asidozda toksik alkol farkındalığı",
        "differentials": [
            "Metanol (formik asit metaboliti ile HAGMA + görme bulguları)",
            "Etilen glikol (oksalik asit/glikolik asit metabolitleri ile HAGMA + kalsiyum oksalat kristalüri)",
            "İzopropil alkol (asetona metabolize olur, HAGMA yapmaz; osmol gap artışı)",
            "Propilen glikol (lorazepam/diazepam çözücüsü; laktat ve osmol gap artışı)",
        ],
        "suggested_tests": [
            {
                "consider": "Serum ozmolalitesi (ölcülen) ve osmol gap",
                "to_differentiate": "Toksik alkol maruziyeti",
                "note": (
                    "Ozmol gap > 10 mOsm/kg anormal kabul edilir; > 50 mOsm/kg toksik "
                    "alkol maruziyeti ile güçlü ilişkili olabilir. Formülde kullanılan "
                    "birim sistemi (mg/dL veya SI) klinik laboratuvara göre ayarlanmalıdır."
                ),
            },
            {
                "consider": "Toksik alkol / metabolit düzeyleri",
                "to_differentiate": "Metanol, etilen glikol, izopropil alkol",
                "note": "Kesin ayırım için spesifik düzeyler ve klinik görünüm değerlendirilmelidir.",
            },
        ],
        "refs": ["R5", "R6", "R7"],
        "factcheck_status": "confirmed",
    },
}


# =============================================================================
# Trigger değerlendirme motoru
# =============================================================================
def _get_value(obj: Any, param: str) -> Any:
    """Noktalı parametre adlarını destekleyen güvenli getattr.

    Örn. 'sid_values.sid_simple' → obj.sid_values.sid_simple
    'disorder_components' → obj.disorder_components
    """
    parts = param.split(".")
    value = obj
    for part in parts:
        if value is None:
            return None
        value = getattr(value, part)
    return value


def _evaluate_condition(condition: Dict[str, Any], core_output: Any) -> bool:
    """Tek bir koşul ifadesini değerlendir.

    op değerleri:
        lt, lte, gt, gte: karşılaştırma
        eq: eşitlik
        contains: liste/string içeriyor mu
        abs_gt: mutlak değer eşikten büyük mü
    """
    param = condition["param"]
    op = condition["op"]
    value = condition.get("value")
    actual = _get_value(core_output, param)

    if actual is None:
        return False

    if op == "lt":
        return actual < value
    if op == "lte":
        return actual <= value
    if op == "gt":
        return actual > value
    if op == "gte":
        return actual >= value
    if op == "eq":
        return actual == value
    if op == "contains":
        return value in actual
    if op == "abs_gt":
        return abs(actual) > value

    raise ValueError(f"Bilinmeyen op: {op}")


def _evaluate_trigger(trigger: Dict[str, Any], core_output: Any) -> bool:
    """Bir trigger sözlüğünü (match + conditions) değerlendir."""
    match = trigger.get("match", "all")
    conditions = trigger["conditions"]

    if not conditions:
        return False

    results = [_evaluate_condition(c, core_output) for c in conditions]

    if match == "all":
        return all(results)
    if match == "any":
        return any(results)

    raise ValueError(f"Bilinmeyen match: {match}")


# =============================================================================
# Ana değerlendirme fonksiyonu
# =============================================================================
def evaluate_differentials(core_output: Any) -> List[Dict[str, Any]]:
    """Hesaplanan Stewart çıktısına göre etiyolojik diferansiyelleri döndür.

    Args:
        core_output: StewartOutput nesnesi veya uyumlu bir veri sınıfı.

    Returns:
        Eşleşen her diferansiyel girişi için normalize edilmiş dict listesi.
        Her dict: key, paradigm, mechanism, differentials, suggested_tests, refs,
        factcheck_status içerir.
    """
    results: List[Dict[str, Any]] = []

    for key, entry in DIFFERENTIAL_KNOWLEDGE.items():
        if _evaluate_trigger(entry["trigger"], core_output):
            results.append(
                {
                    "key": key,
                    "paradigm": entry["paradigm"],
                    "mechanism": entry["mechanism"],
                    "differentials": list(entry["differentials"]),
                    "suggested_tests": [dict(t) for t in entry.get("suggested_tests", [])],
                    "refs": [ref for ref in entry.get("refs", [])],
                    "factcheck_status": entry.get("factcheck_status", "unverified"),
                }
            )

    return results
