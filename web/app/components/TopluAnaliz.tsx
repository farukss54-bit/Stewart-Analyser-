"use client";

import { useRef, useState } from "react";
import { api, type TopluYanit } from "../lib/api";
import { sayiYaz, simgesizMetin } from "../lib/bicim";
import type { Mod } from "../lib/form";
import { dosyaIndir } from "../lib/indir";
import { apiModu, ORNEK_CSV, ORNEK_DOSYA_ADI, ozetCumlesi, satirNotlari, sonucDosyaAdi } from "../lib/toplu";
import dugme from "./Button.module.css";
import styles from "./TopluAnaliz.module.css";

type Durum =
  | { tur: "bosta" }
  | { tur: "suruyor" }
  | { tur: "okunamadi" }
  | { tur: "ag" }
  | { tur: "sunucu" }
  | { tur: "reddedildi" }
  | { tur: "gecersiz"; hatalar: string[] }
  | { tur: "hazir"; mod: Mod; yanit: TopluYanit };

const CSV_TURU = "text/csv;charset=utf-8";

const HATA_METNI = {
  okunamadi: "Dosya okunamadı. Başka bir dosya seçip yeniden deneyin.",
  ag: "API’ye ulaşılamadı. Sunucunun çalıştığından emin olun ve yeniden deneyin.",
  sunucu: "API beklenmeyen bir hata verdi. Yeniden deneyin.",
  reddedildi: "API dosyayı kabul etmedi. Dosyayı kontrol edip yeniden deneyin.",
} as const;

/** Toplu analiz: CSV dosyasındaki her satır ayrı bir analizdir. Mod, üst çubuktaki seçimdir. */
export default function TopluAnaliz({ mod }: { mod: Mod }) {
  const [dosya, setDosya] = useState<File | null>(null);
  const [durum, setDurum] = useState<Durum>({ tur: "bosta" });
  const secici = useRef<HTMLInputElement>(null);
  const sonIstek = useRef<AbortController | null>(null);

  const suruyor = durum.tur === "suruyor";

  function dosyaSecildi(secilen: File | null) {
    if (!secilen) return;
    sonIstek.current?.abort();
    setDosya(secilen);
    setDurum({ tur: "bosta" });
  }

  async function analizEt() {
    if (!dosya || suruyor) return;
    sonIstek.current?.abort();
    const iptal = new AbortController();
    sonIstek.current = iptal;
    setDurum({ tur: "suruyor" });

    let metin: string;
    try {
      metin = await dosya.text();
    } catch {
      setDurum({ tur: "okunamadi" });
      return;
    }

    try {
      const sonuc = await api.toplu(metin, apiModu(mod), iptal.signal);
      if (sonuc.tur !== "tamam") setDurum({ tur: sonuc.tur });
      else if (!sonuc.veri.is_valid) setDurum({ tur: "gecersiz", hatalar: sonuc.veri.errors });
      else setDurum({ tur: "hazir", mod, yanit: sonuc.veri });
    } catch {
      // Yeni dosya seçildi; eski isteğin sonucu gösterilmez
    }
  }

  // Sonuç, analizin yapıldığı modla gösterilir; mod değişince gizlenir (tekli analizdeki gibi)
  const goster = durum.tur === "hazir" && durum.mod === mod ? durum.yanit : null;

  return (
    <section className={styles.toplu} aria-labelledby="toplu-baslik">
      <h1 id="toplu-baslik" className={styles.baslik}>
        Toplu analiz
      </h1>
      <p className={styles.aciklama}>
        CSV dosyasındaki her satır ayrı bir analizdir. <code>ph</code>, <code>pco2</code>, <code>na</code> ve{" "}
        <code>cl</code> sütunları zorunludur. <code>k</code>, <code>lactate</code>, <code>albumin_gl</code> (g/L),{" "}
        <code>be</code>, <code>hco3</code>, <code>ca</code>, <code>mg</code> ve <code>po4</code> isteğe bağlıdır.
        Dosya virgülle ayrılmış ve UTF-8 olmalıdır. Analiz modu: {mod === "hizli" ? "Hızlı" : "Gelişmiş"}.
      </p>

      <div className={styles.eylemler}>
        <button type="button" className={dugme.ghost} onClick={() => dosyaIndir(new Blob([ORNEK_CSV], { type: CSV_TURU }), ORNEK_DOSYA_ADI)}>
          Örnek CSV indir
        </button>
        <button type="button" className={dugme.ghost} onClick={() => secici.current?.click()}>
          CSV dosyası seç
        </button>
        <input
          ref={secici}
          type="file"
          accept=".csv,text/csv"
          hidden
          aria-hidden="true"
          tabIndex={-1}
          onChange={(olay) => {
            dosyaSecildi(olay.target.files?.[0] ?? null);
            // Aynı dosya yeniden seçilebilsin
            olay.target.value = "";
          }}
        />
        <p className={styles.dosyaAdi}>{dosya ? dosya.name : "Dosya seçilmedi."}</p>
      </div>

      <div>
        <button
          type="button"
          className={dugme.dolgun}
          aria-disabled={!dosya || suruyor}
          onClick={analizEt}
        >
          Toplu analiz yap
        </button>
      </div>

      {durum.tur === "suruyor" && <p role="status">Analiz ediliyor…</p>}
      {(durum.tur === "okunamadi" || durum.tur === "ag" || durum.tur === "sunucu" || durum.tur === "reddedildi") && (
        <p className={styles.hata} role="alert">
          {HATA_METNI[durum.tur]}
        </p>
      )}
      {durum.tur === "gecersiz" && (
        <div role="alert">
          <p className={styles.hata}>Dosya analiz edilemedi.</p>
          <ul className={styles.hatalar}>
            {durum.hatalar.map((h) => (
              <li key={h}>{h}</li>
            ))}
          </ul>
        </div>
      )}
      {goster && <Sonuc yanit={goster} />}
    </section>
  );
}

