import { describe, expect, it } from "vitest";
import { sayiYaz, simgesizMetin } from "./bicim";

describe("sayiYaz", () => {
  it("bir ondalık basamakla yazar", () => {
    expect(sayiYaz(14.74)).toBe("14.7");
    expect(sayiYaz(14)).toBe("14.0");
  });

  it("eksiyi tipografik eksiyle, işaretli modda artıyı da yazar", () => {
    expect(sayiYaz(-10.4)).toBe("−10.4");
    expect(sayiYaz(-10.4, true)).toBe("−10.4");
    expect(sayiYaz(2.1, true)).toBe("+2.1");
    expect(sayiYaz(2.1)).toBe("2.1");
  });

  it("sıfıra yuvarlanan değerde işaret yazmaz", () => {
    expect(sayiYaz(-0.04, true)).toBe("0.0");
    expect(sayiYaz(0, true)).toBe("0.0");
  });
});

describe("simgesizMetin", () => {
  it("baştaki uyarı simgesini ve boşluğu atar, geri kalana dokunmaz", () => {
    expect(simgesizMetin("⚠️ pH (7.20) asidemi gösteriyor ama BE (+5.0) pozitif. İşaret hatası olabilir!")).toBe(
      "pH (7.20) asidemi gösteriyor ama BE (+5.0) pozitif. İşaret hatası olabilir!",
    );
  });

  it("simge yoksa metni değiştirmez", () => {
    expect(simgesizMetin("Değer tutarlı.")).toBe("Değer tutarlı.");
  });
});
