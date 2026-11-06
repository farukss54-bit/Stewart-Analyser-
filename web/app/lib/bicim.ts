/** Bir ondalık basamakla yazar. Eksi işareti tipografik "−"; işaretli modda artı da yazılır (BE gibi). */
export function sayiYaz(sayi: number, isaretli = false): string {
  const yazi = Math.abs(sayi).toFixed(1);
  // -0.04 gibi değerler "−0.0" olarak görünmesin
  if (Number(yazi) === 0) return yazi;
  if (sayi < 0) return `−${yazi}`;
  return isaretli ? `+${yazi}` : yazi;
}

/** Sunucu mesajları başında uyarı simgesi taşıyabilir (örn. "⚠️ pH ..."); arayüzde metin yeterli. */
export function simgesizMetin(mesaj: string): string {
  return mesaj.replace(/^[^\p{L}\p{N}]+/u, "");
}