function Sonuc({ yanit }: { yanit: TopluYanit }) {
  function indir() {
    dosyaIndir(new Blob([yanit.csv], { type: CSV_TURU }), sonucDosyaAdi(new Date()));
  }

  return (
    <div className={styles.sonuc}>
      <h2 className={styles.h2} aria-live="polite">
        {ozetCumlesi(yanit.total, yanit.ok, yanit.failed)}
      </h2>
      <div className={styles.kaydir} role="region" aria-label="Satır sonuçları" tabIndex={0}>
        <table className={styles.tablo}>
          <thead>
            <tr>
              <th scope="col">Satır</th>
              <th scope="col">Durum</th>
              <th scope="col" className={styles.sayi}>
                pH
              </th>
              <th scope="col" className={styles.sayi}>
                pCO₂
              </th>
              <th scope="col" className={styles.sayi}>
                BE
              </th>
              <th scope="col">Sonuç</th>
            </tr>
          </thead>
          <tbody>
            {yanit.rows.map((satir) => {
              const notlar = satirNotlari(satir);
              const hatali = satir.status === "ERROR";
              return (
                <tr key={satir.row}>
                  <th scope="row">{satir.row}</th>
                  <td className={hatali ? styles.hataDurumu : undefined}>{hatali ? "Hata" : "Tamam"}</td>
                  <td className={styles.sayi}>{satir.ph == null ? "–" : satir.ph.toFixed(2)}</td>
                  <td className={styles.sayi}>{satir.pco2 == null ? "–" : sayiYaz(satir.pco2)}</td>
                  <td className={styles.sayi}>{satir.be_used == null ? "–" : sayiYaz(satir.be_used, true)}</td>
                  <td>
                    {hatali ? (
                      <span className={styles.hataDurumu}>{simgesizMetin(satir.errors ?? "")}</span>
                    ) : (
                      satir.headline
                    )}
                    {notlar.length > 0 && (
                      <ul className={styles.notlar}>
                        {notlar.map((n, i) => (
                          <li key={i}>{simgesizMetin(n)}</li>
                        ))}
                      </ul>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div>
        <button type="button" className={dugme.ghost} onClick={indir}>
          Sonuçları indir (CSV)
        </button>
      </div>
    </div>
  );
}
