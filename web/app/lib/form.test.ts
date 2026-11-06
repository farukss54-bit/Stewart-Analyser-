import { describe, expect, it } from "vitest";
import {
  albuminCevir,
  alanHatasi,
  analizIstegi,
  ayristir,
  BOS_CIHAZ,
  BOS_DEGERLER,
  eksikZorunlular,
  hatalariBul,
  turetilmisIstegi,
  vakaDegerleri,
  type Degerler,
  type Sinirlar,
} from "./form";

// /api/meta'nın döndürdüğü sınırların bir kısmı (değerler constants.py ile aynı)
const SINIRLAR: Sinirlar = {
  ph: { min: 6.5, max: 7.9 },
  pco2: { min: 5, max: 250 },
  na: { min: 80, max: 220 },
  cl: { min: 50, max: 200 },
  lactate: { min: 0, max: 40 },
  hco3: { min: 5, max: 50 },
  be: { min: -30, max: 30 },
  albumin_gl: { min: 5, max: 60 },
  albumin_gdl: { min: 0.5, max: 6 },
};

// Tasarım örneğindeki kurgusal vaka
const VAKA: Degerler = { ph: "7.30", pco2: "31", na: "141", cl: "114", lactate: "2.8", albumin: "25" };

describe("ayristir", () => {
  it("nokta ve virgülü kabul eder", () => {
    expect(ayristir("7.30")).toEqual({ tur: "sayi", deger: 7.3 });
    expect(ayristir("7,30")).toEqual({ tur: "sayi", deger: 7.3 });
    expect(ayristir(" -10,4 ")).toEqual({ tur: "sayi", deger: -10.4 });
  });

  it("boş girişi ayırt eder", () => {
    expect(ayristir("")).toEqual({ tur: "bos" });
    expect(ayristir("   ")).toEqual({ tur: "bos" });
  });

  it("Infinity'ye taşan çok uzun rakam dizisini geçersiz sayar", () => {
    expect(ayristir("9".repeat(400))).toEqual({ tur: "gecersiz" });
    expect(ayristir("9".repeat(400) + ",5")).toEqual({ tur: "gecersiz" });
  });

  it.each(["abc", "7.3.0", "7,3,0", "1e3", "Infinity", "NaN", "0x10", "7 30", "--5", "+5", "7.", ".5"])(
    "geçersiz sayar: %s",
    (metin) => {
      expect(ayristir(metin)).toEqual({ tur: "gecersiz" });
    },
  );
});

describe("alanHatasi", () => {
  const sinir = { min: 6.5, max: 7.9 };

  it("sınır içindeki değerde hata yok, boş alanda da hata yok", () => {
    expect(alanHatasi("pH", "7.30", sinir)).toBeNull();
    expect(alanHatasi("pH", "", sinir)).toBeNull();
  });

  it("sınır değerlerinin kendisi geçerlidir", () => {
    expect(alanHatasi("pH", "6.5", sinir)).toBeNull();
    expect(alanHatasi("pH", "7.9", sinir)).toBeNull();
  });

  it("aralık dışını girilen değer ve sınırlarla bildirir", () => {
    expect(alanHatasi("pH", "8.02", sinir)).toBe(
      "pH 8.02 girildi, ancak 6.5 ile 7.9 arasında olmalı. Değeri kontrol edin.",
    );
    expect(alanHatasi("pH", "6,49", sinir)).toContain("6.49 girildi");
  });

  it("sayı olmayan girişi bildirir", () => {
    expect(alanHatasi("pH", "yedi", sinir)).toBe("Sayı girin (örn. 7,30).");
  });

  it("sınırlar yüklenmediyse yalnızca biçim denetlenir", () => {
    expect(alanHatasi("pH", "99", undefined)).toBeNull();
    expect(alanHatasi("pH", "x", undefined)).not.toBeNull();
  });
});

