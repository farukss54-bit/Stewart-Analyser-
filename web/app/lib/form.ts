import type { AnalyzeRequest, DerivedRequest, Meta } from "./api";

export type AlanAdi = "ph" | "pco2" | "na" | "cl" | "lactate" | "albumin" | "k" | "ca" | "mg" | "po4";
/** Hızlı mod: pH, pCO₂, Na⁺, Cl⁻, laktat, albümin. Gelişmiş mod: bunlara K⁺, Ca²⁺, Mg²⁺ ve fosfat eklenir. */
export type Mod = "hizli" | "gelismis";
export type AlbuminBirimi = "g/L" | "g/dL";
export type Degerler = Record<AlanAdi, string>;
export type Sinirlar = Meta["limits"];

export interface Cihaz {
  acik: boolean;
  hco3: string;
  be: string;
  /** Baz açığı (BD) olarak girildiyse true: işareti çekirdek çevirir */
  bd: boolean;
}

export interface AlanTanimi {
  ad: AlanAdi;
  etiket: string;
  birim: string;
  zorunlu: boolean;
  /** Panelde satırın tamamını kaplar (yanında eşi olmayan alanlar) */
  tam?: boolean;
  /** Gelişmiş modun ileri parametresi (K⁺, Ca²⁺, Mg²⁺, fosfat): boşken kesikli çerçeveyle işaretlenir */
  ileri?: boolean;
}

export interface Grup {
  baslik: string;
  alanlar: AlanTanimi[];
  /** Grup başlığının altındaki kısa açıklama */
  not?: string;
}

// Hızlı mod alanları. K⁺ burada yok: hızlı modda hesaba girmez (yalnızca gelişmiş modda).
// Zorunlu olanlar çekirdeğin gerektirdikleridir; laktat ve albümin boş bırakılabilir,
// bu durumda etkileri değerlendirilmez (çekirdek bunu yumuşak uyarıyla bildirir).
const GRUPLAR_HIZLI: Grup[] = [
  {
    baslik: "Kan gazı",
    alanlar: [
      { ad: "ph", etiket: "pH", birim: "", zorunlu: true },
      { ad: "pco2", etiket: "pCO₂", birim: "mmHg", zorunlu: true },
    ],
  },
  {
    baslik: "Elektrolitler",
    alanlar: [
      { ad: "na", etiket: "Na⁺", birim: "mmol/L", zorunlu: true },
      { ad: "cl", etiket: "Cl⁻", birim: "mmol/L", zorunlu: true },
      { ad: "lactate", etiket: "Laktat", birim: "mmol/L", zorunlu: false, tam: true },
    ],
  },
  {
    baslik: "Albümin",
    alanlar: [{ ad: "albumin", etiket: "Albümin", birim: "", zorunlu: false, tam: true }],
  },
];

// Gelişmiş mod: K⁺, Ca²⁺, Mg²⁺ ve fosfat isteğe bağlıdır; girilmeyenler SIG'in kesinliğini azaltır.
// Birimleri çekirdeğin beklediği gibidir (iyonize Ca, Mg ve fosfat mmol/L).
const GRUPLAR_GELISMIS: Grup[] = [
  GRUPLAR_HIZLI[0],
  {
    baslik: "Elektrolitler",
    alanlar: [
      { ad: "na", etiket: "Na⁺", birim: "mmol/L", zorunlu: true },
      { ad: "cl", etiket: "Cl⁻", birim: "mmol/L", zorunlu: true },
      { ad: "k", etiket: "K⁺", birim: "mmol/L", zorunlu: false, ileri: true },
      { ad: "lactate", etiket: "Laktat", birim: "mmol/L", zorunlu: false },
    ],
  },
  {
    baslik: "İleri parametreler",
    not: "İsteğe bağlı. Girilirse ölçülmemiş anyonlar (SIG) tam hesaplanır.",
    alanlar: [
      { ad: "ca", etiket: "Ca²⁺ (iyonize)", birim: "mmol/L", zorunlu: false, tam: true, ileri: true },
      { ad: "mg", etiket: "Mg²⁺", birim: "mmol/L", zorunlu: false, ileri: true },
      { ad: "po4", etiket: "Fosfat", birim: "mmol/L", zorunlu: false, ileri: true },
    ],
  },
  GRUPLAR_HIZLI[2],
];

export function gruplar(mod: Mod): Grup[] {
  return mod === "gelismis" ? GRUPLAR_GELISMIS : GRUPLAR_HIZLI;
}

export function alanlar(mod: Mod): AlanTanimi[] {
  return gruplar(mod).flatMap((g) => g.alanlar);
}

