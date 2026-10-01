FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:24-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
# Destino do proxy /api/* (os rewrites do Next sao fixados no build).
ARG API_INTERNAL_URL=http://backend:8000
ENV API_INTERNAL_URL=$API_INTERNAL_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:24-alpine
WORKDIR /app
# Paginas publicas (contratacao e instituicao) sao renderizadas no servidor e chamam a API direto.
ARG API_INTERNAL_URL=http://backend:8000
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    API_INTERNAL_URL=$API_INTERNAL_URL
COPY --from=build /app ./
EXPOSE 3000
CMD ["node", "server.mjs"]
