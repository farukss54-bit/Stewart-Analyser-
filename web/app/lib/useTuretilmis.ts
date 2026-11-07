"use client";

import { useEffect, useState } from "react";
import { api, type ApiSonuc, type DerivedRequest, type DerivedResponse } from "./api";

const BEKLEME_MS = 300;

/**
 * pH/pCO₂ ve cihaz değerlerinden HCO₃ ile BE'yi API'ye hesaplatır.
 * Yazarken her tuşta istek atılmaz (bekleme), eskimiş yanıt gösterilmez.
 * İstek yoksa ya da yanıt henüz gelmediyse null döner.
 */
export function useTuretilmis(istek: DerivedRequest | null): ApiSonuc<DerivedResponse> | null {
  const anahtar = istek ? JSON.stringify(istek) : null;
  const [kayit, setKayit] = useState<{ anahtar: string; sonuc: ApiSonuc<DerivedResponse> } | null>(null);

  useEffect(() => {
    if (anahtar === null) return;
    const iptal = new AbortController();
    const zamanlayici = setTimeout(() => {
      api
        .turetilmis(JSON.parse(anahtar) as DerivedRequest, iptal.signal)
        .then((sonuc) => setKayit({ anahtar, sonuc }))
        .catch(() => {
          // Girdi değişti ya da bileşen kapandı; yeni istek zaten yolda
        });
    }, BEKLEME_MS);
    return () => {
      clearTimeout(zamanlayici);
      iptal.abort();
    };
  }, [anahtar]);

  return kayit !== null && kayit.anahtar === anahtar ? kayit.sonuc : null;
}
