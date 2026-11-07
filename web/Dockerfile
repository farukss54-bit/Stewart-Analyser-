# Stewart Asit-Baz Analizi: web imajı (Next.js)
# Derleme bağlamı web/ klasörüdür. Tarayıcı yalnızca bu uygulamaya bağlanır; /api/* istekleri
# sunucu tarafında API servisine yönlendirilir (next.config.ts, STEWART_API_URL).
FROM node:22-slim

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Yönlendirme adresi derleme sırasında da çalışma sırasında da aynı olmalı
ARG STEWART_API_URL=http://api:8000
ENV STEWART_API_URL=${STEWART_API_URL}

# Yazı tipleri derleme sırasında indirilir ve imaja gömülür (çalışırken internet gerekmez)
RUN npm run build && chown -R node:node /app
USER node

ENV NODE_ENV=production
ENV PORT=3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

EXPOSE 3000

CMD ["npm", "start"]
