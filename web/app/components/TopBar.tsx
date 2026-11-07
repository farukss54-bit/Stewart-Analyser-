"use client";

import type { Gorunum, Mod } from "../lib/form";
import dugme from "./Button.module.css";
import ThemeToggle from "./ThemeToggle";
import styles from "./TopBar.module.css";

const MODLAR: { mod: Mod; ad: string }[] = [
  { mod: "hizli", ad: "Hızlı" },
  { mod: "gelismis", ad: "Gelişmiş" },
];

export default function TopBar({
  mod,
  onMod,
  gorunum,
  onGorunum,
  onVakalar,
}: {
  mod: Mod;
  onMod: (mod: Mod) => void;
  gorunum: Gorunum;
  onGorunum: (gorunum: Gorunum) => void;
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
        <button
          type="button"
          className={`${dugme.ghost} ${styles.gorunum}`}
          aria-pressed={gorunum === "toplu"}
          onClick={() => onGorunum(gorunum === "toplu" ? "tekli" : "toplu")}
        >
          Toplu CSV
        </button>
        <button type="button" className={dugme.ghost} onClick={onVakalar}>
          Hazır vakalar
        </button>
        <ThemeToggle />
      </nav>
    </header>
  );
}
