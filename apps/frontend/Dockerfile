FROM node:22-alpine

WORKDIR /app

# pnpm 설치
RUN corepack enable && corepack prepare pnpm@latest --activate

# 의존성 설치
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# 소스 복사
COPY . .

CMD ["pnpm", "dev"]
