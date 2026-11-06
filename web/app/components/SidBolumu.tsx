import { sayiYaz } from "../lib/bicim";
import type { AnalyzeRequest, Meta } from "../lib/api";
import { girilmeyenDegerler, sidMerdiveni, sigEtiketi, sigYorumu, yuzde, type Sonuc } from "../lib/sonuc";
import dugme from "./Button.module.css";
import styles from "./SidBolumu.module.css";

interface Props {
  istek: AnalyzeRequest;
  sonuc: Sonuc;
  araliklar: Meta["reference_ranges"];
  onAlanaGit: (alan: string) => void;
}

/** Gelişmiş mod: güçlü iyon farkının üç katmanı, etkin SID ve aradaki fark (SIG) */
export default function SidBolumu({ istek, sonuc, araliklar, onAlanaGit }: Props) {
  const merdiven = sidMerdiveni(sonuc, araliklar);
  if (merdiven === null) return null;

  const { olcek } = merdiven;
  const konum = (deger: number) => yuzde(deger, olcek);
  const etiket = sigEtiketi(istek);
  const eksikler = girilmeyenDegerler(istek);
  const yorum = sigYorumu(sonuc);
  const isaretler: number[] = [];
  for (let d = olcek.min; d <= olcek.max; d += 5) isaretler.push(d);

  return (
    <section aria-labelledby="sid-baslik">
      <div className={styles.baslikSatiri}>
        <div>
          <h2 id="sid-baslik" className={styles.h2}>
            Güçlü iyon farkı: üç katman ve SIG
          </h2>
          <p className={styles.alt}>
            Her katman bir öncekine ölçülen iyonları ekler. Tam katman (SIDa), albümin, fosfat ve karbondioksitten
            hesaplanan etkin değerle (SIDe) karşılaştırılır; aradaki fark SIG’dir.
          </p>
        </div>
        {/* Hüküm değil veri durumu: SIG'in hangi girdilerle hesaplandığını söyler */}
        <span className={`${styles.durum} ${etiket.tam ? "" : styles.eksik}`}>{etiket.metin}</span>
      </div>

      <div className={styles.olcek} aria-hidden="true">
        <span />
        <div className={styles.isaretler}>
          {isaretler.map((d) => (
            <span key={d}>{d}</span>
          ))}
        </div>
        <span className={styles.birim}>mmol/L</span>
      </div>

      {merdiven.basamaklar.map((b) => (
        <div key={b.kimlik} className={styles.satir}>
          <div>
            <div className={styles.ad}>{b.ad}</div>
            <div className={styles.altAd}>{b.alt}</div>
          </div>
          <div className={styles.yol} aria-hidden="true">
            {b.deger !== null && (
              <span
                className={`${styles.cubuk} ${b.eksik ? styles.kesik : b.kimlik === "effective" || b.kimlik === "full" ? styles.dolu : styles.soluk}`}
                style={{ width: `${konum(b.deger)}%` }}
              />
            )}
            {b.normal !== null && <span className={styles.normal} style={{ left: `${konum(b.normal)}%` }} />}
          </div>
          <div className={styles.deger}>{b.deger === null ? "—" : sayiYaz(b.deger)}</div>
        </div>
      ))}

      <div className={`${styles.satir} ${styles.sig}`}>
        <div>
          <div className={styles.ad}>SIG</div>
          <div className={styles.altAd}>SIDa − SIDe</div>
        </div>
        <div className={styles.yol} aria-hidden="true">
          <span
            className={styles.fark}
            style={{
              left: `${konum(merdiven.sig.baslangic)}%`,
              width: `${konum(merdiven.sig.bitis) - konum(merdiven.sig.baslangic)}%`,
            }}
          />
        </div>
        <div className={styles.deger}>{sayiYaz(merdiven.sig.deger)}</div>
      </div>

      <p className={styles.not}>
        <span className={styles.normalOrnek} aria-hidden="true" />
        Normal değer. SIG normalde sıfıra yakındır.{yorum && ` ${yorum}.`}
      </p>

      {eksikler.length > 0 && (
        <div className={styles.hatirlatma}>
          <p>
            Girilmeyenler: {eksikler.map((e) => e.sembol).join(", ")}. Tam katman ve SIG eksik veriyle hesaplandı;
            girdiğinizde sonuç değişebilir.
          </p>
          <button type="button" className={dugme.ghost} onClick={() => onAlanaGit(eksikler[0].alan)}>
            Eksik alanlara git
          </button>
        </div>
      )}
    </section>
  );
}
