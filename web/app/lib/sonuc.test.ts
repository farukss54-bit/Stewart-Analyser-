import { describe, expect, it } from "vitest";
import {
  cubukYariGenisligi,
  degerDurumu,
  DEGERLER,
  gosterilenDeger,
  klasikKarsilastirma,
  mekanizmaSatirlari,
  normalMetni,
  notGruplari,
  ozetSatirlari,
  toplamEtki,
  uyarilar,
  yuzde,
  type Sonuc,
} from "./sonuc";

const ESIK = 2;

function mekanizma(kimlik: string, etki: number, seviye: string, aciklama: string) {
  return {
    name: kimlik,
    identifier: kimlik,
    effect_meq: etki,
    contribution_percent: 0,
    level: seviye,
    direction: etki < 0 ? "acidosis" : "alkalosis",
    description: aciklama,
  };
}

// Tasarım örneği (pH 7.30, pCO₂ 31, Na 141, Cl 114, laktat 2.8, albümin 25): çekirdeğin gerçek çıktısından
const ORNEK = {
  be_used: -10.4,
  be_source: "calculated",
  sid_effect: -11.0,
  albumin_effect: 4.2,
  lactate_effect: -2.8,
  residual_effect: -0.8,
  compensation_details: "Beklenen pCO2: 30 ± 2",
  warnings: ["K⁺, Ca²⁺ ve Mg²⁺ girilmedi; ileri analiz için Gelişmiş mod gerekir."],
  soft_warnings: [],
  headline: {
    dominant_mechanism: "Güçlü iyon (SID) aracılı metabolik asidoz (−11.0 mEq/L)",
    significant_mechanisms: ["Zayıf asit azalması (hipoalbüminemi) etkisi (+4.2 mEq/L)"],
    contributing_mechanisms: ["Laktat aracılı etki (−2.8 mEq/L)"],
    respiratory_status: "Uygun solunumsal kompanzasyon",
  },
  mechanism_analysis: {
    total_metabolic_effect: -10.4,
    all_mechanisms: [
      mekanizma("sid", -11.0, "dominant", "Güçlü iyon (SID) aracılı metabolik asidoz"),
      mekanizma("albumin", 4.2, "significant", "Zayıf asit azalması (hipoalbüminemi) etkisi"),
      mekanizma("lactate", -2.8, "contributing", "Laktat aracılı metabolik asidoz mekanizması"),
    ],
  },
} as unknown as Sonuc;

function sonuc(degisiklik: Record<string, unknown>): Sonuc {
  return { ...(ORNEK as object), ...degisiklik } as Sonuc;
}

