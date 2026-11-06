import ApiStatus from "./ApiStatus";

export default function Home() {
  return (
    <main style={{ padding: "32px", maxWidth: "60ch" }}>
      <h1>Stewart asit-baz analizi</h1>
      <p>Yeni arayüz iskeleti. Tasarım sonraki aşamalarda eklenecek.</p>
      <ApiStatus />
    </main>
  );
}
