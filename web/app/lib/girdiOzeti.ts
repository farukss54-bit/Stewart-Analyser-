import type { AnalyzeRequest } from "./api";
import { sayiYaz } from "./bicim";

/**
 * Analizin yapıldığı değerlerin tek satırlık özeti (dar ekranda form gizlenince sonucun üstünde görünür).
 * Girilmeyen değerler yazılmaz; bu satır yalnızca hekimin ne girdiğini hatırlatır.
 */
export function girdiOzeti(istek: AnalyzeRequest): string {
  const parcalar: string[] = [`pH ${istek.ph.toFixed(2)}`, `pCO₂ ${istek.pco2} mmHg`, `Na⁺ ${istek.na}`, `Cl⁻ ${istek.cl}`];
  const ekle = (ad: string, deger: number | null | undefined, birim = "") => {
    if (deger !== null && deger !== undefined) parcalar.push(`${ad} ${deger}${birim}`);
  };
  ekle("K⁺", istek.k);
  ekle("Ca²⁺", istek.ca);
  ekle("Mg²⁺", istek.mg);
  ekle("fosfat", istek.po4);
  ekle("laktat", istek.lactate);
  ekle("albümin", istek.albumin, ` ${istek.albumin_unit ?? "g/L"}`);
  ekle("HCO₃⁻", istek.hco3);
  if (istek.be !== null && istek.be !== undefined) {
    parcalar.push(`${istek.is_be_base_deficit ? "BD" : "BE"} ${sayiYaz(istek.be, true)}`);
  }
  return parcalar.join(", ");
}
