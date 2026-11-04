# AGENTS.md — Stewart Analyser Çalışma Protokolü

> **ÖNCE BUNU OKU — bir cümlede protokol:**
> Dar kal, doğrula, kanıt getir, **commit'leme**, sapmanı beyan et, klinik
> doğruluğu koda tercih et. Emin değilsen **dur ve sor.**
>
> Bu bir özet değil, bir sözleşmedir. Altındaki 10 madde bunu açar. Hepsini
> oku, ama bu altı kelimeyi unutma.

---

Bu dosya, bu depoda çalışan her yapay zeka ajanı (Kimi Code, Claude Code,
ve diğerleri) içindir. Kodlamaya başlamadan önce **tamamını oku**. Buradaki
kurallar, projenin sahibi Faruk'un üzerinde uzlaşılmış çalışma biçimidir;
bir talimat bu kurallarla çelişiyorsa, **dur ve sor** — kuralları kendi
başına esnetme.

---

## 1. Proje nedir

Stewart Analyser, fizikokimyasal (Stewart-Figge) asit-baz analizi yapan bir
Streamlit uygulamasıdır. Hekimlerin kan gazı değerlerini saniyeler içinde
yorumlamasını sağlar. Proje şu an akademik yayına (JOSS / SoftwareX)
hazırlanmaktadır; bu yüzden kod kalitesi, test güvenilirliği ve depo hijyeni
kritiktir.

Kullanıcı yazılımcı değil, acil tıp hekimidir. Teknik kararların gerekçesini
açık yaz; "şöyle yaptım" değil, "şu yüzden şöyle yaptım".

---

## 2. Mimari sınırlar — ihlal etme

Katmanlar ayrıdır ve ayrı kalır. Mantık (logic) ile sunum (UI) karışmaz:

| Dosya | Sorumluluk | Kural |
|---|---|---|
| `core.py` | Hesaplama motoru (SID, SIG, BE, sınıflama) | Deterministik çekirdek. **Kutsaldır.** |
| `validation.py` | Girdi doğrulama ve temizleme | Projenin kalbi. Savunmacı. |
| `ui_components.py` | Streamlit arayüz parçaları | Hesaplama mantığı İÇERMEZ. |
| `app.py` | Giriş noktası, akış | İnce tutulur. |
| `constants.py` | Eşik değerleri, CDS notları, örnek vakalar | Değerler literatüre bağlıdır. |
| `visualization.py` | Grafikler (Gamblegram vb.) | Sunum katmanı. |
| `logger.py` | Loglama | |
| `cds_differential.py` | Klinik karar destek diferansiyeli | |

**Monolitik yapı üretme.** Bir fonksiyon hem hesaplıyor hem çiziyorsa, yanlış
yerdedir. Yeni kod eklerken önce "bu hangi katmana ait" diye sor.

---

## 3. ALTIN KURAL: Ajan commit atmaz

**Hiçbir koşulda `git commit` çalıştırma.** `git push` çalıştırma.

Değişiklikleri working tree'de bırak. Faruk diff'i inceler ve kendi
commit'ler. Bu, projenin tek değişmez kuralıdır. "Kolaylık olsun diye"
commit'leme; "nasılsa testler geçiyor" diye commit'leme.

Yaptığın değişiklikleri `git add` ile staged'a alabilirsin (inceleme kolaylığı
için), ama commit kararı Faruk'undur.

---

## 4. Test protokolü

Testler bu projenin güvenlik ağıdır. Onlara göre davran:

- **İşe başlamadan önce** `python -m pytest -q` koş. Beklenen sayıyı not et.
  Başlangıç sayısı beklenenden farklıysa **DUR ve bildir** — kirli bir zeminde
  çalışma.
- **İş bittikten sonra** tekrar koş. Sayı, o işin beklenen sonucuyla
  eşleşmeli.
- **Test sayısı bir hedef değil, bir alarmdır.** Sana "şu sayıyı tuttur"
  denmez; "şu sayı çıkmıyorsa dur" denir. Sayıyı tutturmak için **asla** assert
  değiştirme, test sil, ya da testi gevşetme. Sayı yanlışsa, yaptığın işi geri
  al ve bildir — testi değil, işi sorgula.
- Bir iş test sayısını bilerek düşürüyorsa (ör. bir modül kaldırılıyor), bu
  **prompt'ta açıkça yazılı** olmalı. Yazılı değilse, düşüş bir hatadır.

**Dikkat:** `pytest` yeşil yanması "her şey yolunda" demek değildir; "koşabildiğim
testler geçti" demektir. Bir test dosyası import hatasıyla hiç toplanmazsa ya da
sessizce silinirse, pytest yine yeşil yanabilir — daha az test koşarak. Bu yüzden
**sayıyı her zaman raporla.**

---

## 5. Değiştirmeden / silmeden önce doğrula

Yıkıcı işlemler (silme, taşıma, yeniden adlandırma) körlemesine yapılmaz:

- **Silmeden önce:** O dosyaya/sembole repo genelinde referans ara (import,
  doküman linki, config). Referans bulursan **DUR ve bildir** — kendi başına
  silme.
- **Taşımadan önce:** Import yollarının kırılıp kırılmayacağını analiz et.
  Önce analizi sun, sonra uygula (çok adımlı işlerde).
