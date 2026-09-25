# Yamancı | Özer — Avukatlık & Arabuluculuk

Bu depo, Yamancı | Özer Avukatlık & Arabuluculuk web sitesinin kaynaklarını içerir.

## Yayın dizini
Cloudflare tarafından yayınlanan statik site: `dist/`

## Cloudflare
Workers Static Assets yapılandırması `wrangler.jsonc` dosyasındadır.
Deploy komutu:

`npm run deploy`

Dağıtımdan önce statik çıktıyı yeniden üretmek ve yapılandırmayı kontrol etmek için:

```bash
npm run build
npm run check:deploy
```

Yerel Wrangler kimlik doğrulaması gerekiyorsa `.env.example` dosyasını `.env`
olarak kopyalayın ve Cloudflare hesap kimliği ile sınırlı yetkili API token'ını
yalnızca bu yerel dosyaya yazın. `.env` Git tarafından yok sayılır.

## İçerik
Blog kaynak verileri `content/`, blog üretim betiği `scripts/` dizinindedir.
GitHub → Cloudflare otomatik dağıtım aktiftir.
