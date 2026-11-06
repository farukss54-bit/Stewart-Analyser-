"use client";

import { useEffect, useState } from "react";

type Durum =
  | { tur: "yukleniyor" }
  | { tur: "hazir"; surum: string }
  | { tur: "hata" };

// Aşama 0: arayüzün API'ye ulaştığını gösteren geçici bileşen.
export default function ApiStatus() {
  const [durum, setDurum] = useState<Durum>({ tur: "yukleniyor" });

  useEffect(() => {
    let iptal = false;
    // API yanıt vermezse bağlantı sonsuza kadar beklemesin
    fetch("/api/meta", { signal: AbortSignal.timeout(8000) })
      .then((yanit) => {
        if (!yanit.ok) throw new Error(String(yanit.status));
        return yanit.json() as Promise<{ version: string }>;
      })
      .then((veri) => {
        if (!iptal) setDurum({ tur: "hazir", surum: veri.version });
      })
      .catch(() => {
        if (!iptal) setDurum({ tur: "hata" });
      });
    return () => {
      iptal = true;
    };
  }, []);

  if (durum.tur === "yukleniyor") return <p>API’ye bağlanılıyor…</p>;
  if (durum.tur === "hata") {
    return (
      <p role="alert">
        API’ye ulaşılamadı. Python sunucusunun çalıştığından emin olun
        (uvicorn api.main:app --port 8000).
      </p>
    );
  }
  return <p>API hazır, sürüm v{durum.surum}</p>;
}
