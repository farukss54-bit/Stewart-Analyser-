import type { AnalyzeRequest } from "../lib/api";
import { girdiOzeti } from "../lib/girdiOzeti";
import dugme from "./Button.module.css";
import styles from "./GirdiOzeti.module.css";

/** Dar ekranda sonuç açıkken form gizlenir; yerine girilen değerlerin özeti ve düzenleme düğmesi görünür */
export default function GirdiOzeti({ istek, onDuzenle }: { istek: AnalyzeRequest; onDuzenle: () => void }) {
  return (
    <section className={styles.ozet} aria-label="Girilen değerler">
      <p>{girdiOzeti(istek)}</p>
      <button type="button" className={dugme.ghost} onClick={onDuzenle}>
        Değerleri düzenle
      </button>
    </section>
  );
}