describe("hatalariBul", () => {
  it("tasarım örneğinde hata yok", () => {
    expect(hatalariBul(VAKA, "g/L", BOS_CIHAZ, SINIRLAR)).toEqual({});
  });

  it("birden çok hatayı alan adıyla verir", () => {
    const hatalar = hatalariBul({ ...VAKA, ph: "8.02", na: "abc" }, "g/L", BOS_CIHAZ, SINIRLAR);
    expect(Object.keys(hatalar).sort()).toEqual(["na", "ph"]);
  });

  it("albümin sınırı seçili birime göre uygulanır", () => {
    // 25 g/L geçerli, ama g/dL olarak 25 imkânsız
    expect(hatalariBul(VAKA, "g/L", BOS_CIHAZ, SINIRLAR).albumin).toBeUndefined();
    expect(hatalariBul(VAKA, "g/dL", BOS_CIHAZ, SINIRLAR).albumin).toContain("25 girildi");
  });

  it("cihaz değerleri yalnızca bölüm açıkken denetlenir", () => {
    const kapali = { ...BOS_CIHAZ, hco3: "99", be: "99" };
    expect(hatalariBul(VAKA, "g/L", kapali, SINIRLAR)).toEqual({});
    const hatalar = hatalariBul(VAKA, "g/L", { ...kapali, acik: true }, SINIRLAR);
    expect(Object.keys(hatalar).sort()).toEqual(["cihazBe", "cihazHco3"]);
  });
});

describe("eksikZorunlular", () => {
  it("boş formda dört zorunlu alanı sırayla verir; laktat ve albümin zorunlu değildir", () => {
    expect(eksikZorunlular(BOS_DEGERLER).map((a) => a.ad)).toEqual(["ph", "pco2", "na", "cl"]);
  });

  it("dolu alanlar listeden düşer", () => {
    expect(eksikZorunlular({ ...BOS_DEGERLER, ph: "7.3", cl: "114" }).map((a) => a.ad)).toEqual(["pco2", "na"]);
    expect(eksikZorunlular(VAKA)).toEqual([]);
  });
});

describe("turetilmisIstegi", () => {
  it("pH ve pCO₂ yoksa ya da aralık dışındaysa istek yok", () => {
    expect(turetilmisIstegi(BOS_DEGERLER, BOS_CIHAZ, SINIRLAR)).toBeNull();
    expect(turetilmisIstegi({ ...VAKA, ph: "8.02" }, BOS_CIHAZ, SINIRLAR)).toBeNull();
    expect(turetilmisIstegi({ ...VAKA, pco2: "x" }, BOS_CIHAZ, SINIRLAR)).toBeNull();
  });

  it("cihaz bölümü kapalıyken yalnızca pH ve pCO₂ gider", () => {
    const kapali = { ...BOS_CIHAZ, hco3: "14", be: "-10", bd: true };
    expect(turetilmisIstegi(VAKA, kapali, SINIRLAR)).toEqual({ ph: 7.3, pco2: 31 });
  });

  it("cihaz değerleri ham gider; geçersiz olan düşer", () => {
    const cihaz = { acik: true, hco3: "14,5", be: "10", bd: true };
    expect(turetilmisIstegi(VAKA, cihaz, SINIRLAR)).toEqual({
      ph: 7.3,
      pco2: 31,
      hco3_device: 14.5,
      be_device: 10,
      is_base_deficit: true,
    });
    expect(turetilmisIstegi(VAKA, { ...cihaz, hco3: "99", be: "" }, SINIRLAR)).toEqual({ ph: 7.3, pco2: 31 });
  });
});

describe("analizIstegi", () => {
  it("zorunlu alan eksikse istek yok", () => {
    expect(analizIstegi({ ...VAKA, cl: "" }, "g/L", BOS_CIHAZ, SINIRLAR)).toBeNull();
  });

  it("tasarım örneğini hızlı mod isteğine çevirir", () => {
    expect(analizIstegi(VAKA, "g/L", BOS_CIHAZ, SINIRLAR)).toEqual({
      ph: 7.3,
      pco2: 31,
      na: 141,
      cl: 114,
      lactate: 2.8,
      albumin: 25,
      albumin_unit: "g/L",
      mode: "quick",
    });
  });

  it("boş laktat ve albümin isteğe girmez; albümin birimi olduğu gibi gider", () => {
    const istek = analizIstegi({ ...VAKA, lactate: "", albumin: "" }, "g/dL", BOS_CIHAZ, SINIRLAR);
    expect(istek).not.toHaveProperty("lactate");
    expect(istek).not.toHaveProperty("albumin");
    expect(istek?.albumin_unit).toBe("g/dL");
  });

  it("BD ile girilen BE ham gider, işareti ARAYÜZ çevirmez (çekirdek bir kez çevirir)", () => {
    const istek = analizIstegi(VAKA, "g/L", { acik: true, hco3: "", be: "5", bd: true }, SINIRLAR);
    expect(istek?.be).toBe(5);
    expect(istek?.is_be_base_deficit).toBe(true);
  });
});

