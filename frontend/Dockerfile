FROM oven/bun:1.0.36-slim

WORKDIR /app

COPY package.json tsconfig.json vite.config.ts ./
RUN bun install

COPY . .

RUN bun run build

EXPOSE 3000
CMD ["bun", "run", "dev"]