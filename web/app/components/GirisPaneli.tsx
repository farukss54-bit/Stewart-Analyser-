import type { FormEvent } from "react";
import type { ApiSonuc, DerivedResponse } from "../lib/api";
import {
  gruplar,
  type AlanAdi,
  type AlbuminBirimi,
  type Cihaz,
  type Degerler,
  type Hatalar,
  type Mod,
} from "../lib/form";
import dugme from "./Button.module.css";
import styles from "./GirisPaneli.module.css";
import SayiAlani from "./SayiAlani";
import TuretilmisDegerler from "./TuretilmisDegerler";

interface Props {
  mod: Mod;
  degerler: Degerler;
  albuminBirimi: AlbuminBirimi;
  cihaz: Cihaz;
  /** Yalnızca kullanıcının dokunduğu alanların hataları (yazarken uyarı çıkmasın) */
  hatalar: Hatalar;
  hesaplanabilir: boolean;
  turetilmis: ApiSonuc<DerivedResponse> | null;
  analizEtkin: boolean;
  analizYapildi: boolean;
  analizSuruyor: boolean;
  yardimMetni: string;
  onDeger: (ad: AlanAdi, deger: string) => void;
  onAlanAyrildi: (ad: AlanAdi | "cihazHco3" | "cihazBe") => void;
  onBirim: (birim: AlbuminBirimi) => void;
  onCihaz: (cihaz: Cihaz) => void;
  onGonder: () => void;
}

const BIRIMLER: AlbuminBirimi[] = ["g/L", "g/dL"];

export default function GirisPaneli(p: Props) {
  function gonder(e: FormEvent) {
    e.preventDefault();
    if (p.analizEtkin) p.onGonder();
  }

  return (
    <form className={`${styles.panel} ${p.analizYapildi ? styles.sonucVar : ""}`} aria-label="Girilen değerler" noValidate onSubmit={gonder}>
      {gruplar(p.mod).map((grup) => {
        const albuminGrubu = grup.alanlar.some((a) => a.ad === "albumin");
        return (
          <section key={grup.baslik} className={styles.grup}>
            <div className={styles.grupBasligi}>
              <h2 className={styles.baslik}>{grup.baslik}</h2>
              {albuminGrubu && (
                <div className={styles.birimSecici} role="group" aria-label="Albümin birimi">
                  {BIRIMLER.map((birim) => (
                    <button
                      key={birim}
                      type="button"
                      className={birim === p.albuminBirimi ? styles.secili : ""}
                      aria-pressed={birim === p.albuminBirimi}
                      onClick={() => p.onBirim(birim)}
                    >
                      {birim}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {grup.not && <p className={styles.grupNotu}>{grup.not}</p>}
            <div className={styles.alanlar}>
              {grup.alanlar.map((alan) => (
                <SayiAlani
                  key={alan.ad}
                  alanAdi={alan.ad}
                  ileri={alan.ileri}
                  etiket={alan.etiket}
                  birim={alan.ad === "albumin" ? p.albuminBirimi : alan.birim}
                  deger={p.degerler[alan.ad]}
                  hata={p.hatalar[alan.ad]}
                  tamGenislik={alan.tam}
                  onDegisti={(d) => p.onDeger(alan.ad, d)}
                  onAyrildi={() => p.onAlanAyrildi(alan.ad)}
                />
              ))}
            </div>
          </section>
        );
      })}

      <TuretilmisDegerler
        hesaplanabilir={p.hesaplanabilir}
        sonuc={p.turetilmis}
        cihaz={p.cihaz}
        hatalar={p.hatalar}
        onCihazDegisti={p.onCihaz}
        onAlanAyrildi={p.onAlanAyrildi}
      />

      <div className={styles.eylem}>
        {/* disabled yerine aria-disabled: düğme odaklanabilir kalır, yardım metni klavye ve ekran okuyucuyla duyulur.
            Etkin değilken gönderme gonder() içinde engellenir. */}
        <button
          type="submit"
          className={dugme.birincil}
          aria-disabled={!p.analizEtkin}
          aria-describedby="analiz-yardim"
        >
          {p.analizSuruyor ? "Analiz ediliyor…" : p.analizYapildi ? "Yeniden analiz et" : "Analiz et"}
        </button>
        <p id="analiz-yardim" className={styles.yardim}>
          {p.yardimMetni}
        </p>
      </div>
    </form>
  );
}
