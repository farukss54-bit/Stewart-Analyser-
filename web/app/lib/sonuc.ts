import type { components } from "./api-types";
import { sayiYaz } from "./bicim";

export type Sonuc = components["schemas"]["StewartOutput"];
type CekirdekMekanizma = components["schemas"]["MechanismContribution"];
type KlinikNot = components["schemas"]["CDSNote"];

/** Renk anlamı: mercan = asit yönü, mavi = baz yönü */
export type Yon = "asit" | "baz";

// ---------------------------------------------------------------------------
// Mekanizma satırları
// ---------------------------------------------------------------------------

export type MekanizmaKimligi = "sid" | "albumin" | "lactate" | "residual";

export interface MekanizmaSatiri {
  kimlik: MekanizmaKimligi;
  ad: string;
  /** mEq/L; negatif = asit yönü, pozitif = baz yönü */
  etki: number;
  yon: Yon;
  etiket: "Baskın" | "Anlamlı" | null;
  metin: string;
  /** Etki anlamlılık eşiğini aşmıyor: varsayılan olarak gizlenir */
  kucuk: boolean;
  /**
   * Yalnızca artık satırında: laktat ya da albümin girilmedi, bu yüzden artık onların payını da
   * içeriyor. Satır soluk çizilir ve "açıklanamayan" diye yorumlanmaması söylenir.
   */
  soluk: boolean;
}

const AD: Record<MekanizmaKimligi, string> = {
  sid: "Güçlü iyon farkı (SID)",
  albumin: "Albümin",
  lactate: "Laktat",
  residual: "Açıklanamayan kalan",
};

// Çekirdeğin mekanizma kimlikleri; "unmeasured" burada "residual" satırıdır
const CEKIRDEK_KIMLIGI: Record<string, MekanizmaKimligi> = {
  sid: "sid",
  albumin: "albumin",
  lactate: "lactate",
  unmeasured: "residual",
};

const ETIKET: Record<string, MekanizmaSatiri["etiket"]> = {
  dominant: "Baskın",
  significant: "Anlamlı",
};

/**
 * Baz açığına katkı satırları. Etkiler çekirdeğin ham alanlarından alınır (SID, albümin, laktat,
 * artık), mekanizma listesinden değil: liste yalnızca eşiği aşanları (artığı ise yalnızca belirli
 * koşullarda) içerir, oysa satırların toplamı ölçülen baz açığını tutmalıdır.
 * "Baskın/Anlamlı" etiketi ve açıklama metni, çekirdeğin listesinde varsa oradan gelir.
 */
export function mekanizmaSatirlari(sonuc: Sonuc, esik: number): MekanizmaSatiri[] {
  const cekirdek = new Map<MekanizmaKimligi, CekirdekMekanizma>();
  for (const m of sonuc.mechanism_analysis?.all_mechanisms ?? []) {
    const kimlik = CEKIRDEK_KIMLIGI[m.identifier];
    if (kimlik) cekirdek.set(kimlik, m);
  }

  const etkiler: [MekanizmaKimligi, number | null | undefined][] = [
    ["sid", sonuc.sid_effect],
    ["albumin", sonuc.albumin_effect],
    ["lactate", sonuc.lactate_effect],
    ["residual", sonuc.residual_effect],
  ];

  const satirlar: MekanizmaSatiri[] = [];
  for (const [kimlik, etki] of etkiler) {
    // Girilmeyen parametrenin etkisi hesaplanmaz (null); satır da gösterilmez
    if (etki === null || etki === undefined) continue;
    const m = cekirdek.get(kimlik);
    const kucuk = Math.abs(etki) <= esik;
    // Girilmeyen laktat/albümin payı çekirdekte artığa katılır; artık "açıklanamayan" olarak okunmamalı
    const girilmeyen = kimlik === "residual" ? girilmeyenler(sonuc) : [];
    const soluk = girilmeyen.length > 0;
    let metin = m?.description ?? varsayilanMetin(kimlik, kucuk, esik);
    if (soluk) {
      const uyari = `Girilmeyen ${girilmeyen.join(" ve ")} etkisini de içerir; ayrı yorumlanmamalıdır.`;
      metin = m ? `${m.description}. ${uyari}` : uyari;
    }
    satirlar.push({
      kimlik,
      ad: AD[kimlik],
      etki,
      yon: etki < 0 ? "asit" : "baz",
      etiket: m ? (ETIKET[m.level] ?? null) : null,
      metin,
      kucuk,
      soluk,
    });
  }
  return satirlar;
}

