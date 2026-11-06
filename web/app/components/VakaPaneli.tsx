"use client";

import { useEffect, useRef, useState } from "react";
import { sayiYaz } from "../lib/bicim";
import { api, type Vaka } from "../lib/api";
import dugme from "./Button.module.css";
import styles from "./VakaPaneli.module.css";

interface Props {
  acik: boolean;
  onKapat: () => void;
  onYukle: (vaka: Vaka) => void;
}

type Durum = { tur: "yukleniyor" } | { tur: "hazir"; vakalar: Vaka[] } | { tur: "hata" };

// BE çubuğunun ölçeği (yalnızca çizim): ±20 mEq/L
const BE_OLCEK = 20;

function sayi(vaka: Vaka, anahtar: string): number | undefined {
  const v = vaka.values[anahtar];
  return typeof v === "number" ? v : undefined;
}

/** Ayrıntı tablosu: vakada bulunan değerler, tasarımdaki sırayla */
function ayrintiSatirlari(vaka: Vaka): { ad: string; deger: string }[] {
  const alanlar: [string, string, (v: number) => string][] = [
    ["ph", "pH", (v) => v.toFixed(2)],
    ["pco2", "pCO₂", (v) => `${v} mmHg`],
    ["na", "Na⁺", String],
    ["cl", "Cl⁻", String],
    ["k", "K⁺", String],
    ["lactate", "Laktat", String],
    ["albumin_gl", "Albümin", (v) => `${v} g/L`],
    ["be", "BE", (v) => sayiYaz(v, true)],
  ];
  const satirlar: { ad: string; deger: string }[] = [];
  for (const [anahtar, ad, yaz] of alanlar) {
    const v = sayi(vaka, anahtar);
    if (v !== undefined) satirlar.push({ ad, deger: yaz(v) });
  }
  return satirlar;
}

export default function VakaPaneli({ acik, onKapat, onYukle }: Props) {
  const kutu = useRef<HTMLDialogElement>(null);
  const basladi = useRef(false);
  const [durum, setDurum] = useState<Durum>({ tur: "yukleniyor" });
  const [seciliId, setSeciliId] = useState<string | null>(null);

  function vakalariGetir() {
    api
      .vakalar()
      .then((sonuc) => setDurum(sonuc.tur === "tamam" ? { tur: "hazir", vakalar: sonuc.veri } : { tur: "hata" }))
      .catch(() => setDurum({ tur: "hata" }));
  }

  // Vakalar panel ilk açıldığında bir kez alınır
  useEffect(() => {
    if (!acik || basladi.current) return;
    basladi.current = true;
    vakalariGetir();
  }, [acik]);

  // Tarayıcının yerleşik modal penceresi: odak panelin içinde kalır, Esc kapatır,
  // kapanınca odak paneli açan düğmeye döner
  useEffect(() => {
    const pencere = kutu.current;
    if (!pencere) return;
    if (acik && !pencere.open) pencere.showModal();
    if (!acik && pencere.open) pencere.close();
  }, [acik]);

  function kapandi() {
    setSeciliId(null);
    onKapat();
  }

  function yenidenDene() {
    setDurum({ tur: "yukleniyor" });
    vakalariGetir();
  }

  const vakalar = durum.tur === "hazir" ? durum.vakalar : [];
  const secili = vakalar.find((v) => v.id === seciliId);

  return (
    <dialog
      ref={kutu}
      className={styles.panel}
      aria-labelledby="vaka-baslik"
      onClose={kapandi}
      // Panelin dışına (karartılmış alana) tıklamak kapatır
      onClick={(e) => {
        if (e.target === kutu.current) kutu.current?.close();
      }}
    >
      <span className={styles.tutamac} aria-hidden="true" />
      <div className={styles.baslikSatiri}>
        <div>
          <h2 id="vaka-baslik" className={styles.baslik}>
            Hazır vakalar
          </h2>
          <p className={styles.altBaslik}>Eğitim amaçlı kurgusal vakalar. Birini seçince değerleri forma yüklenir.</p>
        </div>
        <button type="button" className={styles.kapat} aria-label="Kapat" onClick={() => kutu.current?.close()}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <path d="M6 6l12 12" />
            <path d="M18 6L6 18" />
          </svg>
        </button>
      </div>

      <div className={styles.liste}>
        {durum.tur === "yukleniyor" && <p className={styles.mesaj}>Vakalar yükleniyor…</p>}
        {durum.tur === "hata" && (
          <div className={styles.mesaj} role="alert">
            <p>Vakalar alınamadı. API’ye ulaşılamıyor ya da yanıt vermiyor.</p>
            <button type="button" className={dugme.ghost} onClick={yenidenDene}>
              Yeniden dene
            </button>
          </div>
        )}
        <ul className={styles.vakalar}>
          {vakalar.map((v) => (
            <VakaSatiri
              key={v.id}
              vaka={v}
              acik={v.id === seciliId}
              onSec={() => setSeciliId(v.id === seciliId ? null : v.id)}
            />
          ))}
        </ul>
      </div>

      <div className={styles.alt}>
        <button
          type="button"
          className={`${dugme.dolgun} ${styles.yukle}`}
          aria-disabled={!secili}
          onClick={() => {
            if (secili) onYukle(secili);
          }}
        >
          {secili ? "Değerleri forma yükle" : "Bir vaka seçin"}
        </button>
        <button type="button" className={dugme.ghost} onClick={() => kutu.current?.close()}>
          Vazgeç
        </button>
      </div>
    </dialog>
  );
}

