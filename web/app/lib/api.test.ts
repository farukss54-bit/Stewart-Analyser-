import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";

function yanitla(durum: number, govde: string): Response {
  return new Response(govde, { status: durum });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("api istemcisi", () => {
  it("başarılı yanıtı çözer", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(yanitla(200, '{"version":"3.5.0"}')));
    expect(await api.meta()).toEqual({ tur: "tamam", veri: { version: "3.5.0" } });
  });

  it("422'yi 'reddedildi' olarak ayırır", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(yanitla(422, '{"detail":[]}')));
    expect(await api.turetilmis({ ph: 7.3, pco2: 31 })).toEqual({ tur: "reddedildi" });
  });

  it("5xx'i 'sunucu' hatası sayar", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(yanitla(500, "hata")));
    expect(await api.meta()).toEqual({ tur: "sunucu" });
  });

  it("JSON olmayan yanıtı 'sunucu' hatası sayar, ağ hatası saymaz", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(yanitla(200, "<html>proxy hatası</html>")));
    expect(await api.meta()).toEqual({ tur: "sunucu" });
  });

  it("ağ hatasını 'ag' olarak bildirir", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    expect(await api.meta()).toEqual({ tur: "ag" });
  });

  it("çağıran vazgeçtiyse hata olarak bildirmez, fırlatır", async () => {
    const iptal = new AbortController();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async () => {
        iptal.abort();
        throw new DOMException("iptal", "AbortError");
      }),
    );
    await expect(api.meta(iptal.signal)).rejects.toThrow();
  });

  it("analiz isteğini JSON olarak gönderir", async () => {
    const sahteFetch = vi.fn().mockResolvedValue(yanitla(200, '{"is_valid":true}'));
    vi.stubGlobal("fetch", sahteFetch);
    await api.analiz({ ph: 7.3, pco2: 31, na: 141, cl: 114 });
    const [yol, init] = sahteFetch.mock.calls[0];
    expect(yol).toBe("/api/analyze");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ ph: 7.3, pco2: 31, na: 141, cl: 114 });
  });
});