describe("mekanizmaSatirlari", () => {
  const satirlar = mekanizmaSatirlari(ORNEK, ESIK);

  it("dört satır verir ve etkilerin toplamı ölçülen baz açığını tutar", () => {
    expect(satirlar.map((s) => s.kimlik)).toEqual(["sid", "albumin", "lactate", "residual"]);
    const toplam = satirlar.reduce((t, s) => t + s.etki, 0);
    expect(toplam).toBeCloseTo(-10.4, 5);
  });

  it("yönü etkinin işaretinden alır", () => {
    expect(satirlar.map((s) => s.yon)).toEqual(["asit", "baz", "asit", "asit"]);
  });

  it("Baskın/Anlamlı etiketini ve açıklamayı çekirdeğin listesinden alır", () => {
    expect(satirlar[0]).toMatchObject({ etiket: "Baskın", metin: "Güçlü iyon (SID) aracılı metabolik asidoz" });
    expect(satirlar[1].etiket).toBe("Anlamlı");
    expect(satirlar[2].etiket).toBeNull(); // "contributing": etiketsiz
  });

  it("eşiği aşmayan etkiyi küçük sayar (eşiğin kendisi de küçüktür)", () => {
    expect(satirlar.map((s) => s.kucuk)).toEqual([false, false, false, true]);
    const sinirda = mekanizmaSatirlari(sonuc({ sid_effect: 2.0 }), ESIK);
    expect(sinirda[0].kucuk).toBe(true);
  });

  it("çekirdeğin listesinde olmayan artığı da gösterir (toplam BE'yi tutsun)", () => {
    const dka = sonuc({
      be_used: -18,
      sid_effect: -4.0,
      albumin_effect: null,
      lactate_effect: -2.2,
      residual_effect: -11.8,
      mechanism_analysis: { total_metabolic_effect: -18, all_mechanisms: [] },
    });
    const s = mekanizmaSatirlari(dka, ESIK);
    expect(s.map((x) => x.kimlik)).toEqual(["sid", "lactate", "residual"]);
    const artik = s[2];
    expect(artik).toMatchObject({ etki: -11.8, kucuk: false, etiket: null });
    // Albümin girilmediği için artık onun payını da içerir: soluk çizilir ve bu söylenir
    expect(artik.soluk).toBe(true);
    expect(artik.metin).toBe("Girilmeyen albümin etkisini de içerir; ayrı yorumlanmamalıdır.");
    expect(s.reduce((t, x) => t + x.etki, 0)).toBeCloseTo(-18, 5);
  });

  it("çekirdek ölçülmemiş bileşeni yorumladıysa artık satırı onun etiketini ve metnini taşır", () => {
    const s = mekanizmaSatirlari(
      sonuc({
        residual_effect: 4.2,
        mechanism_analysis: {
          total_metabolic_effect: -8,
          all_mechanisms: [mekanizma("unmeasured", 4.2, "significant", "Ölçülmemiş katyon aracılı etki")],
        },
      }),
      ESIK,
    );
    expect(s.find((x) => x.kimlik === "residual")).toMatchObject({
      etiket: "Anlamlı",
      metin: "Ölçülmemiş katyon aracılı etki",
    });
  });

  it("girilmeyen parametrenin (null) satırını göstermez", () => {
    const s = mekanizmaSatirlari(sonuc({ albumin_effect: null, lactate_effect: null, residual_effect: null }), ESIK);
    expect(s.map((x) => x.kimlik)).toEqual(["sid"]);
  });

  it("küçük etkiye eşiği söyleyen metin verir", () => {
    expect(satirlar[3].metin).toBe("Etkisi 2 mEq/L’nin altında.");
  });
});

describe("artık satırı ve girilmeyen parametreler", () => {
  const artik = (s: Sonuc) => mekanizmaSatirlari(s, ESIK).find((x) => x.kimlik === "residual")!;

  it("laktat ve albümin girildiyse artık soluk değildir", () => {
    expect(artik(ORNEK).soluk).toBe(false);
  });

  it("laktat girilmediyse artık soluktur ve girilmeyeni söyler", () => {
    const s = artik(sonuc({ lactate_effect: null, residual_effect: -3.6 }));
    expect(s.soluk).toBe(true);
    expect(s.metin).toBe("Girilmeyen laktat etkisini de içerir; ayrı yorumlanmamalıdır.");
  });

  it("ikisi de girilmediyse ikisini de sayar", () => {
    const s = artik(sonuc({ lactate_effect: null, albumin_effect: null, residual_effect: 3.0 }));
    expect(s.metin).toBe("Girilmeyen laktat ve albümin etkisini de içerir; ayrı yorumlanmamalıdır.");
  });

  it("çekirdek artığı yorumladıysa onun açıklaması korunur, uyarı eklenir", () => {
    const s = artik(
      sonuc({
        albumin_effect: null,
        residual_effect: -4.0,
        mechanism_analysis: {
          total_metabolic_effect: -10.4,
          all_mechanisms: [mekanizma("unmeasured", -4.0, "significant", "Ölçülmemiş anyon aracılı etki")],
        },
      }),
    );
    expect(s.etiket).toBe("Anlamlı");
    expect(s.metin).toBe(
      "Ölçülmemiş anyon aracılı etki. Girilmeyen albümin etkisini de içerir; ayrı yorumlanmamalıdır.",
    );
  });

  it("diğer satırlar bundan etkilenmez", () => {
    const satirlar = mekanizmaSatirlari(sonuc({ lactate_effect: null, residual_effect: -3.6 }), ESIK);
    expect(satirlar.filter((x) => x.kimlik !== "residual").every((x) => !x.soluk)).toBe(true);
  });
});

