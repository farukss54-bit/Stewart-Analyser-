# Ev sunucusuna kurulum (Docker + Tailscale)

React arayüzünü (web) ve API'sini tek komutla Docker üzerinde çalıştırır. Eski Streamlit uygulaması bu kurulumda yoktur.

## Gerekenler
- Docker ve Docker Compose v2 (`docker compose version` çalışmalı)
- Sunucuda ve telefonda/bilgisayarda Tailscale (aynı tailnet)
- Sunucunun internete çıkabilmesi (imaj derlenirken paketler ve yazı tipleri indirilir; çalışırken internet gerekmez)

## İlk kurulum
Sunucuda:

```bash
git clone -b feature/react-arayuz https://github.com/farukss54-bit/Stewart-Analyser-.git
cd Stewart-Analyser-

# Arayüzün hangi adresten dinleyeceği: sunucunun Tailscale IP'si
echo "STEWART_BIND=$(tailscale ip -4 | head -n1)" > .env

docker compose up -d --build
```

İlk derleme birkaç dakika sürer. Bitince:

```bash
docker compose ps        # api ve web "healthy" görünmeli
```

Telefonda (Tailscale açıkken) tarayıcıya `http://<sunucunun-tailscale-ip>:3000` yazın. Adresi görmek için sunucuda `tailscale ip -4`. MagicDNS açıksa `http://<sunucu-adı>:3000` de çalışır.

`.env` dosyası yoksa ya da `STEWART_BIND` boşsa arayüz yalnızca sunucunun kendisinden (`127.0.0.1`) erişilebilir olur; bu bilerek güvenli varsayılandır. Ev ağındaki (Wi-Fi) herkese açmak için `STEWART_BIND=0.0.0.0` yazabilirsiniz, ama giriş (şifre) olmadığını unutmayın.

## Güncelleme
```bash
cd Stewart-Analyser-
git pull
docker compose up -d --build
```

## Durdurma, kaldırma
```bash
docker compose stop      # durdurur, imajlar kalır
docker compose down      # kaldırır
```
Sunucu yeniden başlarsa servisler kendiliğinden açılır (`restart: unless-stopped`).

## Ayarlar (`.env`)
| Değişken | Anlamı | Varsayılan |
|---|---|---|
| `STEWART_BIND` | Arayüzün dinlediği adres | `127.0.0.1` |
| `STEWART_PORT` | Sunucuda yayınlanan port | `3000` |

## Gizlilik ve güvenlik
- Girilen değerler sunucuda saklanmaz. API durumsuzdur.
- API, analiz ettiği değerleri konsola yazar; Docker konsol çıktısını diskte tutar. Bu yüzden API servisinin günlüğü kapalıdır (`logging: driver: none`). Bunun sonucu: `docker compose logs api` çalışmaz. Sorun ararken geçici olarak `docker-compose.yml` içindeki `logging:` iki satırını silip `docker compose up -d` çalıştırın, işiniz bitince geri koyun.
- Uygulamada kullanıcı girişi yoktur; tailnet'e erişimi olan herkes kullanabilir. Erişimi kısıtlamak için Tailscale ACL'lerini kullanın.
- Tailscale trafiği zaten şifreler; bu yüzden `http` yeterlidir. Tarayıcıda "güvenli değil" uyarısı görmek isterseniz sunucuda `tailscale serve --bg 3000` ile `https://<sunucu-adı>.<tailnet>.ts.net` adresi açılabilir.
- API portu (8000) sunucudan dışarıya yayınlanmaz; yalnızca web servisi ona ulaşır.

## Sorun giderme
| Belirti | Bakılacak yer |
|---|---|
| Telefonda sayfa açılmıyor | Telefonda Tailscale açık mı? `.env` içindeki IP, `tailscale ip -4` çıktısıyla aynı mı? Sunucunun güvenlik duvarında 3000 portu Tailscale arayüzüne açık mı (Ubuntu'da `ufw allow in on tailscale0 to any port 3000`)? |
| Sayfa açılıyor ama sonuç gelmiyor | `docker compose ps`: api "healthy" mi? `docker compose restart api` |
| Güncellemeden sonra eski sayfa görünüyor | Tarayıcıyı sert yenileyin; `docker compose up -d --build` çalıştığından emin olun |
| `port is already allocated` | `.env` içine `STEWART_PORT=3100` gibi başka bir port yazıp `docker compose up -d` |