export const BOS_DEGERLER: Degerler = {
  ph: "",
  pco2: "",
  na: "",
  cl: "",
  lactate: "",
  albumin: "",
  k: "",
  ca: "",
  mg: "",
  po4: "",
};
export const BOS_CIHAZ: Cihaz = { acik: false, hco3: "", be: "", bd: false };

// Albümin birimine göre API'nin döndürdüğü sınır anahtarı
function sinirAnahtari(ad: AlanAdi, birim: AlbuminBirimi): string {
  if (ad === "albumin") return birim === "g/L" ? "albumin_gl" : "albumin_gdl";
  return ad;
}

export type Ayrisma = { tur: "bos" } | { tur: "gecersiz" } | { tur: "sayi"; deger: number };

/** "7,30" ve "7.30" kabul edilir; bilimsel gösterim, boşluk ve harf kabul edilmez. */
export function ayristir(metin: string): Ayrisma {
  const temiz = metin.trim();
  if (temiz === "") return { tur: "bos" };
  if (!/^-?\d+(?:[.,]\d+)?$/.test(temiz)) return { tur: "gecersiz" };
  const deger = Number(temiz.replace(",", "."));
  // Çok uzun rakam dizileri Infinity olur; JSON'da null'a dönüşüp API'ye bozuk gider
  if (!Number.isFinite(deger)) return { tur: "gecersiz" };
  return { tur: "sayi", deger };
}

/** Alan için hata metni; hata yoksa null. Boş alan hata değildir (zorunluluk ayrıca denetlenir). */
export function alanHatasi(
  etiket: string,
  metin: string,
  sinir: { min: number; max: number } | undefined,
): string | null {
  const a = ayristir(metin);
  if (a.tur === "bos") return null;
  if (a.tur === "gecersiz") return "Sayı girin (örn. 7,30).";
  if (sinir && (a.deger < sinir.min || a.deger > sinir.max)) {
    return `${etiket} ${a.deger} girildi, ancak ${sinir.min} ile ${sinir.max} arasında olmalı. Değeri kontrol edin.`;
  }
  return null;
}

export type Hatalar = Partial<Record<AlanAdi | "cihazHco3" | "cihazBe", string>>;

/** Sınırlar henüz yüklenmediyse yalnızca biçim denetlenir; sınır denetimini sunucu yapar. */
export function hatalariBul(
  degerler: Degerler,
  birim: AlbuminBirimi,
  cihaz: Cihaz,
  sinirlar: Sinirlar | undefined,
  mod: Mod = "hizli",
): Hatalar {
  const hatalar: Hatalar = {};
  // Yalnızca ekrandaki alanlar denetlenir: hızlı modda gizli kalan K⁺ vb. analizi engellemez
  for (const alan of alanlar(mod)) {
    const etiket = alan.etiket;
    const h = alanHatasi(etiket, degerler[alan.ad], sinirlar?.[sinirAnahtari(alan.ad, birim)]);
    if (h) hatalar[alan.ad] = h;
  }
  if (cihaz.acik) {
    const hco3 = alanHatasi("HCO₃⁻", cihaz.hco3, sinirlar?.hco3);
    if (hco3) hatalar.cihazHco3 = hco3;
    const be = alanHatasi("BE", cihaz.be, sinirlar?.be);
    if (be) hatalar.cihazBe = be;
  }
  return hatalar;
}

/** Henüz doldurulmamış zorunlu alanlar (arayüzdeki sırayla). */
export function eksikZorunlular(degerler: Degerler, mod: Mod = "hizli"): AlanTanimi[] {
  return alanlar(mod).filter((a) => a.zorunlu && ayristir(degerler[a.ad]).tur === "bos");
}

function sayi(metin: string): number | undefined {
  const a = ayristir(metin);
  return a.tur === "sayi" ? a.deger : undefined;
}

/** Sınırlar içindeki cihaz değerleri; geçersiz olan istekte yer almaz. */
function cihazDegeri(metin: string, sinir: { min: number; max: number } | undefined): number | undefined {
  const d = sayi(metin);
  if (d === undefined) return undefined;
  if (sinir && (d < sinir.min || d > sinir.max)) return undefined;
  return d;
}

