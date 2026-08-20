# ==================================================
# Usta kg — Web Dockerfile (Next.js standalone, build context ./web)
# ==================================================
FROM node:18-alpine AS builder

WORKDIR /app
ARG NEXT_PUBLIC_API_BASE=/api/v1
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# ---- Runtime image ----
FROM node:18-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]