/** Girilmediği için etkisi hesaplanamayan parametreler */
function girilmeyenler(sonuc: Sonuc): string[] {
  const liste: string[] = [];
  if (sonuc.lactate_effect === null || sonuc.lactate_effect === undefined) liste.push("laktat");
  if (sonuc.albumin_effect === null || sonuc.albumin_effect === undefined) liste.push("albümin");
  return liste;
}

function varsayilanMetin(kimlik: MekanizmaKimligi, kucuk: boolean, esik: number): string {
  if (kucuk) return `Etkisi ${esik} mEq/L’nin altında.`;
  if (kimlik === "residual") {
    return "Diğer mekanizmaların açıklamadığı pay. Ölçülmemiş anyonları ayrıca değerlendirmek için gelişmiş mod gerekir.";
  }
  return "Bu mekanizmanın baz açığına katkısı.";
}

/** Çubuk ölçeğinin yarı genişliği (mEq/L): en büyük etkiyi sığdırır, en az 12 */
export function cubukYariGenisligi(satirlar: MekanizmaSatiri[]): number {
  const enBuyuk = Math.max(0, ...satirlar.map((s) => Math.abs(s.etki)));
  return Math.max(12, Math.ceil(enBuyuk));
}

// ---------------------------------------------------------------------------
// Temel değerler (aralık çubukları)
// ---------------------------------------------------------------------------

export type DegerKodu = "ph" | "pco2" | "hco3" | "be";

export interface DegerTanimi {
  kod: DegerKodu;
  ad: string;
  birim: string;
  /** Aralık çubuğunun gösterim ölçeği (klinik eşik değil, yalnızca çizim) */
  olcek: { min: number; max: number };
  /** true: değer düşükken baz yönünde etki yapar (pCO₂) */
  ters: boolean;
  /** Gösterimde kaç ondalık basamak yazılır (yok: girilen değer olduğu gibi) */
  hane?: number;
  yaz: (deger: number) => string;
}

export const DEGERLER: DegerTanimi[] = [
  { kod: "ph", ad: "pH", birim: "", olcek: { min: 7.0, max: 7.6 }, ters: false, hane: 2, yaz: (v) => v.toFixed(2) },
  { kod: "pco2", ad: "pCO₂", birim: "mmHg", olcek: { min: 15, max: 75 }, ters: true, yaz: (v) => String(v) },
  { kod: "hco3", ad: "HCO₃⁻", birim: "mEq/L", olcek: { min: 5, max: 40 }, ters: false, hane: 1, yaz: (v) => sayiYaz(v) },
  {
    kod: "be",
    ad: "Baz fazlası (BE)",
    birim: "mEq/L",
    olcek: { min: -20, max: 20 },
    ters: false,
    hane: 1,
    yaz: (v) => sayiYaz(v, true),
  },
];

/**
 * Ekranda yazılan değer. Normal/anormal durumu bu değerle hesaplanır: yoksa sınırda yuvarlanan bir
 * değer (örn. 7.346 → "7.35") "Normalin altında" denirken sınırın üzerinde görünürdü.
 */
export function gosterilenDeger(tanim: DegerTanimi, deger: number): number {
  return tanim.hane === undefined ? deger : Number(deger.toFixed(tanim.hane));
}

export interface DegerDurumu {
  metin: "Normalin altında" | "Normalin üstünde" | "Normal aralıkta";
  /** Normal aralıkta null */
  yon: Yon | null;
  simge: "▼" | "▲" | "";
}

