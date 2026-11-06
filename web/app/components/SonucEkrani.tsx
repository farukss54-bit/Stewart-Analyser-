import { useEffect, useRef } from "react";
import type { AnalyzeRequest, Meta } from "../lib/api";
import { notGruplari, ozetSatirlari, uyarilar, type Sonuc } from "../lib/sonuc";
import MekanizmaListesi from "./MekanizmaListesi";
import Notlar from "./Notlar";
import styles from "./SonucEkrani.module.css";
import TemelDegerler from "./TemelDegerler";

interface Props {
  /** Analizin yapıldığı girdiler (sonuçla birlikte tutulur; formdaki güncel değerler değil) */
  istek: AnalyzeRequest;
  sonuc: Sonuc;
  meta: Meta;
}

export default function SonucEkrani({ istek, sonuc, meta }: Props) {
  const baslik = useRef<HTMLHeadingElement>(null);

  // Sonuç göründüğünde odak başlığa geçer: ekran okuyucu sonucu okur, dar ekranda sayfa oraya kayar
  useEffect(() => {
    baslik.current?.focus();
  }, []);

  const ozet = ozetSatirlari(sonuc);
  const notlar = notGruplari(sonuc.cds_notes ?? []);
  const uyari = uyarilar(sonuc);
  const desenNotu = sonuc.headline?.pattern_note;

  return (
    <div className={styles.sonuc}>
      <section className={styles.lead} aria-label="Sonuç özeti">
        {/* Başlık metni çekirdekten gelir (headline); arayüz klinik cümle kurmaz */}
        <h1 ref={baslik} tabIndex={-1} className={styles.baslik}>
          {sonuc.headline?.dominant_mechanism || "Sonuç özeti üretilemedi."}
        </h1>
        {desenNotu && <p className={styles.desen}>{desenNotu}</p>}
        <dl className={styles.ozet}>
          {ozet.map((s) => (
            <div key={s.ad} className={styles.ozetSatiri}>
              <dt>{s.ad}</dt>
              <dd>{s.deger}</dd>
            </div>
          ))}
        </dl>
      </section>

      <TemelDegerler istek={istek} sonuc={sonuc} araliklar={meta.reference_ranges} />
      <MekanizmaListesi sonuc={sonuc} esik={meta.clinical_significance_threshold} />
      {notlar.length > 0 && <Notlar gruplar={notlar} />}

      {uyari.length > 0 && (
        <section aria-labelledby="uyarilar-baslik">
          <h2 id="uyarilar-baslik" className={styles.h2}>
            Uyarılar
          </h2>
          <ul className={styles.uyarilar}>
            {uyari.map((u) => (
              <li key={u}>{u}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
