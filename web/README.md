# Stewart asit-baz analizi: web arayüzü

Next.js (App Router, TypeScript) arayüzü. Hesaplama yapmaz; `/api/*` isteklerini Python API'sine (`api/`, varsayılan `localhost:8000`) yönlendirir ve çekirdeğin sonucunu gösterir. Kök dizindeki `README.md` projenin genel açıklamasını içerir.

## Çalıştırma

Depo kökünden `.\scripts\dev.ps1` (Windows) API ve web'i birlikte başlatır. Elle:

```bash
# depo kökünde
pip install -r requirements.txt -r api/requirements.txt
uvicorn api.main:app --port 8000

# web/ klasöründe
npm install
npm run dev        # http://localhost:3000
```

## Komutlar

| Komut | Ne yapar |
|---|---|
| `npm test` | Vitest birim testleri (`app/lib/*.test.ts`) |
| `npm run lint` | ESLint |
| `npm run build` | Üretim derlemesi (tip denetimi dahil) |
| `npm run api:tipleri` | `openapi.json`'dan `app/lib/api-types.ts` üretir |

API şeması değişince önce depo kökünde `python scripts/export_openapi.py`, sonra `npm run api:tipleri` çalıştırılır. Üretilen iki dosya da depoda tutulur; eski kalırsa CI hata verir.

## Yapı

- `app/components`: ekranlar ve bileşenler (CSS Modules; renk ve yazı ölçeği `app/globals.css` değişkenleriyle)
- `app/lib`: saf yardımcılar (biçimlendirme, form kuralları, sonuç satırları, grafik verisi) ve testleri; API istemcisi `api.ts`
- Klinik sayı, eşik ve metin çekirdekten ve `/api/meta`'dan gelir; arayüzde sabit yazılmaz.

Bu klasördeki `AGENTS.md`, `next dev` tarafından yazılır ve yeniden oluşturulur.
