import { describe, expect, it } from "vitest";
import type { AnalyzeRequest } from "./api";
import { girdiOzeti } from "./girdiOzeti";

const TEMEL: AnalyzeRequest = { ph: 7.3, pco2: 31, na: 141, cl: 114 };

describe("girdiOzeti", () => {
  it("zorunlu dört değeri yazar", () => {
    expect(girdiOzeti(TEMEL)).toBe("pH 7.30, pCO₂ 31 mmHg, Na⁺ 141, Cl⁻ 114");
  });

  it("girilen isteğe bağlı değerleri tasarımdaki sırayla ekler", () => {
    const ozet = girdiOzeti({ ...TEMEL, k: 4.1, lactate: 2.8, albumin: 25, albumin_unit: "g/L" });
    expect(ozet).toBe("pH 7.30, pCO₂ 31 mmHg, Na⁺ 141, Cl⁻ 114, K⁺ 4.1, laktat 2.8, albümin 25 g/L");
  });

  it("albümin birimini girildiği gibi yazar", () => {
    expect(girdiOzeti({ ...TEMEL, albumin: 2.5, albumin_unit: "g/dL" })).toContain("albümin 2.5 g/dL");
  });

  it("girilmeyen değerleri yazmaz", () => {
    const ozet = girdiOzeti({ ...TEMEL, lactate: null, albumin: null });
    expect(ozet).not.toContain("laktat");
    expect(ozet).not.toContain("albümin");
  });

  it("BE ile BD'yi ayırır; 0 değeri de yazılır", () => {
    expect(girdiOzeti({ ...TEMEL, be: -6 })).toContain("BE −6.0");
    expect(girdiOzeti({ ...TEMEL, be: 5, is_be_base_deficit: true })).toContain("BD +5.0");
    expect(girdiOzeti({ ...TEMEL, be: 0 })).toContain("BE 0.0");
  });

  it("gelişmiş değerleri ekler", () => {
    const ozet = girdiOzeti({ ...TEMEL, ca: 1.2, mg: 0.8, po4: 1.1, hco3: 15 });
    expect(ozet).toContain("Ca²⁺ 1.2, Mg²⁺ 0.8, fosfat 1.1");
    expect(ozet).toContain("HCO₃⁻ 15");
  });
});
