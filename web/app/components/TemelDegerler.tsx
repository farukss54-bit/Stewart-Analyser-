import type { AnalyzeRequest, Meta } from "../lib/api";
import { DEGERLER, degerDurumu, gosterilenDeger, normalMetni, yuzde, type DegerKodu, type Sonuc } from "../lib/sonuc";
import styles from "./TemelDegerler.module.css";

interface Props {
  istek: AnalyzeRequest;
  sonuc: Sonuc;
  araliklar: Meta["reference_ranges"];
}

export default function TemelDegerler({ istek, sonuc, araliklar }: Props) {
  const degerler: Record<DegerKodu, number> = {
    ph: istek.ph,
    pco2: istek.pco2,
    hco3: sonuc.hco3_used,
    be: sonuc.be_used,
  };

  return (
    <>
      <section className={styles.degerler} aria-label="Temel değerler">
        {DEGERLER.map((d) => {
          const aralik = araliklar[d.kod];
          // Durum, ekranda yazılan (yuvarlanmış) değerle hesaplanır; yazılan değer sınırdaysa çelişki olmaz
          const deger = gosterilenDeger(d, degerler[d.kod]);
          // Aralık API'den gelir; bilinmiyorsa değer yine gösterilir, bant ve durum çizilmez
          const durum = aralik ? degerDurumu(deger, aralik, d.ters) : null;
          const yon = durum?.yon ?? null;
          return (
            <div key={d.kod} className={styles.deger}>
              <div className={styles.ad}>{d.ad}</div>
              <div className={styles.sayi}>
                {d.yaz(deger)}
                {d.birim && <span className={styles.birim}>{d.birim}</span>}
              </div>
              {durum && (
                <div className={`${styles.durum} ${yon ? styles[yon] : ""}`}>
                  {durum.simge && <span aria-hidden="true">{durum.simge} </span>}
                  {durum.metin}
                </div>
              )}
              {aralik && (
                <>
                  <div className={styles.cubuk} aria-hidden="true">
                    <span
                      className={styles.bant}
                      style={{
                        left: `${yuzde(aralik.low, d.olcek)}%`,
                        width: `${yuzde(aralik.high, d.olcek) - yuzde(aralik.low, d.olcek)}%`,
                      }}
                    />
                    <span
                      className={`${styles.isaret} ${yon ? styles[yon] : styles.normal}`}
                      style={{ left: `calc(${yuzde(deger, d.olcek)}% - 2px)` }}
                    />
                  </div>
                  <div className={styles.normalMetni}>{normalMetni(aralik)}</div>
                </>
              )}
            </div>
          );
        })}
      </section>
      <div className={styles.aciklama}>
        <span>
          <i className={`${styles.ornek} ${styles.asit}`} />
          Asit yönünde etki
        </span>
        <span>
          <i className={`${styles.ornek} ${styles.baz}`} />
          Baz yönünde etki
        </span>
      </div>
    </>
  );
}
