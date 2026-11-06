"use client";

import { useEffect, useState } from "react";

type Durum =
  | { tur: "yukleniyor" }
  | { tur: "hazir"; surum: string }
  | { tur: "hata" };

// Sürüm tek kaynaktan (kökteki __init__.py) gelir; arayüzde sabit yazılmaz
export default function SurumEtiketi() {
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

  if (durum.tur === "yukleniyor") return <p>Sürüm alınıyor…</p>;
  if (durum.tur === "hata") return <p>API’ye ulaşılamadı</p>;
  return <p>v{durum.surum}</p>;
}
