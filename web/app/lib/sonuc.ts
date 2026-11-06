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
export function mekanizmaSatirlari(sonuc: Sonuc, esik: number, gelismis = false): MekanizmaSatiri[] {
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
    let metin = m?.description ?? varsayilanMetin(kimlik, kucuk, esik, gelismis);
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

function varsayilanMetin(kimlik: MekanizmaKimligi, kucuk: boolean, esik: number, gelismis: boolean): string {
  if (kucuk) return `Etkisi ${esik} mEq/L’nin altında.`;
  if (kimlik === "residual") {
    // Gelişmiş modda ölçülmemiş anyonlar zaten SIG satırında değerlendirilir
    return gelismis
      ? "Diğer mekanizmaların açıklamadığı pay. Ölçülmemiş anyonlar için SIG satırına bakın."
      : "Diğer mekanizmaların açıklamadığı pay. Ölçülmemiş anyonları ayrıca değerlendirmek için gelişmiş mod gerekir.";
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

// ---------------------------------------------------------------------------
// Gelişmiş mod: SID katmanları, SIG ve anyon açığı
// ---------------------------------------------------------------------------

/** Analizde girilmeyen isteğe bağlı değerler, ekrandaki sırayla */
const GIRILEBILEN: { alan: "lactate" | "albumin" | "k" | "ca" | "mg" | "po4"; ad: string; sembol: string }[] = [
  { alan: "lactate", ad: "laktat", sembol: "laktat" },
  { alan: "albumin", ad: "albümin", sembol: "albümin" },
  { alan: "k", ad: "K", sembol: "K⁺" },
  { alan: "ca", ad: "Ca", sembol: "Ca²⁺" },
  { alan: "mg", ad: "Mg", sembol: "Mg²⁺" },
  { alan: "po4", ad: "fosfat", sembol: "fosfat" },
];

type IstekDegerleri = Partial<Record<"lactate" | "albumin" | "k" | "ca" | "mg" | "po4", number | null>>;

/** Girilmeyen isteğe bağlı değerler (gelişmiş modda SIG'in kesinliğini belirler) */
export function girilmeyenDegerler(istek: IstekDegerleri): { alan: string; ad: string; sembol: string }[] {
  return GIRILEBILEN.filter((g) => istek[g.alan] === undefined || istek[g.alan] === null);
}

function listele(adlar: string[]): string {
  if (adlar.length <= 1) return adlar.join("");
  return `${adlar.slice(0, -1).join(", ")} ve ${adlar[adlar.length - 1]}`;
}

/** "Ca ve Mg girilmedi" gibi cümle; her şey girildiyse null. */
export function girilmeyenCumlesi(istek: IstekDegerleri): string | null {
  const eksik = girilmeyenDegerler(istek);
  if (eksik.length === 0) return null;
  const metin = `${listele(eksik.map((e) => e.ad))} girilmedi`;
  return metin.charAt(0).toLocaleUpperCase("tr") + metin.slice(1);
}

/**
 * SIG'in yanındaki etiket: hüküm vermez, veri durumunu söyler ("Tam veriyle hesaplandı",
 * "Ca ve Mg girilmedi"). Durum, çekirdeğin sig_reliability alanından değil girilen değerlerden
 * çıkarılır: çekirdek K⁺ ve fosfat eksikliğini güvenilirlik değerlendirmesine katmaz.
 */
export function sigEtiketi(istek: IstekDegerleri): { metin: string; tam: boolean } {
  const cumle = girilmeyenCumlesi(istek);
  return cumle === null ? { metin: "Tam veriyle hesaplandı", tam: true } : { metin: cumle, tam: false };
}

/** Çekirdeğin SIG yorumu yarı İngilizce gelir ("… (unmeasured anions likely)"); parantezli İngilizce kısım atılır. */
export function sigYorumu(sonuc: Sonuc): string {
  return (sonuc.sig_interpretation ?? "").replace(/\s*\([A-Za-z ,.'-]+\)\s*$/, "").trim();
}

export interface SidBasamagi {
  kimlik: "simple" | "basic" | "full" | "effective";
  ad: string;
  alt: string;
  /** Hesaplanamadıysa null (örn. laktat girilmediği için temel katman) */
  deger: number | null;
  /** Bu katmanın normal değeri (referans bandının ortası); etkin SID için yok */
  normal: number | null;
  /** Eksik değerle hesaplandı: çubuk kesikli çizilir */
  eksik: boolean;
}

export interface SidMerdiveni {
  basamaklar: SidBasamagi[];
  sig: { deger: number; baslangic: number; bitis: number };
  /** Çubuk ölçeği (mmol/L): en az 15–45, değerler dışarı taşarsa genişler */
  olcek: { min: number; max: number };
}

const SID_ARALIGI = { simple: "sid_simple", basic: "sid_basic", full: "sid_full" } as const;

function ortasi(aralik: { low: number; high: number } | undefined): number | null {
  return aralik ? (aralik.low + aralik.high) / 2 : null;
}

/** Gelişmiş modun SID merdiveni; SIG hesaplanamadıysa (gelişmiş mod değilse) null. */
export function sidMerdiveni(
  sonuc: Sonuc,
  araliklar: Record<string, { low: number; high: number }>,
): SidMerdiveni | null {
  const sig = sonuc.sig;
  const etkin = sonuc.sid_effective;
  if (sig === null || sig === undefined || etkin === null || etkin === undefined) return null;
  const v = sonuc.sid_values;

  const basamaklar: SidBasamagi[] = [
    {
      kimlik: "simple",
      ad: "Na⁺ − Cl⁻",
      alt: "Basit",
      deger: v.sid_simple,
      normal: ortasi(araliklar[SID_ARALIGI.simple]),
      eksik: false,
    },
    {
      kimlik: "basic",
      ad: "… − laktat",
      alt: v.sid_basic === null ? "Laktat girilmedi" : "Temel",
      deger: v.sid_basic,
      normal: ortasi(araliklar[SID_ARALIGI.basic]),
      eksik: false,
    },
    {
      kimlik: "full",
      ad: v.sid_full_status === "complete" ? "… + K⁺ + Ca²⁺ + Mg²⁺" : "… + K⁺ + Ca²⁺ + Mg²⁺ (eksik)",
      alt: "Tam (SIDa)",
      deger: v.sid_full,
      normal: ortasi(araliklar[SID_ARALIGI.full]),
      eksik: v.sid_full_status !== "complete",
    },
    {
      kimlik: "effective",
      ad: "Etkin (SIDe)",
      alt: "albümin, fosfat, pH ve pCO₂ ile",
      deger: etkin,
      normal: null,
      eksik: false,
    },
  ];

  const noktalar = [
    ...basamaklar.flatMap((b) => [b.deger, b.normal]),
    etkin + sig,
  ].filter((n): n is number => n !== null);
  const olcek = {
    min: Math.min(15, Math.floor(Math.min(...noktalar) / 5) * 5),
    max: Math.max(45, Math.ceil(Math.max(...noktalar) / 5) * 5),
  };

  return {
    basamaklar,
    sig: { deger: sig, baslangic: Math.min(etkin, etkin + sig), bitis: Math.max(etkin, etkin + sig) },
    olcek,
  };
}

export interface AnyonAcigiDegerleri {
  olculen: number;
  /** Albümin girilmediyse null */
  duzeltilmis: number | null;
  normal: { low: number; high: number };
  esik: number;
  /** Çubuk ölçeği: en az 0–30 */
  olcek: { min: number; max: number };
  metin: string;
}

/**
 * Anyon açığı bölümü. Karşılaştırmalar ekranda yazılan (1 ondalık) değerle yapılır; yoksa sınırda
 * yuvarlanan bir değer eşiğin üstünde yazılı görünüp altında sayılırdı.
 */
export function anyonAcigi(
  sonuc: Sonuc,
  normal: { low: number; high: number },
  esik: number,
): AnyonAcigiDegerleri {
  const olculen = Number((sonuc.anion_gap ?? 0).toFixed(1));
  const duzeltilmis =
    sonuc.anion_gap_corrected === null || sonuc.anion_gap_corrected === undefined
      ? null
      : Number(sonuc.anion_gap_corrected.toFixed(1));
  const noktalar = [olculen, duzeltilmis ?? 0, esik];
  return {
    olculen,
    duzeltilmis,
    normal,
    esik,
    olcek: { min: 0, max: Math.max(30, Math.ceil((Math.max(...noktalar) + 3) / 5) * 5) },
    metin: anyonAcigiMetni(olculen, duzeltilmis, esik),
  };
}

function anyonAcigiMetni(olculen: number, duzeltilmis: number | null, esik: number): string {
  if (duzeltilmis === null) {
    const yon = olculen > esik ? "üstünde" : "altında";
    return `Ölçülen değer tarama eşiğinin (${esik}) ${yon}. Albümin girilmediği için düzeltilmiş değer hesaplanamadı.`;
  }
  const olculenUstte = olculen > esik;
  const duzeltilmisUstte = duzeltilmis > esik;
  if (olculenUstte && duzeltilmisUstte) return `İkisi de tarama eşiğinin (${esik}) üstünde.${duzeltmeYonu(olculen, duzeltilmis)}`;
  if (!olculenUstte && !duzeltilmisUstte) return `İkisi de tarama eşiğinin (${esik}) altında.${duzeltmeYonu(olculen, duzeltilmis)}`;
  if (duzeltilmisUstte) {
    return `Ölçülen değer tarama eşiğinin (${esik}) altında; albümine göre düzeltilince eşiğin üstüne çıkıyor.`;
  }
  return `Ölçülen değer tarama eşiğinin (${esik}) üstünde; albümine göre düzeltilince eşiğin altına iniyor.`;
}

function duzeltmeYonu(olculen: number, duzeltilmis: number): string {
  if (duzeltilmis > olculen) return " Albümin düşük olduğu için düzeltilmiş değer ölçülenden büyük.";
  if (duzeltilmis < olculen) return " Albümin yüksek olduğu için düzeltilmiş değer ölçülenden küçük.";
  return "";
}
