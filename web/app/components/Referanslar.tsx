"use client";

import { useState } from "react";
import { api, type Referans } from "../lib/api";
import dugme from "./Button.module.css";
import styles from "./Referanslar.module.css";

type Durum = { tur: "bosta" } | { tur: "yukleniyor" } | { tur: "hazir"; liste: Referans[] } | { tur: "hata" };

/** Alt bilgideki "Referanslar" bölümü; liste ilk açıldığında API'den alınır */
export default function Referanslar() {
  const [durum, setDurum] = useState<Durum>({ tur: "bosta" });

  function getir() {
    setDurum({ tur: "yukleniyor" });
    api
      .referanslar()
      .then((sonuc) => setDurum(sonuc.tur === "tamam" ? { tur: "hazir", liste: sonuc.veri } : { tur: "hata" }))
      .catch(() => setDurum({ tur: "hata" }));
  }

  return (
    <details
      className={styles.kutu}
      onToggle={(olay) => {
        if (olay.currentTarget.open && (durum.tur === "bosta" || durum.tur === "hata")) getir();
      }}
    >
      <summary className={styles.ozet}>Referanslar</summary>
      {durum.tur === "yukleniyor" && <p role="status">Referanslar yükleniyor…</p>}
      {durum.tur === "hata" && (
        <div className={styles.hata} role="alert">
          <p>Referanslar alınamadı.</p>
          <button type="button" className={dugme.ghost} onClick={getir}>
            Yeniden dene
          </button>
        </div>
      )}
      {durum.tur === "hazir" && (
        <ul className={styles.liste}>
          {durum.liste.map((r) => (
            <li key={r.id}>{r.text}</li>
          ))}
        </ul>
      )}
    </details>
  );
}