- **Geri alınamaz işlerde** (binary dosya, satır sonu normalizasyonu) önce
  envanter çıkar, Faruk'un onayını bekle, sonra uygula.

Doğru sonuç yeterli değildir; **doğru gerekçe** de gerekir. Bir dosyanın
gereksiz olduğunu iddia ediyorsan, neden gereksiz olduğunu kanıtla.

---

## 6. Sapma dürüstlüğü

- Sana "aynen taşı / sadece şunu değiştir" dendiyse ve sen **tek karakter bile**
  fazladan değiştirdiysen (girinti, boşluk, satır sonu dahil), bunu raporunda
  **açıkça beyan et.** Küçük ve zararsız olması, gizlenmesini mazur göstermez.
- Emin olmadığın yerde **tahmin etme.** "Belirsiz" yaz ve nedenini söyle.
  Emin görünmek için uydurmak, en ağır hatadır.
- Bir hata yaptıysan ve kendi doğrulaman yakaladıysa: düzelt, **ve söyle.**
  Sessizce düzeltme.

Faruk bağımsız olarak doğrular (diff okur, pytest koşar, grep'ler). Seni
yakalamasını beklemek yerine, kendin beyan et. Dürüstlük, mükemmellikten
değerlidir.

---

## 7. Kapsam disiplini

- Her prompt'ta bir **DOKUNMA listesi** olur. Ona harfiyen uy.
- İşinin dışında bir tutarsızlık, hata veya iyileştirme fırsatı görürsen:
  **RAPORLA, düzeltme.** Kapsamı Faruk genişletir, sen değil.
- "Bu arada şunu da düzelteyim" refleksi, bu projede bir hatadır. Dar kal.
- Bir prompt belirsizse ve yanlış yorum pahalıysa: dur, sor.

---

## 8. Rapor formatı — kanıt getir

Her iş sonunda yapılandırılmış rapor ver. Hikâye değil, **kanıt**:

1. Başlangıç doğrulaması (`git status` temiz mi, başlangıç pytest sayısı)
2. Ne yapıldı (dosya dosya)
3. İlgili komut çıktıları (grep sonucu, `git status --short`, vb.)
4. `python -m pytest -q` son satırı (sayı dahil)
5. Beklenen vs. gerçek sayı karşılaştırması
6. Sapma beyanı (madde 6)

"Tamamlandı, her şey yolunda" bir rapor değildir. Doğrulanabilir çıktı sun.

---

## 9. Klinik hassasiyet

Bu bir tıbbi araçtır. Hesaplama mantığı klinik literatüre sadıktır:

- SID, SIG, BE, anyon açığı hesapları **Stewart, Figge, Fencl** metodolojisine
  uygun olmalı.
- `constants.py` içindeki eşik değerleri ve CDS notları keyfi değildir;
  literatüre dayanır. Bir eşiği değiştirmen istenirse, kaynağını sor.
- Klinik bir tutarsızlık fark edersen (bir formül, bir eşik, bir sınıflama
  yanlış görünüyorsa): **kod olarak doğru olsa bile RAPORLA.** Tıbbi doğruluk,
  kodun kendi içinde tutarlı olmasından önce gelir.
- Klinik kararı sen veremezsin. Veriyi sun, kararı Faruk'a bırak.

---

## 10. Bilinen tuzaklar

Bu projede daha önce başa bela olmuş teknik ayrıntılar:

- **Satır sonları (LF):** Depo satır sonlarını LF'te sabitler (`.gitattributes`).
  Windows'ta çalışıyorsan editörün CRLF gösterebilir; git kaydederken çevirir.
  `git diff` "tüm satırlar değişti" diyorsa, muhtemelen satır sonudur, içerik
  değil — `git diff --ignore-all-space` ile doğrula.
- **`sys.path`:** Testler `tests/` altındadır ve `pytest.ini` içindeki
  `pythonpath = .` ile çözülür. Test dosyalarına elle `sys.path.insert`
  **ekleme** — gereksiz ve yanıltıcıdır.
- **Mojibake / encoding:** Dosyalar yoğun Türkçe karakter, bilimsel sembol
  (±, →, ≤) ve emoji içerir. Kodlama bozulması (mojibake) olursa, el yapımı
  string-replace haritaları yerine `ftfy.fix_encoding()` kullan. Detay:
  `docs/AGENTS.md` içindeki ilgili bölüm.
- **İki makine:** Proje iki makinede geliştirilir (asıl: Windows dizüstü,
  ikincil: Ubuntu masaüstü). `origin/main` tek hakikat kaynağıdır. İşe
  başlamadan önce güncel olduğundan emin ol.

---

## Kapanış

Bu kuralların hepsi tek bir amaca hizmet eder: Faruk'un yaptığın işi
**güvenle inceleyebilmesi.** Dar kapsam, temiz diff, doğrulanabilir rapor —
hepsi bunun için. İncelemeyi kolaylaştıran her şey doğru, zorlaştıran her şey
yanlıştır. Şüphedeyken bu soruyu sor: "Bu, Faruk'un işimi incelemesini
kolaylaştırıyor mu, zorlaştırıyor mu?"