function VakaSatiri({ vaka, acik, onSec }: { vaka: Vaka; acik: boolean; onSec: () => void }) {
  const be = sayi(vaka, "be");
  const ph = sayi(vaka, "ph");
  const pco2 = sayi(vaka, "pco2");
  const genislik = be === undefined ? 0 : Math.min(50, (Math.abs(be) / BE_OLCEK) * 50);
  const yon = be === undefined || be === 0 ? "sifir" : be < 0 ? "asit" : "baz";

  return (
    <li>
      <button type="button" className={`${styles.vaka} ${acik ? styles.secili : ""}`} aria-expanded={acik} onClick={onSec}>
        <span className={styles.ad}>{vaka.name}</span>
        <span className={styles.aciklama}>{vaka.description}</span>
        <span className={styles.ozet}>
          {ph !== undefined && `pH ${ph.toFixed(2)}`}
          {pco2 !== undefined && `, pCO₂ ${pco2}`}
        </span>
        {be !== undefined && (
          <span className={styles.be}>
            <span className={`${styles.beYazi} ${styles[yon]}`}>BE {sayiYaz(be, true)}</span>
            <span className={styles.beIz} aria-hidden="true">
              <span className={styles.beEksen} />
              {yon !== "sifir" && (
                <span
                  className={`${styles.beCubuk} ${styles[yon]}`}
                  style={yon === "asit" ? { right: "50%", width: `${genislik}%` } : { left: "50%", width: `${genislik}%` }}
                />
              )}
            </span>
          </span>
        )}
      </button>
      {acik && (
        <div className={styles.ayrinti}>
          <dl className={styles.degerler}>
            {ayrintiSatirlari(vaka).map((s) => (
              <div key={s.ad}>
                <dt>{s.ad}</dt>
                <dd>{s.deger}</dd>
              </div>
            ))}
          </dl>
          <div>
            <h3 className={styles.ogretici}>Öğretici nokta</h3>
            <p>{vaka.teaching_point}</p>
          </div>
          <p className={styles.not}>
            BE değeri cihaz alanına yazılır ama analizde kullanılmaz; BE, pH ve pCO₂’den hesaplanır. Cihaz değeri olarak
            kullanmak için forma geçince “Cihaz değerlerini gir”i açın.
          </p>
        </div>
      )}
    </li>
  );
}
