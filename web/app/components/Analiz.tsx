"use client";

import { useRef, useState } from "react";
import { api, type AnalyzeResponse } from "../lib/api";
import {
  albuminCevir,
  analizIstegi,
  BOS_CIHAZ,
  BOS_DEGERLER,
  eksikZorunlular,
  hatalariBul,
  turetilmisIstegi,
  TUM_ALANLAR,
  type AlanAdi,
  type AlbuminBirimi,
  type Cihaz,
  type Degerler,
  type Hatalar,
} from "../lib/form";
import { useTuretilmis } from "../lib/useTuretilmis";
import styles from "./Analiz.module.css";
import BosEkran from "./BosEkran";
import GirisPaneli from "./GirisPaneli";
import { useMeta } from "./MetaProvider";

type AnalizDurumu =
  | { tur: "bos" }
  | { tur: "suruyor" }
  | { tur: "hazir" }
  | { tur: "gecersiz"; hatalar: string[] }
  | { tur: "ag" }
  | { tur: "sunucu" }
  | { tur: "reddedildi" };

type AlanAnahtari = keyof Hatalar;

// "4 alandan 1’i" gibi sayı ekleri (0–4)
const SAYI_EKI = ["ı", "i", "si", "ü", "ü"];

const ZORUNLU_SAYISI = TUM_ALANLAR.filter((a) => a.zorunlu).length;

export default function Analiz() {
  const meta = useMeta();
  const sinirlar = meta.tur === "hazir" ? meta.meta.limits : undefined;

  const [degerler, setDegerler] = useState<Degerler>(BOS_DEGERLER);
  const [albuminBirimi, setAlbuminBirimi] = useState<AlbuminBirimi>("g/L");
  const [cihaz, setCihaz] = useState<Cihaz>(BOS_CIHAZ);
  const [dokunulan, setDokunulan] = useState<Partial<Record<AlanAnahtari, true>>>({});
  const [analiz, setAnaliz] = useState<AnalizDurumu>({ tur: "bos" });
  const sonIstek = useRef<AbortController | null>(null);

  const tumHatalar = hatalariBul(degerler, albuminBirimi, cihaz, sinirlar);
  // Yazarken uyarı çıkmasın: bir alanın hatası, alandan ayrıldıktan sonra gösterilir
  const gorunenHatalar = Object.fromEntries(
    Object.entries(tumHatalar).filter(([ad]) => dokunulan[ad as AlanAnahtari]),
  ) as Hatalar;

  const turetilmisIstek = turetilmisIstegi(degerler, cihaz, sinirlar);
  const turetilmis = useTuretilmis(turetilmisIstek);
  const turetilmisVeri = turetilmis?.tur === "tamam" ? turetilmis.veri : null;

  const cihazBeVar = turetilmisIstek?.be_device !== undefined;
  const isaretHatasi = turetilmisVeri?.sign_check?.has_error === true;
  const cihazBekliyor = cihazBeVar && turetilmis === null;
  const cihazDenetlenemedi = cihazBeVar && turetilmis !== null && turetilmis.tur !== "tamam";

  const eksik = eksikZorunlular(degerler);
  const hataVar = Object.keys(tumHatalar).length > 0;
  const analizEtkin =
    meta.tur === "hazir" &&
    eksik.length === 0 &&
    !hataVar &&
    !isaretHatasi &&
    !cihazBekliyor &&
    !cihazDenetlenemedi &&
    analiz.tur !== "suruyor";

  function degerDegisti(ad: AlanAdi, deger: string) {
    setDegerler((onceki) => ({ ...onceki, [ad]: deger }));
  }

  function alanAyrildi(ad: AlanAnahtari) {
    setDokunulan((onceki) => ({ ...onceki, [ad]: true }));
  }

  function birimDegisti(yeni: AlbuminBirimi) {
    if (yeni === albuminBirimi) return;
    // Girilen değer yeni birime çevrilir; yoksa 25 g/L, g/dL olarak 25 sayılırdı
    setDegerler((onceki) => ({ ...onceki, albumin: albuminCevir(onceki.albumin, albuminBirimi, yeni) }));
    setAlbuminBirimi(yeni);
  }

  async function gonder() {
    const istek = analizIstegi(degerler, albuminBirimi, cihaz, sinirlar);
    if (istek === null) return;

    sonIstek.current?.abort();
    const iptal = new AbortController();
    sonIstek.current = iptal;
    setAnaliz({ tur: "suruyor" });

    try {
      const sonuc = await api.analiz(istek, iptal.signal);
      if (sonuc.tur === "tamam") setAnaliz(analizDurumu(sonuc.veri));
      else setAnaliz({ tur: sonuc.tur });
    } catch {
      // Yeni bir analiz başlatıldı; onun sonucu gösterilecek
    }
  }

  function yardimMetni(): string {
    if (meta.tur === "hata") return "API’ye ulaşılamadı. Sunucunun çalıştığından emin olun.";
    if (meta.tur === "yukleniyor") return "Sunucuya bağlanılıyor…";
    if (hataVar) return "Hata gösteren alanları düzeltin.";
    if (isaretHatasi) return "BE işaret hatası düzeltilmeden analiz yapılamaz.";
    if (cihazDenetlenemedi) return "Cihaz değerleri denetlenemedi. API’ye ulaşılamıyor.";
    if (cihazBekliyor) return "Cihaz değerleri denetleniyor…";
    if (eksik.length > 0) {
      const dolu = ZORUNLU_SAYISI - eksik.length;
      return `Zorunlu ${ZORUNLU_SAYISI} alandan ${dolu}’${SAYI_EKI[dolu]} dolu. Eksik: ${eksik.map((a) => a.etiket).join(", ")}.`;
    }
    const girilmeyen = [];
    if (degerler.lactate.trim() === "") girilmeyen.push("laktat");
    if (degerler.albumin.trim() === "") girilmeyen.push("albümin");
    if (girilmeyen.length > 0) {
      const metin = girilmeyen.join(" ve ");
      const buyuk = metin.charAt(0).toLocaleUpperCase("tr") + metin.slice(1);
      return `${buyuk} girilmedi; ${girilmeyen.length > 1 ? "etkileri" : "etkisi"} değerlendirilemeyecek.`;
    }
    return "Fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir.";
  }

  return (
    <div className={styles.govde}>
      <GirisPaneli
        degerler={degerler}
        albuminBirimi={albuminBirimi}
        cihaz={cihaz}
        hatalar={gorunenHatalar}
        hesaplanabilir={turetilmisIstek !== null}
        turetilmis={turetilmis}
        analizEtkin={analizEtkin}
        analizYapildi={analiz.tur === "hazir"}
        analizSuruyor={analiz.tur === "suruyor"}
        yardimMetni={yardimMetni()}
        onDeger={degerDegisti}
        onAlanAyrildi={alanAyrildi}
        onBirim={birimDegisti}
        onCihaz={setCihaz}
        onGonder={gonder}
      />
      <main className={styles.ana}>
        <AnaAlan durum={analiz} />
      </main>
    </div>
  );
}

