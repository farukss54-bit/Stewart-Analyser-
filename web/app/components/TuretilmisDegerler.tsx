import { useId } from "react";
import { simgesizMetin, sayiYaz } from "../lib/bicim";
import type { ApiSonuc, DerivedResponse } from "../lib/api";
import { ayristir, type Cihaz, type Hatalar } from "../lib/form";
import dugme from "./Button.module.css";
import SayiAlani from "./SayiAlani";
import styles from "./TuretilmisDegerler.module.css";

interface Props {
  /** pH ve pCO₂ geçerli mi (hesaplama için istek atılabiliyor mu) */
  hesaplanabilir: boolean;
  /** null: istek yok ya da yanıt bekleniyor */
  sonuc: ApiSonuc<DerivedResponse> | null;
  cihaz: Cihaz;
  hatalar: Hatalar;
  onCihazDegisti: (yeni: Cihaz) => void;
  onAlanAyrildi: (ad: "cihazHco3" | "cihazBe") => void;
}

const FARK_UYARISI = "Bu fark önemli: örnek kalitesi, cihaz kalibrasyonu veya giriş hatası olabilir.";

function notMetni(hesaplanabilir: boolean, sonuc: Props["sonuc"]): string {
  if (!hesaplanabilir) return "pH ve pCO₂ girilince hesaplanır.";
  if (sonuc === null) return "Hesaplanıyor…";
  if (sonuc.tur !== "tamam") return "Hesaplanamadı. API’ye ulaşılamıyor ya da yanıt vermiyor.";
  return "pH ve pCO₂ üzerinden hesaplandı. Cihaz çıktınız varsa girerek doğrulayın.";
}

export default function TuretilmisDegerler({
  hesaplanabilir,
  sonuc,
  cihaz,
  hatalar,
  onCihazDegisti,
  onAlanAyrildi,
}: Props) {
  const baslikId = useId();
  const veri = sonuc?.tur === "tamam" ? sonuc.veri : null;
  const hco3 = veri ? sayiYaz(veri.hco3_calculated) : "—";
  const be = veri ? sayiYaz(veri.be_calculated, true) : "—";

  return (
    <section className={styles.kutu} aria-labelledby={baslikId}>
      <h2 id={baslikId} className={styles.baslik}>
        Hesaplanan değerler
      </h2>
      <div className={styles.degerler}>
        <span>
          HCO₃⁻<b>{hco3}</b>
        </span>
        <span>
          BE<b>{be}</b>
        </span>
      </div>
      <p className={styles.not}>{notMetni(hesaplanabilir, sonuc)}</p>

      <button
        type="button"
        className={dugme.ghost}
        aria-expanded={cihaz.acik}
        onClick={() => onCihazDegisti({ ...cihaz, acik: !cihaz.acik })}
      >
        {cihaz.acik ? "Cihaz değerlerini kaldır" : "Cihaz değerlerini gir"}
      </button>

      {cihaz.acik && (
        <div className={styles.cihaz}>
          <p className={styles.not}>
            Cihazın gösterdiği değeri girerseniz hesaplananla tutarlılığı denetlenir (fark 2 mEq/L’yi aşarsa uyarı
            görürsünüz). Girdiğiniz değer analizde kullanılır.
          </p>
          <div className={styles.alanlar}>
            <SayiAlani
              etiket="HCO₃⁻"
              birim="mEq/L"
              deger={cihaz.hco3}
              hata={hatalar.cihazHco3}
              onDegisti={(d) => onCihazDegisti({ ...cihaz, hco3: d })}
              onAyrildi={() => onAlanAyrildi("cihazHco3")}
            />
            <SayiAlani
              etiket="BE"
              birim="mEq/L"
              deger={cihaz.be}
              hata={hatalar.cihazBe}
              onDegisti={(d) => onCihazDegisti({ ...cihaz, be: d })}
              onAyrildi={() => onAlanAyrildi("cihazBe")}
            />
          </div>
          <label className={styles.onay}>
            <input
              type="checkbox"
              checked={cihaz.bd}
              onChange={(e) => onCihazDegisti({ ...cihaz, bd: e.target.checked })}
            />
            <span>BE’yi baz açığı (BD) olarak girdim</span>
          </label>
          <Sonuclar veri={veri} cihaz={cihaz} />
        </div>
      )}
    </section>
  );
}

function Sonuclar({ veri, cihaz }: { veri: DerivedResponse | null; cihaz: Cihaz }) {
  if (veri === null) return null;
  const girilenBe = ayristir(cihaz.be);

  return (
    <div className={styles.sonuclar} aria-live="polite">
      {veri.hco3_check &&
        (veri.hco3_check.consistent ? (
          <p>HCO₃⁻ tutarlı (fark {sayiYaz(veri.hco3_check.diff)} mEq/L).</p>
        ) : (
          <p className={styles.uyari}>
            HCO₃⁻ farkı {sayiYaz(veri.hco3_check.diff)} mEq/L (hesaplanan {sayiYaz(veri.hco3_calculated)}).{" "}
            {FARK_UYARISI}
          </p>
        ))}

      {veri.sign_check?.has_error ? (
        <div className={styles.uyari} role="alert">
          <p>{simgesizMetin(veri.sign_check.message)}</p>
          {girilenBe.tur === "sayi" && (
            <p>
              Düzeltmek için değeri <b>{sayiYaz(-girilenBe.deger)}</b> olarak değiştirin
              {girilenBe.deger > 0 && !cihaz.bd ? " ya da BD kutusunu işaretleyin" : ""}.
            </p>
          )}
        </div>
      ) : (
        veri.be_check &&
        (veri.be_check.consistent ? (
          <p>BE tutarlı (fark {sayiYaz(veri.be_check.diff)} mEq/L).</p>
        ) : (
          <p className={styles.uyari}>
            BE farkı {sayiYaz(veri.be_check.diff)} mEq/L (hesaplanan {sayiYaz(veri.be_calculated, true)}).{" "}
            {FARK_UYARISI}
          </p>
        ))
      )}
    </div>
  );
}
