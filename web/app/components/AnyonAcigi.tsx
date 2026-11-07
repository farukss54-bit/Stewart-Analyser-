import { sayiYaz } from "../lib/bicim";
import { anyonAcigi, yuzde, type Sonuc } from "../lib/sonuc";
import styles from "./AnyonAcigi.module.css";

interface Props {
  sonuc: Sonuc;
  /** Normal bant (API'den); bilinmiyorsa bant çizilmez */
  normal: { low: number; high: number } | undefined;
  /** Tarama eşiği (API'den) */
  esik: number;
}

// Etiketleri ayırma eşiği: iki işaret arası (çubuk genişliğinin yüzdesi)
const YAKINLIK_YUZDESI = 12;

/** Ölçülen ve albümine göre düzeltilmiş anyon açığı, tarama eşiğiyle birlikte */
export default function AnyonAcigi({ sonuc, normal, esik }: Props) {
  const ag = anyonAcigi(sonuc, normal ?? { low: 0, high: 0 }, esik);
  const konum = (deger: number) => yuzde(deger, ag.olcek);
  const { olculen, duzeltilmis } = ag;
  // İşaretler çubuğun %12'sinden yakınsa etiketler ayrı yönlere yaslanır
  const yakin = duzeltilmis !== null && Math.abs(konum(olculen) - konum(duzeltilmis)) < YAKINLIK_YUZDESI;
  const olculenAlt = duzeltilmis !== null && olculen <= duzeltilmis;
  const yasla = (kucuk: boolean) => (!yakin ? "" : kucuk ? styles.solaYasli : styles.sagaYasli);

  return (
    <section aria-labelledby="ag-baslik">
      <h2 id="ag-baslik" className={styles.h2}>
        Anyon açığı
      </h2>
      <div className={styles.kutu}>
        <dl className={styles.sayilar}>
          <div className={styles.sayi}>
            <dt>Ölçülen</dt>
            <dd>
              {sayiYaz(olculen)}
              <span>mmol/L</span>
            </dd>
          </div>
          <div className={`${styles.sayi} ${styles.duzeltilmis}`}>
            <dt>Albümine göre düzeltilmiş</dt>
            <dd>
              {duzeltilmis === null ? "—" : sayiYaz(duzeltilmis)}
              {duzeltilmis !== null && <span>mmol/L</span>}
            </dd>
          </div>
        </dl>

        <div className={styles.cubuk} aria-hidden="true">
          {normal && (
            <span
              className={styles.bant}
              style={{ left: `${konum(normal.low)}%`, width: `${konum(normal.high) - konum(normal.low)}%` }}
            />
          )}
          {duzeltilmis !== null && (
            <span
              className={styles.kayma}
              style={{
                left: `${konum(Math.min(olculen, duzeltilmis))}%`,
                width: `${konum(Math.max(olculen, duzeltilmis)) - konum(Math.min(olculen, duzeltilmis))}%`,
              }}
            />
          )}
          <span className={styles.esik} style={{ left: `${konum(esik)}%` }} />
          <span className={styles.esikEtiketi} style={{ left: `${konum(esik)}%` }}>
            Tarama eşiği {esik}
          </span>
          <span className={`${styles.isaret} ${styles.olculen}`} style={{ left: `calc(${konum(olculen)}% - 2px)` }} />
          <span className={`${styles.etiket} ${yasla(olculenAlt)}`} style={{ left: `${konum(olculen)}%` }}>
            {sayiYaz(olculen)}
          </span>
          {duzeltilmis !== null && (
            <>
              <span
                className={`${styles.isaret} ${styles.duzeltilmisIsaret}`}
                style={{ left: `calc(${konum(duzeltilmis)}% - 2px)` }}
              />
              <span className={`${styles.etiket} ${styles.etiketAsit} ${yasla(!olculenAlt)}`} style={{ left: `${konum(duzeltilmis)}%` }}>
                {sayiYaz(duzeltilmis)}
              </span>
            </>
          )}
        </div>

        <p className={styles.metin}>{ag.metin}</p>
      </div>
    </section>
  );
}