function analizDurumu(yanit: AnalyzeResponse): AnalizDurumu {
  return yanit.is_valid ? { tur: "hazir" } : { tur: "gecersiz", hatalar: yanit.errors };
}

// Sonuç ekranı Aşama 4'te eklenecek; şimdilik yalnızca durum bildirilir
function AnaAlan({ durum }: { durum: AnalizDurumu }) {
  switch (durum.tur) {
    case "bos":
      return <BosEkran />;
    case "suruyor":
      return <p role="status">Analiz ediliyor…</p>;
    case "hazir":
      return (
        <div className={styles.durum} role="status">
          <h1 className={styles.baslik}>Analiz tamamlandı.</h1>
          <p>Sonuç ekranı bir sonraki aşamada eklenecek.</p>
        </div>
      );
    case "gecersiz":
      return (
        <div className={styles.durum} role="alert">
          <h1 className={styles.baslik}>Değerler analiz edilemedi.</h1>
          <ul className={styles.hata}>
            {durum.hatalar.map((h) => (
              <li key={h}>{h}</li>
            ))}
          </ul>
        </div>
      );
    case "ag":
      return (
        <p className={styles.hata} role="alert">
          API’ye ulaşılamadı. Sunucunun çalıştığından emin olun ve yeniden deneyin.
        </p>
      );
    case "sunucu":
      return (
        <p className={styles.hata} role="alert">
          API beklenmeyen bir hata verdi. Yeniden deneyin.
        </p>
      );
    case "reddedildi":
      return (
        <p className={styles.hata} role="alert">
          API girilen değerleri kabul etmedi. Alanları kontrol edip yeniden deneyin.
        </p>
      );
  }
}