describe("albuminCevir", () => {
  it("g/L ↔ g/dL çevirir ve kayan nokta artığı bırakmaz", () => {
    expect(albuminCevir("25", "g/L", "g/dL")).toBe("2.5");
    expect(albuminCevir("2,5", "g/dL", "g/L")).toBe("25");
    expect(albuminCevir("32.5", "g/L", "g/dL")).toBe("3.25");
    expect(albuminCevir("3.25", "g/dL", "g/L")).toBe("32.5");
    expect(albuminCevir("2.3", "g/dL", "g/L")).toBe("23");
  });

  it("boş ya da geçersiz metne dokunmaz", () => {
    expect(albuminCevir("", "g/L", "g/dL")).toBe("");
    expect(albuminCevir("abc", "g/L", "g/dL")).toBe("abc");
  });

  it("aynı birime çevirmek değeri değiştirmez", () => {
    expect(albuminCevir("25", "g/L", "g/L")).toBe("25");
  });
});

describe("vakaDegerleri", () => {
  // constants.py SAMPLE_CASES: "Sepsis + Hipoalbüminemi"
  const SEPSIS = { ph: 7.38, pco2: 32.0, na: 138.0, cl: 108.0, k: 4.2, lactate: 3.5, albumin_gl: 22.0, be: -4.0 };

  it("vakanın değerlerini forma çevirir; albümin g/L alanına gider", () => {
    const { degerler } = vakaDegerleri(SEPSIS);
    expect(degerler).toEqual({ ph: "7.38", pco2: "32", na: "138", cl: "108", lactate: "3.5", albumin: "22" });
  });

  it("vakadaki BE cihaz alanına yazılır, işareti çevrilmez, ama cihaz bölümü kapalı kalır", () => {
    const { cihaz } = vakaDegerleri(SEPSIS);
    expect(cihaz).toEqual({ acik: false, hco3: "", be: "-4", bd: false });
  });

  it("BE sıfır olan vakada da aynıdır", () => {
    expect(vakaDegerleri({ ...SEPSIS, be: 0 }).cihaz).toEqual({ acik: false, hco3: "", be: "0", bd: false });
  });

  it("K⁺ hızlı modda kullanılmadığı için forma girmez", () => {
    expect(Object.values(vakaDegerleri(SEPSIS).degerler)).not.toContain("4.2");
  });

  it("eksik alanları boş bırakır, cihaz bölümünü açmaz", () => {
    const { degerler, cihaz } = vakaDegerleri({ ph: 7.4, pco2: 40, na: 140, cl: 102 });
    expect(degerler.lactate).toBe("");
    expect(degerler.albumin).toBe("");
    expect(cihaz).toEqual(BOS_CIHAZ);
  });

  it("yüklenen değerler form doğrulamasından hatasız geçer; BE analiz isteğine girmez (hesaplanır)", () => {
    const { degerler, cihaz } = vakaDegerleri(SEPSIS);
    expect(hatalariBul(degerler, "g/L", cihaz, SINIRLAR)).toEqual({});
    const istek = analizIstegi(degerler, "g/L", cihaz, SINIRLAR);
    expect(istek).toMatchObject({ ph: 7.38, albumin: 22 });
    expect(istek).not.toHaveProperty("be");
  });

  it("kullanıcı cihaz bölümünü açarsa vakadaki BE ham değeriyle kullanılır", () => {
    const { degerler, cihaz } = vakaDegerleri(SEPSIS);
    const istek = analizIstegi(degerler, "g/L", { ...cihaz, acik: true }, SINIRLAR);
    expect(istek).toMatchObject({ be: -4, is_be_base_deficit: false });
  });
});
