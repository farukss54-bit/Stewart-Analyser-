import type { TopluSatir } from "./api";
import type { Mod } from "./form";

// Streamlit'teki "Örnek CSV İndir" ile aynı içerik ve dosya adı
export const ORNEK_CSV = [
  "ph,pco2,na,cl,k,lactate,albumin_gl,be",
  "7.40,40,140,102,4.0,1.0,40,0",
  "7.30,30,138,108,4.5,3.0,35,-6",
  "7.25,25,136,100,5.0,8.0,28,-12",
].join("\n");
export const ORNEK_DOSYA_ADI = "sample_stewart.csv";

/** API'nin analiz modu adı */
export function apiModu(mod: Mod): "quick" | "advanced" {
  return mod === "hizli" ? "quick" : "advanced";
}

/** Streamlit'teki sonuç dosyası adı: stewart_results_20261107_1415.csv (yerel saat) */
export function sonucDosyaAdi(an: Date): string {
  const iki = (n: number) => String(n).padStart(2, "0");
  const gun = `${an.getFullYear()}${iki(an.getMonth() + 1)}${iki(an.getDate())}`;
  return `stewart_results_${gun}_${iki(an.getHours())}${iki(an.getMinutes())}.csv`;
}

// Çekirdeğin veri kalitesi işaretleri; yalnızca hekimin dikkat etmesi gerekenler gösterilir
const ISARET_METNI: Record<string, string> = {
  BE_MISMATCH: "Girilen BE, pH ve pCO₂’den hesaplanandan 2 mEq/L’den fazla farklı.",
  HCO3_MISMATCH: "Girilen HCO₃⁻, pH ve pCO₂’den hesaplanandan 2 mEq/L’den fazla farklı.",
  SIG_UNDERESTIMATED: "Laktat girilmediği için SIG düşük hesaplanmış olabilir.",
  SIG_UNRELIABLE: "Albümin girilmediği için SIG güvenilir değil.",
};

/** Satırın dikkat notları: doğrulama uyarıları ve bilinen veri kalitesi işaretleri */
export function satirNotlari(satir: TopluSatir): string[] {
  const isaretler = satir.flags.flatMap((f) => (f in ISARET_METNI ? [ISARET_METNI[f]] : []));
  return [...satir.warnings, ...isaretler];
}

/** "3 satır analiz edildi." / "3 satırdan 2’si analiz edildi, 1’i hatalı." */
export function ozetCumlesi(toplam: number, tamam: number, hatali: number): string {
  if (hatali === 0) return `${toplam} satır analiz edildi.`;
  if (tamam === 0) return `${toplam} satırın hiçbiri analiz edilemedi.`;
  return `${toplam} satırdan ${tamam} satır analiz edildi, ${hatali} satır hatalı.`;
}
