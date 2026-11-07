import type { Metadata } from "next";
import { Atkinson_Hyperlegible_Next, Source_Serif_4 } from "next/font/google";
import Footer from "./components/Footer";
import { MetaProvider } from "./components/MetaProvider";
import { TEMA_ANAHTARI } from "./components/tema";
import "./globals.css";

// Türkçe karakterler (ğ, ş, ı, İ) latin-ext alt kümesindedir
const atkinson = Atkinson_Hyperlegible_Next({
  variable: "--font-atkinson",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

const sourceSerif = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin", "latin-ext"],
  weight: "600",
});

export const metadata: Metadata = {
  title: "Stewart asit-baz analizi",
  description:
    "Stewart-Fencl yaklaşımıyla kan gazı değerlendirmesi. Eğitim amaçlıdır; tanı veya tedavi önerisi değildir.",
};

// Kullanıcı tema seçtiyse sayfa çizilmeden uygulanır (yanlış temayla yanıp sönmesin).
// Yalnızca "light" veya "dark" kabul edilir; depolama kapalıysa sessizce atlanır.
const temaBetigi = `try{var t=localStorage.getItem(${JSON.stringify(TEMA_ANAHTARI)});if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // suppressHydrationWarning: betik data-theme özniteliğini React'ten önce ekler
    <html
      lang="tr"
      className={`${atkinson.variable} ${sourceSerif.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: temaBetigi }} />
      </head>
      <body>
        <MetaProvider>
          {children}
          <Footer />
        </MetaProvider>
      </body>
    </html>
  );
}
