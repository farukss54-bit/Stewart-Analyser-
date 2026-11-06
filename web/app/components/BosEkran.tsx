import styles from "./Analiz.module.css";
import dugme from "./Button.module.css";

// "Gelişmiş moda geç" düğmesi, işlevi eklendiği aşamada gelir
export default function BosEkran({ onVakalar }: { onVakalar: () => void }) {
  return (
    <section className={styles.bos}>
      <h1 className={styles.baslik}>Değerleri girin, sonuç burada görünecek.</h1>
      <p>
        Hızlı mod için pH, pCO₂, Na⁺ ve Cl⁻ yeterli. Laktat ve albümini de girerseniz etkileri değerlendirilir.
        Sonuçta baskın mekanizma, her mekanizmanın etkisi ve notlar yer alır.
      </p>
      <div>
        <button type="button" className={dugme.dolgun} onClick={onVakalar}>
          Hazır vaka yükle
        </button>
      </div>
      <div className={styles.ipuclari}>
        <p>
          Bikarbonat ve baz açığını girmezseniz pH ve pCO₂’den hesaplanır. Cihaz çıktınız varsa girerek
          doğrulayabilirsiniz.
        </p>
        <p>
          Ölçülmemiş anyon (SIG) hesabı için Ca²⁺, Mg²⁺ ve fosfat gerekir. Bunları gelişmiş modda girebilirsiniz.
        </p>
      </div>
    </section>
  );
}
