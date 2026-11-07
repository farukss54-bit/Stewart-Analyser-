"use client";

import { useState } from "react";
import { api, type AnalyzeRequest } from "../lib/api";
import { dosyaIndir } from "../lib/indir";
import buttons from "./Button.module.css";
import styles from "./CsvIndir.module.css";

// Streamlit'teki indirmeyle aynı dosya adı
const DOSYA_ADI = "stewart_result.csv";

type Durum = "bosta" | "iniyor" | "indi" | "ag" | "sunucu" | "reddedildi";

const HATA_METNI: Record<"ag" | "sunucu" | "reddedildi", string> = {
  ag: "API’ye ulaşılamadı; dosya indirilemedi. Yeniden deneyin.",
  sunucu: "API beklenmeyen bir hata verdi; dosya indirilemedi. Yeniden deneyin.",
  reddedildi: "API girilen değerleri kabul etmedi; dosya indirilemedi.",
};

/** Sonucu, analizin yapıldığı girdilerle CSV olarak indirir (formdaki güncel değerlerle değil) */
export default function CsvIndir({ istek }: { istek: AnalyzeRequest }) {
  const [durum, setDurum] = useState<Durum>("bosta");

  async function indir() {
    if (durum === "iniyor") return;
    setDurum("iniyor");
    const sonuc = await api.csv(istek);
    if (sonuc.tur === "tamam") {
      dosyaIndir(sonuc.veri, DOSYA_ADI);
      setDurum("indi");
    } else {
      setDurum(sonuc.tur);
    }
  }

  return (
    <div className={styles.alan}>
      <button type="button" className={buttons.ghost} onClick={indir} aria-disabled={durum === "iniyor"}>
        Sonucu indir (CSV)
      </button>
      {durum === "iniyor" && <p role="status">Dosya hazırlanıyor…</p>}
      {durum === "indi" && <p role="status">Dosya indirildi.</p>}
      {(durum === "ag" || durum === "sunucu" || durum === "reddedildi") && (
        <p className={styles.hata} role="alert">
          {HATA_METNI[durum]}
        </p>
      )}
    </div>
  );
}
