import { useState } from "react";
import { sayiYaz } from "../lib/bicim";
import { cubukYariGenisligi, mekanizmaSatirlari, type MekanizmaSatiri, type Sonuc } from "../lib/sonuc";
import styles from "./MekanizmaListesi.module.css";

interface Props {
  sonuc: Sonuc;
  /** Anlamlılık eşiği (mEq/L), API'den */
  esik: number;
  /** Gelişmiş mod: ölçülmemiş anyonlar SIG satırında ayrıca değerlendirilir */
  gelismis?: boolean;
}

export default function MekanizmaListesi({ sonuc, esik, gelismis }: Props) {
  const [kucukAcik, setKucukAcik] = useState(false);

  const satirlar = mekanizmaSatirlari(sonuc, esik, gelismis);
  const yari = cubukYariGenisligi(satirlar);
  const gorunen = satirlar.filter((s) => !s.kucuk);
  const gizli = satirlar.filter((s) => s.kucuk);
  const toplam = sonuc.mechanism_analysis?.total_metabolic_effect ?? sonuc.be_used;

  const toplamEtiketi =
    gizli.length > 0 && !kucukAcik
      ? `Gizli ${gizli.length} mekanizma dahil toplam etki`
      : "Toplam etki (ölçülen baz fazlası)";

  return (
    <section className={styles.liste} aria-labelledby="mekanizma-baslik">
      <h2 id="mekanizma-baslik" className={styles.h2}>
        Hangi mekanizma ne kadar etki ediyor?
      </h2>
      <p className={styles.altBaslik}>
        Her çubuk, mekanizmanın baz fazlasına katkısını gösterir. Sola uzanan çubuk asit yönünde, sağa uzanan baz
        yönündedir. Ölçek ±{yari} mEq/L.
      </p>
      <div className={styles.eksen} aria-hidden="true">
        <span className={styles.asit}>Asit yönü</span>
        <span className={styles.sifir}>0</span>
        <span className={`${styles.baz} ${styles.sagda}`}>Baz yönü</span>
      </div>

      {gorunen.length === 0 && <p className={styles.bos}>Hiçbir mekanizmanın etkisi {esik} mEq/L’yi aşmıyor.</p>}
      {gorunen.map((s) => (
        <Satir key={s.kimlik} satir={s} yari={yari} />
      ))}

      {gizli.length > 0 && (
        <button
          type="button"
          className={styles.dugme}
          aria-expanded={kucukAcik}
          onClick={() => setKucukAcik(!kucukAcik)}
        >
          {kucukAcik
            ? "Küçük etkileri gizle"
            : `Etkisi küçük ${gizli.length} mekanizmayı göster (her biri ${esik} mEq/L’yi aşmıyor)`}
        </button>
      )}
      {kucukAcik && gizli.map((s) => <Satir key={s.kimlik} satir={s} yari={yari} />)}

      <div className={styles.toplam}>
        <span>{toplamEtiketi}</span>
        <span className={styles.toplamDeger}>{sayiYaz(toplam, true)} mEq/L</span>
      </div>
    </section>
  );
}

function Satir({ satir, yari }: { satir: MekanizmaSatiri; yari: number }) {
  const genislik = Math.min(50, (Math.abs(satir.etki) / yari) * 50);
  const asit = satir.yon === "asit";
  return (
    <div className={`${styles.satir} ${satir.soluk ? styles.soluk : ""}`}>
      <div className={styles.ust}>
        <span className={styles.ad}>{satir.ad}</span>
        {satir.etiket && <span className={`${styles.etiket} ${styles[satir.yon]}`}>{satir.etiket}</span>}
        <span className={`${styles.sayi} ${styles[satir.yon]}`}>
          {sayiYaz(satir.etki, true)}
          <span className={styles.birim}>mEq/L</span>
        </span>
      </div>
      <div className={styles.iz} aria-hidden="true">
        <span className={styles.eksenCizgisi} />
        <span
          className={`${styles.cubuk} ${asit ? styles.sol : styles.sag}`}
          style={asit ? { right: "50%", width: `${genislik}%` } : { left: "50%", width: `${genislik}%` }}
        />
      </div>
      <p className={styles.metin}>{satir.metin}</p>
    </div>
  );
}
