# Use the official Node.js 20 Debian slim image as base (reduces Alpine-specific vulnerabilities)
# Pin the base image to a specific patched digest to avoid transient vulnerabilities;
# replace "<DIGEST>" with the latest patched digest from Docker Hub for node:20-bookworm-slim
ARG BASE_IMAGE=node:20-bookworm-slim
FROM ${BASE_IMAGE} AS base

# Apply security updates to the base image to address known vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies only when needed
FROM base AS deps
# On Debian-based images glibc is provided by default, so libc6-compat (Alpine) is not required.
# See https://github.com/nodejs/docker-node for details.
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --no-frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Install pnpm in builder stage
RUN npm install -g pnpm

# Install TypeScript type definitions for React and React DOM
RUN pnpm add -D @types/react @types/react-dom

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED=1

RUN pnpm build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
# Uncomment the following line in case you want to disable telemetry during runtime.
ENV NEXT_TELEMETRY_DISABLED=1

RUN groupadd -g 1001 nodejs
RUN useradd --system --uid 1001 --gid nodejs --shell /usr/sbin/nologin nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "server.js"]
