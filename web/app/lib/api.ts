import type { components } from "./api-types";

// Tipler api-types.ts'ten gelir (API şemasından üretilir); elle yazılmaz
export type Meta = components["schemas"]["MetaResponse"];
export type DerivedRequest = components["schemas"]["DerivedRequest"];
export type DerivedResponse = components["schemas"]["DerivedResponse"];
export type AnalyzeRequest = components["schemas"]["AnalyzeRequest"];
export type AnalyzeResponse = components["schemas"]["AnalyzeResponse"];

// API yanıt vermezse istek sonsuza kadar beklemesin
const ZAMAN_ASIMI_MS = 8000;

/**
 * İstek sonucu. Hata türleri ayrıdır çünkü kullanıcıya söylenecek şey farklıdır:
 * - ag: API'ye ulaşılamadı
 * - reddedildi: API isteği geçersiz buldu (422); arayüz sınır denetimini geçtiyse beklenmez
 * - sunucu: API hata verdi (5xx ya da beklenmeyen yanıt)
 */
export type ApiSonuc<T> =
  | { tur: "tamam"; veri: T }
  | { tur: "ag" }
  | { tur: "reddedildi" }
  | { tur: "sunucu" };

async function istek<T>(yol: string, init?: RequestInit, signal?: AbortSignal): Promise<ApiSonuc<T>> {
  const zamanAsimi = AbortSignal.timeout(ZAMAN_ASIMI_MS);
  try {
    const yanit = await fetch(yol, {
      ...init,
      signal: signal ? AbortSignal.any([signal, zamanAsimi]) : zamanAsimi,
    });
    if (yanit.status === 422) return { tur: "reddedildi" };
    if (!yanit.ok) return { tur: "sunucu" };
    try {
      return { tur: "tamam", veri: (await yanit.json()) as T };
    } catch (hata) {
      // Yanıt JSON değilse API'ye ulaşılmıştır ama doğru çalışmıyordur
      if (hata instanceof SyntaxError) return { tur: "sunucu" };
      throw hata;
    }
  } catch (hata) {
    // Çağıran vazgeçtiyse (örn. yeni değer yazıldı) bu bir hata değildir; çağıran sonucu yok sayar
    if (signal?.aborted) throw hata;
    return { tur: "ag" };
  }
}

function gonder(govde: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(govde),
  };
}

export const api = {
  meta: (signal?: AbortSignal) => istek<Meta>("/api/meta", undefined, signal),
  turetilmis: (govde: DerivedRequest, signal?: AbortSignal) =>
    istek<DerivedResponse>("/api/derived", gonder(govde), signal),
  analiz: (govde: AnalyzeRequest, signal?: AbortSignal) =>
    istek<AnalyzeResponse>("/api/analyze", gonder(govde), signal),
};
