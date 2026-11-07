import { describe, expect, it } from "vitest";
import type { TopluSatir } from "./api";
import { apiModu, ORNEK_CSV, ozetCumlesi, satirNotlari, sonucDosyaAdi } from "./toplu";

function satir(ek: Partial<TopluSatir>): TopluSatir {
  return { row: 1, status: "OK", warnings: [], flags: [], ...ek };
}

describe("toplu analiz yardımcıları", () => {
  it("örnek CSV, Streamlit'teki örnekle aynı başlık ve üç satırdır", () => {
    const satirlar = ORNEK_CSV.split("\n");
    expect(satirlar[0]).toBe("ph,pco2,na,cl,k,lactate,albumin_gl,be");
    expect(satirlar).toHaveLength(4);
  });

  it("mod adını API'ninkine çevirir", () => {
    expect(apiModu("hizli")).toBe("quick");
    expect(apiModu("gelismis")).toBe("advanced");
  });

  it("sonuç dosyası adı Streamlit'tekiyle aynı biçimdedir", () => {
    expect(sonucDosyaAdi(new Date(2026, 10, 7, 9, 5))).toBe("stewart_results_20261107_0905.csv");
  });

  it("satır notları yalnızca bilinen işaretleri ve uyarıları içerir", () => {
    const notlar = satirNotlari(
      satir({ warnings: ["Na/Cl şüphesi"], flags: ["HCO3_CALCULATED", "BE_MISMATCH", "SID_FULL_APPROXIMATE"] }),
    );
    expect(notlar).toHaveLength(2);
    expect(notlar[0]).toBe("Na/Cl şüphesi");
    expect(notlar[1]).toContain("BE");
  });

  it("işaretsiz satırın notu yoktur", () => {
    expect(satirNotlari(satir({ flags: ["HCO3_CALCULATED"] }))).toEqual([]);
  });

  it("özet cümlesi üç durumu ayırır", () => {
    expect(ozetCumlesi(3, 3, 0)).toBe("3 satır analiz edildi.");
    expect(ozetCumlesi(3, 2, 1)).toBe("3 satırdan 2 satır analiz edildi, 1 satır hatalı.");
    expect(ozetCumlesi(2, 0, 2)).toBe("2 satırın hiçbiri analiz edilemedi.");
  });
});
