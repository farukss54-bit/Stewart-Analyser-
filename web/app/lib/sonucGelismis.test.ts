import { describe, expect, it } from "vitest";
import {
  anyonAcigi,
  girilmeyenDegerler,
  mekanizmaSatirlari,
  sidMerdiveni,
  sigEtiketi,
  sigYorumu,
  type Sonuc,
} from "./sonuc";

// Gelişmiş mod sonuç mantığı. Sonuç değerleri çekirdeğin gerçek çıktısından alındı
// (pH 7.30, pCO₂ 30, Na 136, Cl 106; üç farklı veri durumu).

// /api/meta referansları (api/main.py: normal ± SID_NORMAL_RANGE)
const SID_ARALIKLARI = {
  sid_simple: { low: 36, high: 40 },
  sid_basic: { low: 35, high: 39 },
  sid_full: { low: 40, high: 44 },
};

// Tüm değerler girildi: K 5.6, laktat 1.8, Ca 1.10, Mg 0.95, fosfat 1.9, albümin 32
const TAM_VERI = {
  sid_values: {
    sid_simple: 30.0,
    sid_simple_status: "measured",
    sid_basic: 28.2,
    sid_basic_status: "measured",
    sid_full: 37.9,
    sid_full_status: "complete",
    sid_full_missing: [],
  },
  sid_effective: 26.2,
  sig: 11.7,
  sig_interpretation: "Ölçülmemiş anyonlar mevcut (unmeasured anions likely)",
  anion_gap: 15.7,
  anion_gap_corrected: 18.2,
} as unknown as Sonuc;

// Yalnızca laktat 3.5 ve albümin 22 girildi; K, Ca, Mg, fosfat yok
const EKSIK_VERI = {
  sid_values: {
    sid_simple: 30.0,
    sid_simple_status: "measured",
    sid_basic: 26.5,
    sid_basic_status: "measured",
    sid_full: 26.5,
    sid_full_status: "incomplete",
    sid_full_missing: ["K+", "Ca2+", "Mg2+"],
  },
  sid_effective: 20.2,
  sig: 6.3,
  sig_interpretation: "Ölçülmemiş anyonlar mevcut (unmeasured anions likely)",
  anion_gap: 15.7,
  anion_gap_corrected: 20.7,
} as unknown as Sonuc;

// Laktat ve albümin de girilmedi
const BOS_VERI = {
  sid_values: {
    sid_simple: 30.0,
    sid_simple_status: "measured",
    sid_basic: null,
    sid_basic_status: "lactate_missing",
    sid_full: 30.0,
    sid_full_status: "incomplete",
    sid_full_missing: ["K+", "Ca2+", "Mg2+", "Laktat"],
  },
  sid_effective: 14.3,
  sig: 15.7,
  sig_interpretation: "Ölçülmemiş anyonlar mevcut (unmeasured anions likely)",
  anion_gap: 15.7,
  anion_gap_corrected: null,
} as unknown as Sonuc;

describe("girilmeyenDegerler / sigEtiketi", () => {
  const TAM_ISTEK = { lactate: 1.8, albumin: 32, k: 5.6, ca: 1.1, mg: 0.95, po4: 1.9 };

  it("her şey girildiyse etiket veri durumunu söyler", () => {
    expect(girilmeyenDegerler(TAM_ISTEK)).toEqual([]);
    expect(sigEtiketi(TAM_ISTEK)).toEqual({ metin: "Tam veriyle hesaplandı", tam: true });
  });

  it("girilmeyenleri ekrandaki sırayla sayar", () => {
    expect(girilmeyenDegerler({ ...TAM_ISTEK, ca: undefined, mg: undefined }).map((e) => e.ad)).toEqual(["Ca", "Mg"]);
  });

  it("karar örnekleri: Ca ve Mg / Albümin / Laktat girilmedi", () => {
    expect(sigEtiketi({ ...TAM_ISTEK, ca: undefined, mg: undefined }).metin).toBe("Ca ve Mg girilmedi");
    expect(sigEtiketi({ ...TAM_ISTEK, albumin: undefined }).metin).toBe("Albümin girilmedi");
    expect(sigEtiketi({ ...TAM_ISTEK, lactate: undefined }).metin).toBe("Laktat girilmedi");
  });

  it("K⁺ ve fosfat eksikliğini de söyler (çekirdeğin güvenilirlik alanı bunları saymaz)", () => {
    expect(sigEtiketi({ ...TAM_ISTEK, k: undefined, po4: undefined })).toEqual({
      metin: "K ve fosfat girilmedi",
      tam: false,
    });
  });

  it("ikiden çok eksikte virgül ve 've' kullanır; null da girilmemiş sayılır", () => {
    const etiket = sigEtiketi({ lactate: null, albumin: null });
    expect(etiket.metin).toBe("Laktat, albümin, K, Ca, Mg ve fosfat girilmedi");
  });
});

