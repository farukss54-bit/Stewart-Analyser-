"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Meta } from "../lib/api";

type MetaDurumu = { tur: "yukleniyor" } | { tur: "hazir"; meta: Meta } | { tur: "hata" };

const MetaBaglami = createContext<MetaDurumu>({ tur: "yukleniyor" });

// /api/meta bir kez alınır: sürüm, fizyolojik sınırlar ve eşikler API'den gelir, arayüzde yazılmaz
export function MetaProvider({ children }: { children: ReactNode }) {
  const [durum, setDurum] = useState<MetaDurumu>({ tur: "yukleniyor" });

  useEffect(() => {
    const iptal = new AbortController();
    api
      .meta(iptal.signal)
      .then((sonuc) => setDurum(sonuc.tur === "tamam" ? { tur: "hazir", meta: sonuc.veri } : { tur: "hata" }))
      .catch(() => {
        // Bileşen kapandığı için vazgeçildi; yapılacak bir şey yok
      });
    return () => iptal.abort();
  }, []);

  return <MetaBaglami value={durum}>{children}</MetaBaglami>;
}

export function useMeta(): MetaDurumu {
  return useContext(MetaBaglami);
}