describe("gosterilenDeger (durum, yazılan değerle hesaplanır)", () => {
  const tanim = (kod: string) => DEGERLER.find((d) => d.kod === kod)!;
  const ph = { low: 7.35, high: 7.45 };

  it("değeri ekrandaki basamak sayısına yuvarlar", () => {
    expect(gosterilenDeger(tanim("ph"), 7.346)).toBe(7.35);
    expect(gosterilenDeger(tanim("hco3"), 21.96)).toBe(22);
    expect(gosterilenDeger(tanim("be"), -2.04)).toBe(-2);
  });

  it("pCO₂ olduğu gibi yazıldığı için yuvarlanmaz", () => {
    expect(gosterilenDeger(tanim("pco2"), 31.25)).toBe(31.25);
  });

  it("sınırda yuvarlanan değer 'Normalin altında' denmez", () => {
    // Ham değerle: 7.346 < 7.35 → "altında", ama ekranda "7.35" yazar
    expect(degerDurumu(7.346, ph, false).metin).toBe("Normalin altında");
    expect(degerDurumu(gosterilenDeger(tanim("ph"), 7.346), ph, false).metin).toBe("Normal aralıkta");
  });
});

describe("cubukYariGenisligi", () => {
  it("en az 12, daha büyük etkide yukarı yuvarlanmış en büyük etki", () => {
    expect(cubukYariGenisligi(mekanizmaSatirlari(ORNEK, ESIK))).toBe(12);
    expect(cubukYariGenisligi(mekanizmaSatirlari(sonuc({ sid_effect: -25.3 }), ESIK))).toBe(26);
  });
});

describe("degerDurumu", () => {
  const ph = { low: 7.35, high: 7.45 };
  const pco2 = { low: 35, high: 45 };

  it("pH düşükse asit yönü, yüksekse baz yönü", () => {
    expect(degerDurumu(7.3, ph, false)).toEqual({ metin: "Normalin altında", yon: "asit", simge: "▼" });
    expect(degerDurumu(7.5, ph, false)).toEqual({ metin: "Normalin üstünde", yon: "baz", simge: "▲" });
  });

  it("pCO₂ ters çalışır: düşükse baz yönü, yüksekse asit yönü", () => {
    expect(degerDurumu(31, pco2, true).yon).toBe("baz");
    expect(degerDurumu(60, pco2, true).yon).toBe("asit");
  });

  it("aralığın uç değerleri normaldir, yön yok", () => {
    expect(degerDurumu(7.35, ph, false)).toEqual({ metin: "Normal aralıkta", yon: null, simge: "" });
    expect(degerDurumu(45, pco2, true).yon).toBeNull();
  });
});

describe("yuzde ve normalMetni", () => {
  it("ölçek dışındaki değer uca yapışır", () => {
    expect(yuzde(7.3, { min: 7.0, max: 7.6 })).toBeCloseTo(50, 5);
    expect(yuzde(6.5, { min: 7.0, max: 7.6 })).toBe(0);
    expect(yuzde(9, { min: 7.0, max: 7.6 })).toBe(100);
  });

  it("normal aralık metni: pozitifte tire, BE'de işaretli", () => {
    expect(normalMetni({ low: 7.35, high: 7.45 })).toBe("Normal 7.35–7.45");
    expect(normalMetni({ low: -2, high: 2 })).toBe("Normal −2…+2");
  });
});

describe("notGruplari", () => {
  const notlar = [
    { category: "C", condition: "", note: "olası", mechanisms: ["X", "Y"], references: [] },
    { category: "A", condition: "", note: "birinci", mechanisms: [], references: [] },
    { category: "A", condition: "", note: "ikinci", mechanisms: [], references: [] },
    { category: "B", condition: "", note: "maske", mechanisms: [], references: [] },
  ];

  it("A/B/C'yi tasarımdaki adlarla ve bu sırayla gruplar", () => {
    const g = notGruplari(notlar);
    expect(g.map((x) => x.etiket)).toEqual(["Mekanizma", "Maskelenme", "Olası nedenler"]);
    expect(g[0].maddeler.map((m) => m.metin)).toEqual(["birinci", "ikinci"]);
    expect(g[2].maddeler[0].mekanizmalar).toEqual(["X", "Y"]);
  });

  it("not yoksa boş liste; bilinmeyen kategori 'Diğer' olur", () => {
    expect(notGruplari([])).toEqual([]);
    expect(notGruplari([{ category: "Z", condition: "", note: "n", mechanisms: [], references: [] }])[0].etiket).toBe(
      "Diğer",
    );
  });
});

