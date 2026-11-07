/** Bellekteki bir dosyayı kullanıcının bilgisayarına indirir (sunucuya yeniden gitmez) */
export function dosyaIndir(dosya: Blob, ad: string): void {
  const adres = URL.createObjectURL(dosya);
  const baglanti = document.createElement("a");
  baglanti.href = adres;
  baglanti.download = ad;
  document.body.append(baglanti);
  baglanti.click();
  baglanti.remove();
  // İndirme başlayana kadar adres geçerli kalmalı
  setTimeout(() => URL.revokeObjectURL(adres), 1000);
}