export function degerDurumu(deger: number, aralik: { low: number; high: number }, ters: boolean): DegerDurumu {
  if (deger < aralik.low) return { metin: "Normalin altında", yon: ters ? "baz" : "asit", simge: "▼" };
  if (deger > aralik.high) return { metin: "Normalin üstünde", yon: ters ? "asit" : "baz", simge: "▲" };
  return { metin: "Normal aralıkta", yon: null, simge: "" };
}

/** Değerin çubuk üzerindeki konumu, yüzde (ölçek dışındaki değerler uca yapışır) */
export function yuzde(deger: number, olcek: { min: number; max: number }): number {
  const oran = ((deger - olcek.min) / (olcek.max - olcek.min)) * 100;
  return Math.max(0, Math.min(100, oran));
}

function isaretli(sayi: number): string {
  return sayi < 0 ? `−${Math.abs(sayi)}` : `+${sayi}`;
}

export function normalMetni(aralik: { low: number; high: number }): string {
  if (aralik.low < 0) return `Normal ${isaretli(aralik.low)}…${isaretli(aralik.high)}`;
  return `Normal ${aralik.low}–${aralik.high}`;
}

// ---------------------------------------------------------------------------
// Notlar
// ---------------------------------------------------------------------------

export interface NotMaddesi {
  metin: string;
  /** Yalnızca "Olası nedenler" notlarında: çekirdeğin saydığı olası mekanizmalar */
  mekanizmalar: string[];
}

export interface NotGrubu {
  etiket: string;
  maddeler: NotMaddesi[];
}

// Çekirdekteki A/B/C kategorilerinin arayüzdeki adları
const NOT_ADLARI: Record<string, string> = {
  A: "Mekanizma",
  B: "Maskelenme",
  C: "Olası nedenler",
};

export function notGruplari(notlar: KlinikNot[]): NotGrubu[] {
  const gruplar = new Map<string, NotMaddesi[]>();
  for (const n of notlar) {
    const etiket = NOT_ADLARI[n.category] ?? "Diğer";
    const liste = gruplar.get(etiket) ?? [];
    liste.push({ metin: n.note, mekanizmalar: n.mechanisms ?? [] });
    gruplar.set(etiket, liste);
  }
  const sira = [...Object.values(NOT_ADLARI), "Diğer"];
  return sira.filter((e) => gruplar.has(e)).map((e) => ({ etiket: e, maddeler: gruplar.get(e)! }));
}

// ---------------------------------------------------------------------------
// Özet satırları
// ---------------------------------------------------------------------------

export interface OzetSatiri {
  ad: string;
  deger: string;
}

export function ozetSatirlari(sonuc: Sonuc): OzetSatiri[] {
  const satirlar: OzetSatiri[] = [];
  const baslik = sonuc.headline;

  if (baslik?.significant_mechanisms?.length) {
    satirlar.push({ ad: "Anlamlı katkı", deger: baslik.significant_mechanisms.join("; ") });
  }
  if (baslik?.contributing_mechanisms?.length) {
    satirlar.push({ ad: "Diğer katkılar", deger: baslik.contributing_mechanisms.join("; ") });
  }

  const net = sonuc.mechanism_analysis?.total_metabolic_effect ?? sonuc.be_used;
  satirlar.push({ ad: "Net metabolik etki", deger: `${sayiYaz(net, true)} mEq/L` });

  const solunum = baslik?.respiratory_status || sonuc.mechanism_analysis?.respiratory_status;
  if (solunum) {
    const ayrinti = sonuc.compensation_details ? ` (${sonuc.compensation_details})` : "";
    satirlar.push({ ad: "Solunumsal yanıt", deger: `${solunum}${ayrinti}` });
  }

  satirlar.push({
    ad: "Baz fazlası kaynağı",
    deger: sonuc.be_source === "manual" ? "Cihaz değeri" : "pH ve pCO₂’den hesaplandı",
  });
  return satirlar;
}

/** Uyarı listesi: çekirdeğin uyarıları ve yumuşak uyarıları, tekrarsız */
export function uyarilar(sonuc: Sonuc): string[] {
  return [...new Set([...(sonuc.warnings ?? []), ...(sonuc.soft_warnings ?? [])])];
}
