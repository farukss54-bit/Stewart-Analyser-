import styles from "./Footer.module.css";
import Referanslar from "./Referanslar";
import SurumEtiketi from "./SurumEtiketi";

export default function Footer() {
  return (
    <footer className={styles.foot}>
      <Referanslar />
      <p>
        Bu araç fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir. Eğitim
        amaçlıdır, klinik kararlar uzman hekim değerlendirmesi gerektirir.
      </p>
      <SurumEtiketi />
    </footer>
  );
}
