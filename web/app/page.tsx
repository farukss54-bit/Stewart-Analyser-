import styles from "./page.module.css";

// Boş ekran. "Hazır vaka yükle" ve "Gelişmiş moda geç" düğmeleri, işlevleri eklendiği aşamada gelir
export default function Home() {
  return (
    <main className={styles.main}>
      <section className={styles.empty}>
        <h1 className={styles.lead}>Değerleri girin, sonuç burada görünecek.</h1>
        <p>
          Hızlı mod için pH, pCO₂, Na⁺, Cl⁻, laktat ve albümin yeterli. Sonuçta baskın mekanizma,
          her mekanizmanın etkisi ve notlar yer alır.
        </p>
        <div className={styles.tips}>
          <p>
            Bikarbonat ve baz açığını girmezseniz pH ve pCO₂’den hesaplanır. Cihaz çıktınız varsa
            girerek doğrulayabilirsiniz.
          </p>
          <p>
            Ölçülmemiş anyon (SIG) hesabı için Ca²⁺, Mg²⁺ ve fosfat gerekir. Bunları gelişmiş
            modda girebilirsiniz.
          </p>
        </div>
      </section>
    </main>
  );
}