describe("ozetSatirlari ve uyarilar", () => {
  it("özet çekirdeğin metinlerinden kurulur", () => {
    const o = Object.fromEntries(ozetSatirlari(ORNEK).map((s) => [s.ad, s.deger]));
    expect(o["Net metabolik etki"]).toBe("−10.4 mEq/L");
    expect(o["Solunumsal yanıt"]).toBe("Uygun solunumsal kompanzasyon (Beklenen pCO2: 30 ± 2)");
    expect(o["Anlamlı katkı"]).toBe("Zayıf asit azalması (hipoalbüminemi) etkisi (+4.2 mEq/L)");
    expect(o["Baz fazlası kaynağı"]).toBe("pH ve pCO₂’den hesaplandı");
  });

  it("cihaz BE'si kullanıldıysa bunu söyler", () => {
    const o = Object.fromEntries(ozetSatirlari(sonuc({ be_source: "manual" })).map((s) => [s.ad, s.deger]));
    expect(o["Baz fazlası kaynağı"]).toBe("Cihaz değeri");
  });

  it("uyarılar tekrarsız birleşir", () => {
    expect(uyarilar(sonuc({ warnings: ["a", "b"], soft_warnings: ["b", "c"] }))).toEqual(["a", "b", "c"]);
  });
});

describe("klasikKarsilastirma", () => {
  // Çekirdeğin gerçek çıktısı (pH 7.30, pCO₂ 31, Na 141, Cl 114, laktat 2.8, albümin 25)
  const FARKLI = {
    differences: [
      "Düşük albümin mevcut asidozu maskelemiş olabilir → klasik AG düzeltmesi gerekli.",
      "Karşıt etkiler birbirini dengelemiş → klasik tek parametre değerlendirmesi yetersiz kalabilir.",
    ],
    missed_by_classic: ["Hipoalbüminemi maskeleme etkisi", "Karşıt etkiler birbirini maskelemiş"],
    // Çekirdek artık bu cümleyi üretmiyor; arayüzün yine de almadığını eski yanıtla doğrularız
    stewart_advantage: "Stewart-Fencl yaklaşımı, klasik analizde gözden kaçabilecek bozuklukları ortaya çıkardı.",
  };

  it("farkları ve klasik analizde gözden kaçabilecekleri çekirdekten aynen alır", () => {
    const k = klasikKarsilastirma(sonuc({ classic_comparison: FARKLI }));
    expect(k).toEqual({ farklar: FARKLI.differences, kacirilanlar: FARKLI.missed_by_classic });
  });

  it("çekirdeğin kapanış cümlesini (stewart_advantage) almaz", () => {
    const k = klasikKarsilastirma(sonuc({ classic_comparison: FARKLI }));
    expect(JSON.stringify(k)).not.toContain("ortaya çıkardı");
  });

  it("fark yoksa null döner; 'benzer sonuç veriyor' cümlesi de gösterilmez", () => {
    const benzer = {
      differences: [],
      missed_by_classic: [],
      stewart_advantage: "Bu vakada klasik ve Stewart yaklaşımları benzer sonuç veriyor.",
    };
    expect(klasikKarsilastirma(sonuc({ classic_comparison: benzer }))).toBeNull();
  });

  it("karşılaştırma hiç yoksa null döner", () => {
    expect(klasikKarsilastirma(sonuc({ classic_comparison: null }))).toBeNull();
    expect(klasikKarsilastirma(sonuc({}))).toBeNull();
  });
});

describe("toplamEtki", () => {
  it("çekirdeğin toplam metabolik etkisini verir", () => {
    expect(toplamEtki(ORNEK)).toBe(-10.4);
  });

  it("mekanizma analizi yoksa kullanılan BE'ye döner", () => {
    expect(toplamEtki(sonuc({ mechanism_analysis: null }))).toBe(-10.4);
  });
});
