"use client";

import { useSyncExternalStore } from "react";
import { TEMA_ANAHTARI } from "./tema";
import dugme from "./Button.module.css";
import styles from "./ThemeToggle.module.css";

type Tema = "light" | "dark";

const KOYU_SORGU = "(prefers-color-scheme: dark)";
const dinleyiciler = new Set<() => void>();

function abone(bildir: () => void) {
  dinleyiciler.add(bildir);
  const cihaz = window.matchMedia(KOYU_SORGU);
  cihaz.addEventListener("change", bildir);
  return () => {
    dinleyiciler.delete(bildir);
    cihaz.removeEventListener("change", bildir);
  };
}

// Kullanıcı seçtiyse data-theme, seçmediyse cihaz ayarı geçerlidir
function gecerliTema(): Tema {
  const secili = document.documentElement.dataset.theme;
  if (secili === "light" || secili === "dark") return secili;
  return window.matchMedia(KOYU_SORGU).matches ? "dark" : "light";
}

// Sunucuda cihaz ayarı bilinmez; null, "henüz bilinmiyor" demektir
const sunucuTemasi = (): Tema | null => null;

export default function ThemeToggle() {
  const tema = useSyncExternalStore<Tema | null>(abone, gecerliTema, sunucuTemasi);

  function degistir() {
    const sonraki: Tema = gecerliTema() === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = sonraki;
    try {
      localStorage.setItem(TEMA_ANAHTARI, sonraki);
    } catch {
      // Depolama kapalıysa tercih yalnızca bu sayfa açıkken geçerli kalır
    }
    dinleyiciler.forEach((bildir) => bildir());
  }

  const etiket =
    tema === "dark" ? "Açık temaya geç" : tema === "light" ? "Koyu temaya geç" : "Tema";

  return (
    <button type="button" className={`${dugme.ghost} ${styles.sabit}`} onClick={degistir}>
      {etiket}
    </button>
  );
}