/** pH ve pCO₂ geçerli değilse null: türetilmiş değerler hesaplanamaz. */
export function turetilmisIstegi(
  degerler: Degerler,
  cihaz: Cihaz,
  sinirlar: Sinirlar | undefined,
): DerivedRequest | null {
  const ph = sayi(degerler.ph);
  const pco2 = sayi(degerler.pco2);
  if (ph === undefined || pco2 === undefined) return null;
  if (alanHatasi("pH", degerler.ph, sinirlar?.ph) || alanHatasi("pCO₂", degerler.pco2, sinirlar?.pco2)) return null;

  const istek: DerivedRequest = { ph, pco2 };
  if (cihaz.acik) {
    const hco3 = cihazDegeri(cihaz.hco3, sinirlar?.hco3);
    const be = cihazDegeri(cihaz.be, sinirlar?.be);
    if (hco3 !== undefined) istek.hco3_device = hco3;
    if (be !== undefined) {
      istek.be_device = be;
      istek.is_base_deficit = cihaz.bd;
    }
  }
  return istek;
}

/**
 * Analiz isteği. Cihaz BE'si HAM girildiği gibi gönderilir, BD işareti ayrı bayraktır:
 * işareti çekirdek bir kez çevirir. Çevrilmiş değeri göndermek işareti iki kez çevirirdi.
 */
export function analizIstegi(
  degerler: Degerler,
  birim: AlbuminBirimi,
  cihaz: Cihaz,
  sinirlar: Sinirlar | undefined,
  mod: Mod = "hizli",
): AnalyzeRequest | null {
  const ph = sayi(degerler.ph);
  const pco2 = sayi(degerler.pco2);
  const na = sayi(degerler.na);
  const cl = sayi(degerler.cl);
  if (ph === undefined || pco2 === undefined || na === undefined || cl === undefined) return null;

  const istek: AnalyzeRequest = { ph, pco2, na, cl, mode: mod === "gelismis" ? "advanced" : "quick", albumin_unit: birim };
  const lactate = sayi(degerler.lactate);
  const albumin = sayi(degerler.albumin);
  if (lactate !== undefined) istek.lactate = lactate;
  if (albumin !== undefined) istek.albumin = albumin;
  // K⁺, Ca²⁺, Mg²⁺ ve fosfat yalnızca gelişmiş modda gönderilir (hızlı modda hesaba girmez)
  if (mod === "gelismis") {
    for (const ad of ["k", "ca", "mg", "po4"] as const) {
      const d = sayi(degerler[ad]);
      if (d !== undefined) istek[ad] = d;
    }
  }

  if (cihaz.acik) {
    const hco3 = cihazDegeri(cihaz.hco3, sinirlar?.hco3);
    const be = cihazDegeri(cihaz.be, sinirlar?.be);
    if (hco3 !== undefined) istek.hco3 = hco3;
    if (be !== undefined) {
      istek.be = be;
      istek.is_be_base_deficit = cihaz.bd;
    }
  }
  return istek;
}

/** Birim değişince girilen değer yeni birime çevrilir; geçerli bir sayı değilse olduğu gibi kalır. */
export function albuminCevir(metin: string, kaynak: AlbuminBirimi, hedef: AlbuminBirimi): string {
  const a = ayristir(metin);
  if (a.tur !== "sayi" || kaynak === hedef) return metin;
  const sonuc = hedef === "g/dL" ? a.deger / 10 : a.deger * 10;
  // Kayan nokta artığı (3.2500000000000004 gibi) görünmesin
  return String(Number(sonuc.toFixed(3)));
}

/**
 * Hazır vakanın değerlerini forma çevirir. Albümin g/L'dir. K⁺ her zaman yüklenir ama yalnızca
 * gelişmiş modda kullanılır (hızlı modda alan gizlidir ve istekte yer almaz).
 *
 * Vakadaki BE, cihaz BE alanına yazılır ama cihaz bölümü KAPALI kalır, yani analizde kullanılmaz
 * (BE pH ve pCO₂'den hesaplanır). Streamlit de böyle davranır. Cihaz değeri olarak kullanmak
 * kullanıcının seçimidir: örneğin KOAH vakası (pH 7.28, BE +4.0) cihaz değeri olarak girilince BE
 * işaret denetimi tarafından engellenir.
 */
export function vakaDegerleri(degerler: Record<string, number>): { degerler: Degerler; cihaz: Cihaz } {
  const yaz = (v: number | undefined) => (typeof v === "number" ? String(v) : "");
  return {
    degerler: {
      ph: yaz(degerler.ph),
      pco2: yaz(degerler.pco2),
      na: yaz(degerler.na),
      cl: yaz(degerler.cl),
      lactate: yaz(degerler.lactate),
      albumin: yaz(degerler.albumin_gl),
      k: yaz(degerler.k),
      ca: "",
      mg: "",
      po4: "",
    },
    cihaz: typeof degerler.be === "number" ? { acik: false, hco3: "", be: yaz(degerler.be), bd: false } : BOS_CIHAZ,
  };
}
