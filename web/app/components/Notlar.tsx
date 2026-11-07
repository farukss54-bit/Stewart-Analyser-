import type { NotGrubu } from "../lib/sonuc";
import styles from "./Notlar.module.css";

export default function Notlar({ gruplar }: { gruplar: NotGrubu[] }) {
  return (
    <section aria-labelledby="notlar-baslik">
      <h2 id="notlar-baslik" className={styles.h2}>
        Notlar
      </h2>
      <div className={styles.notlar}>
        {gruplar.map((g) => (
          <div key={g.etiket} className={styles.not}>
            <span className={styles.etiket}>{g.etiket}</span>
            <div className={styles.maddeler}>
              {g.maddeler.map((m, i) => (
                // Aynı metinli iki not olabilir; anahtar sırayı da içerir
                <p key={`${i}-${m.metin}`}>
                  {m.metin}
                  {m.mekanizmalar.length > 0 && (
                    <>
                      {" "}
                      <span className={styles.mekanizmalar}>Olası mekanizmalar: {m.mekanizmalar.join(", ")}.</span>
                    </>
                  )}
                </p>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