describe("sigYorumu", () => {
  it("çekirdeğin parantez içindeki İngilizce kısmını atar", () => {
    expect(sigYorumu(TAM_VERI)).toBe("Ölçülmemiş anyonlar mevcut");
  });

  it("parantezsiz yorumu olduğu gibi bırakır; yoksa boş döner", () => {
    expect(sigYorumu({ sig_interpretation: "Normal / klinik olarak önemsiz" } as Sonuc)).toBe(
      "Normal / klinik olarak önemsiz",
    );
    expect(sigYorumu({} as Sonuc)).toBe("");
  });
});

describe("sidMerdiveni", () => {
  it("tam veride dört basamak, tam katman eksiksiz; normal değer bandın ortasıdır", () => {
    const m = sidMerdiveni(TAM_VERI, SID_ARALIKLARI)!;
    expect(m.basamaklar.map((b) => [b.kimlik, b.deger, b.normal, b.eksik])).toEqual([
      ["simple", 30, 38, false],
      ["basic", 28.2, 37, false],
      ["full", 37.9, 42, false],
      ["effective", 26.2, null, false],
    ]);
    expect(m.basamaklar[2].ad).toBe("… + K⁺ + Ca²⁺ + Mg²⁺");
    expect(m.sig).toEqual({ deger: 11.7, baslangic: 26.2, bitis: 37.9 });
    expect(m.olcek).toEqual({ min: 15, max: 45 });
  });

  it("tam katman eksik veriyle hesaplandıysa işaretlenir", () => {
    const tam = sidMerdiveni(EKSIK_VERI, SID_ARALIKLARI)!.basamaklar[2];
    expect(tam.eksik).toBe(true);
    expect(tam.ad).toBe("… + K⁺ + Ca²⁺ + Mg²⁺ (eksik)");
  });

  it("laktat girilmediyse temel katman değersizdir ve nedenini söyler", () => {
    const temel = sidMerdiveni(BOS_VERI, SID_ARALIKLARI)!.basamaklar[1];
    expect(temel.deger).toBeNull();
    expect(temel.alt).toBe("Laktat girilmedi");
  });

  it("SIG negatifse aralık etkin SID'nin altına uzanır", () => {
    const m = sidMerdiveni({ ...TAM_VERI, sig: -3 } as Sonuc, SID_ARALIKLARI)!;
    expect(m.sig.deger).toBe(-3);
    expect(m.sig.bitis).toBe(26.2);
    expect(m.sig.baslangic).toBeCloseTo(23.2);
  });

  it("ölçek, değerler 15–45'in dışına taşarsa 5'in katlarıyla genişler", () => {
    const m = sidMerdiveni(
      { ...TAM_VERI, sid_effective: 8, sig: 2, sid_values: { ...TAM_VERI.sid_values, sid_simple: 52 } } as Sonuc,
      SID_ARALIKLARI,
    )!;
    expect(m.olcek).toEqual({ min: 5, max: 55 });
  });

  it("hızlı mod sonucunda (SIG yok) null döner", () => {
    expect(sidMerdiveni({ ...TAM_VERI, sig: null, sid_effective: null } as Sonuc, SID_ARALIKLARI)).toBeNull();
  });
});

