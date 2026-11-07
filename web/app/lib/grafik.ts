import { sayiYaz } from "./bicim";
import type { MekanizmaSatiri, Sonuc, Yon } from "./sonuc";

// ---------------------------------------------------------------------------
// Baz açığı şelalesi
// ---------------------------------------------------------------------------

export interface SelaleBasamagi {
  ad: string;
  /** Bu basamağın etkisi (mEq/L); toplam satırında ölçülen baz fazlası */
  deger: number;
  /** Çubuğun başladığı ve bittiği birikmiş değer (toplam satırında 0 ve toplam) */
  bas: number;
  son: number;
  yon: Yon;
  toplam: boolean;
  /** Artık satırı eksik değerlerin payını da içeriyor (mekanizma listesindeki gibi soluk çizilir) */
  soluk: boolean;
}

export interface Selale {
  basamaklar: SelaleBasamagi[];
  /** Eksenin sol ve sağ ucu (mEq/L): sıfırı ve tüm birikmiş değerleri kapsar */
  alt: number;
  ust: number;
}

/**
 * Sıfırdan başlanır, her mekanizmanın etkisi eklenir, sonda ölçülen baz fazlasına ulaşılır.
 * Basamaklar mekanizma listesiyle aynı satırlardır (küçük etkiler dahil); böylece iki gösterim aynı
 * sayıları taşır. Toplam, çekirdeğin toplam metabolik etkisidir (satırların yuvarlanmış toplamı değil).
 */
export function bazAcigiSelalesi(satirlar: MekanizmaSatiri[], toplam: number): Selale {
  let birikmis = 0;
  const basamaklar: SelaleBasamagi[] = satirlar.map((s) => {
    const bas = birikmis;
    birikmis += s.etki;
    return { ad: s.ad, deger: s.etki, bas, son: birikmis, yon: s.yon, toplam: false, soluk: s.soluk };
  });
  basamaklar.push({
    ad: "Toplam (ölçülen baz fazlası)",
    deger: toplam,
    bas: 0,
    son: toplam,
    yon: toplam < 0 ? "asit" : "baz",
    toplam: true,
    soluk: false,
  });

  const noktalar = [0, ...basamaklar.flatMap((b) => [b.bas, b.son])];
  const alt = Math.min(...noktalar);
  const ust = Math.max(...noktalar);
  // Tüm değerler sıfırsa eksen çökmesin
  const pay = ust - alt === 0 ? 1 : (ust - alt) * 0.06;
  return { basamaklar, alt: alt - pay, ust: ust + pay };
}

/** Çubuğun eksen üzerindeki yeri (yüzde): soldan başlangıç ve genişlik */
export function selaleKonumu(basamak: SelaleBasamagi, selale: Selale): { sol: number; genislik: number } {
  const aralik = selale.ust - selale.alt;
  const sol = ((Math.min(basamak.bas, basamak.son) - selale.alt) / aralik) * 100;
  return { sol, genislik: (Math.abs(basamak.son - basamak.bas) / aralik) * 100 };
}

/** Sıfır çizgisinin eksen üzerindeki yeri (yüzde) */
export function selaleSifiri(selale: Selale): number {
  return ((0 - selale.alt) / (selale.ust - selale.alt)) * 100;
}

// ---------------------------------------------------------------------------
// Güçlü iyon farkı sütunları
// ---------------------------------------------------------------------------

export interface SidSutunlari {
  na: number;
  cl: number;
  /** Na⁺ − Cl⁻ (çekirdeğin SID_simple değeri) */
  fark: number;
  /** Aynı Na⁺ ile klorür normal SID'de kaç olurdu */
  normalCl: number;
  /** Sütun yükseklikleri (yüzde, ortak ölçek) */
  naYuzde: number;
  clYuzde: number;
  farkYuzde: number;
  normalYuzde: number;
}

/**
 * Na⁺ ve Cl⁻ sütunları; aradaki fark güçlü iyon farkıdır. Normal çizgi, normal SID'ye (aralığın
 * ortası, API'den) göre klorürün olması gereken yeridir.
 */
export function sidSutunlari(na: number, cl: number, sonuc: Sonuc, normalSid: number): SidSutunlari {
  const fark = sonuc.sid_values.sid_simple;
  const normalCl = na - normalSid;
  const olcek = Math.max(na, cl, normalCl) * 1.06;
  const yuzde = (deger: number) => (deger / olcek) * 100;
  return {
    na,
    cl,
    fark,
    normalCl,
    naYuzde: yuzde(na),
    clYuzde: yuzde(cl),
    farkYuzde: yuzde(Math.max(fark, 0)),
    normalYuzde: yuzde(normalCl),
  };
}

/** Grafiğin altındaki tek cümle: yön yorumu yapmaz, yalnızca sayıları söyler */
export function sidCumlesi(s: SidSutunlari, normalSid: number): string {
  return `Na⁺ − Cl⁻ = ${sayiYaz(s.fark)} mmol/L; normalde yaklaşık ${Math.round(normalSid)}.`;
}
