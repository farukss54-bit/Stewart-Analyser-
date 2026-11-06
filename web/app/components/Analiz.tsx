"use client";

import { useRef, useState } from "react";
import { api, type AnalyzeRequest, type AnalyzeResponse, type Meta, type Vaka } from "../lib/api";
import {
  albuminCevir,
  analizIstegi,
  BOS_CIHAZ,
  BOS_DEGERLER,
  eksikZorunlular,
  hatalariBul,
  turetilmisIstegi,
  TUM_ALANLAR,
  vakaDegerleri,
  type AlanAdi,
  type AlbuminBirimi,
  type Cihaz,
  type Degerler,
  type Hatalar,
} from "../lib/form";
import type { Sonuc } from "../lib/sonuc";
import { useTuretilmis } from "../lib/useTuretilmis";
import styles from "./Analiz.module.css";
import BosEkran from "./BosEkran";
import GirisPaneli from "./GirisPaneli";
import { useMeta } from "./MetaProvider";
import SonucEkrani from "./SonucEkrani";
import TopBar from "./TopBar";
import VakaPaneli from "./VakaPaneli";

type AnalizDurumu =
  | { tur: "bos" }
  | { tur: "suruyor" }
  | { tur: "hazir"; istek: AnalyzeRequest; sonuc: Sonuc }
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
  const [vakaPaneliAcik, setVakaPaneliAcik] = useState(false);
  const sonIstek = useRef<AbortController | null>(null);

  const tumHatalar = hatalariBul(degerler, albuminBirimi, cihaz, sinirlar);
  // Yazarken uyarı çıkmasın: bir alanın hatası, alandan ayrıldıktan sonra gösterilir
  const gorunenHatalar = Object.fromEntries(
    Object.entries(tumHatalar).filter(([ad]) => dokunulan[ad as AlanAnahtari]),
  ) as Hatalar;

  const turetilmisIstek = turetilmisIstegi(degerler, cihaz, sinirlar);
  const turetilmis = useTuretilmis(turetilmisIstek);

  const cihazBeVar = turetilmisIstek?.be_device !== undefined;
  const cihazBekliyor = cihazBeVar && turetilmis === null;
  const cihazDenetlenemedi = cihazBeVar && turetilmis !== null && turetilmis.tur !== "tamam";

  const eksik = eksikZorunlular(degerler);
  const hataVar = Object.keys(tumHatalar).length > 0;
  const analizEtkin =
    meta.tur === "hazir" &&
    eksik.length === 0 &&
    !hataVar &&
    !cihazBekliyor &&
    !cihazDenetlenemedi &&
    analiz.tur !== "suruyor";

  // Girdiler değişince sonuç gizlenir: ekranda yalnızca şu anki değerlerin sonucu görünür.
  // Süren bir analiz de iptal edilir.
  function sonucuGizle() {
    sonIstek.current?.abort();
    setAnaliz((onceki) => (onceki.tur === "bos" ? onceki : { tur: "bos" }));
  }

  function degerDegisti(ad: AlanAdi, deger: string) {
    sonucuGizle();
    setDegerler((onceki) => ({ ...onceki, [ad]: deger }));
  }

  function cihazDegisti(yeni: Cihaz) {
    sonucuGizle();
    setCihaz(yeni);
  }

  // Hazır vakanın değerleri forma yüklenir; önceki sonuç gizlenir (değerler değişti)
  function vakaYukle(vaka: Vaka) {
    sonucuGizle();
    const yuklenen = vakaDegerleri(vaka.values);
    setDegerler(yuklenen.degerler);
    setAlbuminBirimi("g/L");
    setCihaz(yuklenen.cihaz);
    setDokunulan({});
    setVakaPaneliAcik(false);
  }

  function alanAyrildi(ad: AlanAnahtari) {
    setDokunulan((onceki) => ({ ...onceki, [ad]: true }));
  }

  function birimDegisti(yeni: AlbuminBirimi) {
    if (yeni === albuminBirimi) return;
    sonucuGizle();
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
      if (sonuc.tur === "tamam") setAnaliz(analizDurumu(istek, sonuc.veri));
      else setAnaliz({ tur: sonuc.tur });
    } catch {
      // Yeni bir analiz başlatıldı; onun sonucu gösterilecek
    }
  }

  function yardimMetni(): string {
    if (meta.tur === "hata") return "API’ye ulaşılamadı. Sunucunun çalıştığından emin olun.";
    if (meta.tur === "yukleniyor") return "Sunucuya bağlanılıyor…";
    if (hataVar) return "Hata gösteren alanları düzeltin.";
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
    <>
      <TopBar onVakalar={() => setVakaPaneliAcik(true)} />
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
          onCihaz={cihazDegisti}
          onGonder={gonder}
        />
        <main className={styles.ana}>
          <AnaAlan
            durum={analiz}
            meta={meta.tur === "hazir" ? meta.meta : undefined}
            onVakalar={() => setVakaPaneliAcik(true)}
          />
        </main>
      </div>
      <VakaPaneli acik={vakaPaneliAcik} onKapat={() => setVakaPaneliAcik(false)} onYukle={vakaYukle} />
    </>
  );
}

function analizDurumu(istek: AnalyzeRequest, yanit: AnalyzeResponse): AnalizDurumu {
  if (!yanit.is_valid) return { tur: "gecersiz", hatalar: yanit.errors };
  // Geçerli bir analizde sonuç her zaman vardır; yoksa API beklenmedik bir yanıt vermiştir
  if (!yanit.result) return { tur: "sunucu" };
  return { tur: "hazir", istek, sonuc: yanit.result };
}

// Ana alan: duruma göre boş ekran, süren analiz, sonuç ya da hata mesajı
function AnaAlan({
  durum,
  meta,
  onVakalar,
}: {
  durum: AnalizDurumu;
  meta: Meta | undefined;
  onVakalar: () => void;
}) {
  switch (durum.tur) {
    case "bos":
      return <BosEkran onVakalar={onVakalar} />;
    case "suruyor":
      return <p role="status">Analiz ediliyor…</p>;
    case "hazir":
      // Sonuç yalnızca analizin yapıldığı girdilerle gösterilir; meta yoksa (olmaz) gösterilmez
      return meta ? <SonucEkrani istek={durum.istek} sonuc={durum.sonuc} meta={meta} /> : null;
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