describe("anyonAcigi", () => {
  const NORMAL = { low: 3, high: 11 };

  it("ikisi de eşiğin üstündeyse düzeltmenin yönünü söyler", () => {
    const a = anyonAcigi(TAM_VERI, NORMAL, 15);
    expect([a.olculen, a.duzeltilmis]).toEqual([15.7, 18.2]);
    expect(a.metin).toBe(
      "İkisi de tarama eşiğinin (15) üstünde. Albümin düşük olduğu için düzeltilmiş değer ölçülenden büyük.",
    );
    expect(a.olcek).toEqual({ min: 0, max: 30 });
  });

  it("ölçülen eşiğin altında, düzeltilmiş üstündeyse bunu söyler", () => {
    const a = anyonAcigi({ ...TAM_VERI, anion_gap: 11.7, anion_gap_corrected: 16.7 } as Sonuc, NORMAL, 15);
    expect(a.metin).toBe("Ölçülen değer tarama eşiğinin (15) altında; albümine göre düzeltilince eşiğin üstüne çıkıyor.");
  });

  it("ölçülen eşiğin üstünde, düzeltilmiş altındaysa bunu söyler", () => {
    const a = anyonAcigi({ ...TAM_VERI, anion_gap: 16, anion_gap_corrected: 13 } as Sonuc, NORMAL, 15);
    expect(a.metin).toBe("Ölçülen değer tarama eşiğinin (15) üstünde; albümine göre düzeltilince eşiğin altına iniyor.");
  });

  it("ikisi de altındaysa ve albümin yüksekse düzeltmenin küçülttüğünü söyler", () => {
    const a = anyonAcigi({ ...TAM_VERI, anion_gap: 12, anion_gap_corrected: 10 } as Sonuc, NORMAL, 15);
    expect(a.metin).toBe(
      "İkisi de tarama eşiğinin (15) altında. Albümin yüksek olduğu için düzeltilmiş değer ölçülenden küçük.",
    );
  });

  it("albümin girilmediyse düzeltilmiş değer yoktur ve nedeni yazılır", () => {
    const a = anyonAcigi(BOS_VERI, NORMAL, 15);
    expect(a.duzeltilmis).toBeNull();
    expect(a.metin).toBe(
      "Ölçülen değer tarama eşiğinin (15) üstünde. Albümin girilmediği için düzeltilmiş değer hesaplanamadı.",
    );
  });

  it("karşılaştırma ekranda yazılan değerle yapılır: 15.04 → 15.0 eşiğin üstünde sayılmaz", () => {
    const a = anyonAcigi({ ...TAM_VERI, anion_gap: 15.04, anion_gap_corrected: 15.04 } as Sonuc, NORMAL, 15);
    expect(a.metin).toContain("altında");
  });

  it("çok yüksek değerde ölçek genişler", () => {
    expect(anyonAcigi({ ...TAM_VERI, anion_gap: 34, anion_gap_corrected: 40 } as Sonuc, NORMAL, 15).olcek.max).toBe(45);
  });
});

describe("açıklanamayan kalan satırının varsayılan metni", () => {
  const SONUC = {
    sid_effect: -8,
    albumin_effect: 5,
    lactate_effect: -3.5,
    residual_effect: -4.3,
    mechanism_analysis: { all_mechanisms: [] },
  } as unknown as Sonuc;
  const artik = (gelismis: boolean) => mekanizmaSatirlari(SONUC, 2, gelismis).find((x) => x.kimlik === "residual")!.metin;

  it("hızlı modda ölçülmemiş anyonlar için gelişmiş modu önerir", () => {
    expect(artik(false)).toContain("gelişmiş mod gerekir");
  });

  it("gelişmiş modda (zaten gelişmiş moddayız) SIG satırına yönlendirir", () => {
    expect(artik(true)).toBe("Diğer mekanizmaların açıklamadığı pay. Ölçülmemiş anyonlar için SIG satırına bakın.");
  });
});
