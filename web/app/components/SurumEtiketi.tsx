"use client";

import { useMeta } from "./MetaProvider";

// Sürüm tek kaynaktan (kökteki __init__.py) gelir; arayüzde sabit yazılmaz
export default function SurumEtiketi() {
  const meta = useMeta();

  if (meta.tur === "yukleniyor") return <p>Sürüm alınıyor…</p>;
  if (meta.tur === "hata") return <p>API’ye ulaşılamadı</p>;
  return <p>v{meta.meta.version}</p>;
}
