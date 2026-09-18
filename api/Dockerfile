# Dockerfile
FROM oven/bun:1.2-alpine AS base
WORKDIR /app

# ── dependências ──────────────────────────────────────────
FROM base AS deps
COPY package.json ./
RUN bun install

# ── desenvolvimento (hot-reload) ──────────────────────────
FROM base AS development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 4000
# comando sobrescrito pelo docker-compose (bun --hot index.ts)
CMD ["bun", "--hot", "index.ts"]
