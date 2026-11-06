"use client";

import type { Mod } from "../lib/form";
import dugme from "./Button.module.css";
import ThemeToggle from "./ThemeToggle";
import styles from "./TopBar.module.css";

const MODLAR: { mod: Mod; ad: string }[] = [
  { mod: "hizli", ad: "Hızlı" },
  { mod: "gelismis", ad: "Gelişmiş" },
];

// "Toplu analiz (CSV)" seçeneği, ekranı eklendiği aşamada gelir
export default function TopBar({
  mod,
  onMod,
  onVakalar,
}: {
  mod: Mod;
  onMod: (mod: Mod) => void;
  onVakalar: () => void;
}) {
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
        <div className={styles.mod} role="group" aria-label="Analiz modu">
          {MODLAR.map((m) => (
            <button
              key={m.mod}
              type="button"
              className={m.mod === mod ? styles.secili : ""}
              aria-pressed={m.mod === mod}
              onClick={() => onMod(m.mod)}
            >
              {m.ad}
            </button>
          ))}
        </div>
        <button type="button" className={dugme.ghost} onClick={onVakalar}>
          Hazır vakalar
        </button>
        <ThemeToggle />
      </nav>
    </header>
  );
}
