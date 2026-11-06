"use client";

import dugme from "./Button.module.css";
import ThemeToggle from "./ThemeToggle";
import styles from "./TopBar.module.css";

// Mod seçici (Hızlı / Gelişmiş / Toplu analiz), işlevleri eklendiği aşamada gelir
export default function TopBar({ onVakalar }: { onVakalar: () => void }) {
  return (
    <header className={styles.top}>
      <div className={styles.brand}>
        <span className={styles.mark} aria-hidden="true">
          <i />
          <i />
        </span>
        <span>Stewart asit-baz analizi</span>
      </div>
      <nav className={styles.nav} aria-label="Görünüm">
        <button type="button" className={dugme.ghost} onClick={onVakalar}>
          Hazır vakalar
        </button>
        <ThemeToggle />
      </nav>
    </header>
  );
}
