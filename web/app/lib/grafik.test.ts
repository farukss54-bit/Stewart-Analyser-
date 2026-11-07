import { describe, expect, it } from "vitest";
import { bazAcigiSelalesi, selaleKonumu, selaleSifiri, sidCumlesi, sidSutunlari } from "./grafik";
import type { MekanizmaSatiri, Sonuc } from "./sonuc";

function satir(kimlik: MekanizmaSatiri["kimlik"], etki: number, soluk = false): MekanizmaSatiri {
  return {
    kimlik,
    ad: kimlik,
    etki,
    yon: etki < 0 ? "asit" : "baz",
    etiket: null,
    metin: "",
    kucuk: false,
    soluk,
  };
}

// Tasarım örneğindeki dört etki: toplam −10.4
const SATIRLAR = [satir("sid", -11.0), satir("albumin", 4.2), satir("lactate", -2.8), satir("residual", -0.8)];

describe("bazAcigiSelalesi", () => {
  const selale = bazAcigiSelalesi(SATIRLAR, -10.4);

  it("sıfırdan başlar ve her etkiyi biriktirir", () => {
    const [sid, albumin, laktat, artik] = selale.basamaklar;
    expect([sid.bas, sid.son]).toEqual([0, -11]);
    expect(albumin.bas).toBe(-11);
    expect(albumin.son).toBeCloseTo(-6.8);
    expect(laktat.son).toBeCloseTo(-9.6);
    expect(artik.son).toBeCloseTo(-10.4);
  });

  it("son satır çekirdeğin toplamıdır ve sıfırdan başlar", () => {
    const toplam = selale.basamaklar.at(-1)!;
    expect(toplam.toplam).toBe(true);
    expect([toplam.bas, toplam.son, toplam.deger]).toEqual([0, -10.4, -10.4]);
    expect(toplam.yon).toBe("asit");
  });

  it("basamak yönü etkinin işaretinden gelir", () => {
    expect(selale.basamaklar.map((b) => b.yon)).toEqual(["asit", "baz", "asit", "asit", "asit"]);
  });

  it("eksen sıfırı ve tüm birikmiş değerleri kapsar", () => {
    expect(selale.alt).toBeLessThan(-11);
    expect(selale.ust).toBeGreaterThan(0);
  });

  it("çubuk konumu eksen yüzdesidir; sıfır çizgisi eksen içindedir", () => {
    const sifir = selaleSifiri(selale);
    expect(sifir).toBeGreaterThan(0);
    expect(sifir).toBeLessThan(100);
    // Asit çubuğu sıfır çizgisinde biter (sağ ucu = sıfır)
    const sid = selaleKonumu(selale.basamaklar[0], selale);
    expect(sid.sol + sid.genislik).toBeCloseTo(sifir);
    // Baz çubuğu (albümin) −11'den −6.8'e: sıfırın solunda kalır
    const albumin = selaleKonumu(selale.basamaklar[1], selale);
    expect(albumin.sol + albumin.genislik).toBeLessThan(sifir);
  });

  it("soluk işareti artık satırından taşınır", () => {
    const s = bazAcigiSelalesi([satir("sid", -5), satir("residual", -3, true)], -8);
    expect(s.basamaklar.map((b) => b.soluk)).toEqual([false, true, false]);
  });

  it("tüm değerler sıfırsa eksen çökmez", () => {
    const s = bazAcigiSelalesi([satir("sid", 0)], 0);
    expect(s.ust - s.alt).toBeGreaterThan(0);
    expect(Number.isFinite(selaleSifiri(s))).toBe(true);
  });
});

describe("sidSutunlari", () => {
  const sonuc = { sid_values: { sid_simple: 27 } } as unknown as Sonuc;
  const s = sidSutunlari(141, 114, sonuc, 38);

  it("farkı çekirdeğin SID_simple değerinden alır", () => {
    expect(s.fark).toBe(27);
  });

  it("normal klorür, aynı sodyumla normal SID'ye göre bulunur", () => {
    expect(s.normalCl).toBe(103);
  });

  it("sütun yükseklikleri ortak ölçektedir ve %100'ü aşmaz", () => {
    expect(s.naYuzde).toBeGreaterThan(s.clYuzde);
    expect(s.naYuzde).toBeLessThanOrEqual(100);
    expect(s.clYuzde + s.farkYuzde).toBeCloseTo(s.naYuzde);
  });

  it("negatif fark sütun yüksekliğini eksiye indirmez", () => {
    const negatif = sidSutunlari(130, 140, { sid_values: { sid_simple: -10 } } as unknown as Sonuc, 38);
    expect(negatif.farkYuzde).toBe(0);
  });

  it("cümle yalnızca sayıları söyler", () => {
    expect(sidCumlesi(s, 38)).toBe("Na⁺ − Cl⁻ = 27.0 mmol/L; normalde yaklaşık 38.");
  });
});
