import styles from "./Footer.module.css";
import SurumEtiketi from "./SurumEtiketi";

export default function Footer() {
  return (
    <footer className={styles.foot}>
      <p>
        Bu araç fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir. Eğitim
        amaçlıdır, klinik kararlar uzman hekim değerlendirmesi gerektirir.
      </p>
      <SurumEtiketi />
    </footer>
  );
}
