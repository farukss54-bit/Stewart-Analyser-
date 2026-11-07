"use client";

import { useState } from "react";
import type { AnalyzeRequest, Meta } from "../lib/api";
import { sayiYaz } from "../lib/bicim";
import {
  bazAcigiSelalesi,
  selaleKonumu,
  selaleSifiri,
  sidCumlesi,
  sidSutunlari,
  type Selale,
  type SelaleBasamagi,
} from "../lib/grafik";
import { mekanizmaSatirlari, toplamEtki, type Sonuc } from "../lib/sonuc";
import dugme from "./Button.module.css";
import styles from "./Grafikler.module.css";

interface Props {
  istek: AnalyzeRequest;
  sonuc: Sonuc;
  meta: Meta;
}

/** İki grafik: baz açığı şelalesi ve güçlü iyon farkı sütunları. Kapalı başlar. */
export default function Grafikler({ istek, sonuc, meta }: Props) {
  const [acik, setAcik] = useState(false);

  return (
    <section className={styles.grafik} aria-labelledby="grafik-baslik">
      <h2 id="grafik-baslik" className={styles.gizli}>
        Grafikler
      </h2>
      <button type="button" className={`${dugme.ghost} ${styles.dugme}`} aria-expanded={acik} onClick={() => setAcik(!acik)}>
        {acik ? "Grafikleri gizle" : "Grafikleri göster: baz açığı şelalesi ve güçlü iyon farkı"}
      </button>
      {acik && (
        <div className={styles.izgara}>
          <SelalePaneli istek={istek} sonuc={sonuc} esik={meta.clinical_significance_threshold} />
          <SidPaneli istek={istek} sonuc={sonuc} normalSid={ortasi(meta.reference_ranges.sid_simple)} />
        </div>
      )}
    </section>
  );
}

function ortasi(aralik: { low: number; high: number }): number {
  return (aralik.low + aralik.high) / 2;
}

function SelalePaneli({ istek, sonuc, esik }: { istek: AnalyzeRequest; sonuc: Sonuc; esik: number }) {
  const satirlar = mekanizmaSatirlari(sonuc, esik, istek.mode === "advanced");
  const selale = bazAcigiSelalesi(satirlar, toplamEtki(sonuc));
  const sifir = selaleSifiri(selale);
  const soluk = satirlar.some((s) => s.soluk);

  return (
    <div className={styles.panel}>
      <h3 className={styles.h3}>Baz açığı şelalesi</h3>
      <p className={styles.alt}>Sıfırdan başlanır, her mekanizma eklenir ve toplam baz fazlasına ulaşılır.</p>
      <div className={styles.selale}>
        {selale.basamaklar.map((b) => (
          <SelaleSatiri key={b.ad} basamak={b} selale={selale} sifir={sifir} />
        ))}
      </div>
      {soluk && <p className={styles.dipnot}>Soluk satır, girilmeyen değerlerin payını da içerir.</p>}
    </div>
  );
}

function SelaleSatiri({ basamak, selale, sifir }: { basamak: SelaleBasamagi; selale: Selale; sifir: number }) {
  const { sol, genislik } = selaleKonumu(basamak, selale);
  return (
    <div className={`${styles.satir} ${basamak.toplam ? styles.toplam : ""} ${basamak.soluk ? styles.soluk : ""}`}>
      <span className={styles.etiket}>{basamak.ad}</span>
      <div className={styles.iz} aria-hidden="true">
        <span className={styles.sifir} style={{ left: `${sifir}%` }} />
        <span className={`${styles.cubuk} ${styles[basamak.yon]}`} style={{ left: `${sol}%`, width: `${genislik}%` }} />
      </div>
      <span className={`${styles.sayi} ${styles[`sayi_${basamak.yon}`]}`}>{sayiYaz(basamak.deger, true)}</span>
    </div>
  );
}

function SidPaneli({ istek, sonuc, normalSid }: { istek: AnalyzeRequest; sonuc: Sonuc; normalSid: number }) {
  const s = sidSutunlari(istek.na, istek.cl, sonuc, normalSid);

  return (
    <div className={styles.panel}>
      <h3 className={styles.h3}>Güçlü iyon farkı</h3>
      <p className={styles.alt}>{sidCumlesi(s, normalSid)}</p>
      <div className={styles.sutunlar}>
        <div className={styles.cizim} aria-hidden="true">
          <div className={styles.sutun}>
            <div className={`${styles.blok} ${styles.na}`} style={{ height: `${s.naYuzde}%` }}>
              <span>{sayiYaz(s.na)}</span>
            </div>
          </div>
          <div className={styles.sutun}>
            <div className={styles.fark} style={{ height: `${s.farkYuzde}%` }}>
              <span>{sayiYaz(s.fark)}</span>
            </div>
            <div className={`${styles.blok} ${styles.cl}`} style={{ height: `${s.clYuzde}%` }}>
              <span>{sayiYaz(s.cl)}</span>
            </div>
          </div>
          <span className={styles.normal} style={{ bottom: `${s.normalYuzde}%` }} />
        </div>
        <div className={styles.adlar} aria-hidden="true">
          <span>Na⁺</span>
          <span>Cl⁻</span>
        </div>
        <p className={styles.dipnot}>
          Kesikli çizgi: aynı Na⁺ ile Cl⁻ normalde yaklaşık {Math.round(s.normalCl)} mmol/L olurdu. Sütunlar mmol/L.
        </p>
      </div>
    </div>
  );
}
