import { useId } from "react";
import styles from "./SayiAlani.module.css";

interface Props {
  etiket: string;
  birim?: string;
  deger: string;
  hata?: string | null;
  /** Hatalı alan tam genişlikte gösterilir (hata metni sığsın) */
  tamGenislik?: boolean;
  /** İsteğe bağlı ileri parametre: boşken kesikli çerçeve çizilir */
  ileri?: boolean;
  /** Alanın adı; "Eksik alanlara git" gibi programla odaklama için */
  alanAdi?: string;
  onDegisti: (deger: string) => void;
  onAyrildi?: () => void;
}

export default function SayiAlani({
  etiket,
  birim,
  deger,
  hata,
  tamGenislik,
  ileri,
  alanAdi,
  onDegisti,
  onAyrildi,
}: Props) {
  const id = useId();
  const hataId = `${id}-hata`;
  const sinif = [
    styles.alan,
    hata ? styles.hatali : "",
    tamGenislik || hata ? styles.tam : "",
    ileri && deger.trim() === "" ? styles.eksik : "",
  ].join(" ");

  return (
    <div className={sinif}>
      <label htmlFor={id} className={styles.etiket}>
        {etiket} {birim && <span className={styles.birim}>{birim}</span>}
      </label>
      <input
        id={id}
        data-alan={alanAdi}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        spellCheck={false}
        placeholder="—"
        value={deger}
        aria-invalid={hata ? true : undefined}
        aria-describedby={hata ? hataId : undefined}
        onChange={(e) => onDegisti(e.target.value)}
        onBlur={onAyrildi}
      />
      {hata && (
        <p id={hataId} className={styles.hataMetni} role="alert">
          {hata}
        </p>
      )}
    </div>
  );
}
