import type { KlasikKarsilastirma as Karsilastirma } from "../lib/sonuc";
import styles from "./KlasikKarsilastirma.module.css";

/**
 * Klasik (HCO₃⁻, BE, anyon açığı) değerlendirmeye göre farklar. Varsayılan olarak kapalıdır:
 * ana sonucu geri plana itmez, isteyen açar.
 */
export default function KlasikKarsilastirma({ karsilastirma }: { karsilastirma: Karsilastirma }) {
  const { farklar, kacirilanlar } = karsilastirma;

  return (
    <section aria-labelledby="klasik-baslik">
      <details className={styles.kutu}>
        <summary className={styles.ozet}>
          <h2 id="klasik-baslik" className={styles.h2}>
            Klasik yaklaşımla karşılaştırma
          </h2>
        </summary>
        <div className={styles.icerik}>
          <ul className={styles.liste}>
            {farklar.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
          {kacirilanlar.length > 0 && (
            <div>
              <p className={styles.altBaslik}>Klasik analizde gözden kaçabilecek durumlar</p>
              <ul className={styles.liste}>
                {kacirilanlar.map((k) => (
                  <li key={k}>{k}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </details>
    </section>
  );
}
