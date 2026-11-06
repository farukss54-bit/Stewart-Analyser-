import ThemeToggle from "./ThemeToggle";
import styles from "./TopBar.module.css";

// Mod seçici ve "Hazır vakalar" düğmeleri, işlevleri eklendiği aşamada gelir
export default function TopBar() {
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
        <ThemeToggle />
      </nav>
    </header>
  );
}
