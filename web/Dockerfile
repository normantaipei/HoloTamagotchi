# HoloTamagotchi 美術動畫 Review 模擬器 —— production 容器
# 多階段：build 階段裝相依 + 打包，runtime 階段只留 .output，映像小、無原始碼。
# 建置 context = web/ 目錄。

# ---- build ----------------------------------------------------------------
FROM node:22-slim AS build
WORKDIR /app

# 非互動：跳過 Nuxt 遙測詢問，避免在無 TTY 的 build 環境卡住
ENV CI=1 \
    NUXT_TELEMETRY_DISABLED=1 \
    npm_config_yes=true

# 先只拷 lockfile 以善用 layer cache（相依沒變就不重裝）
COPY package.json package-lock.json ./
RUN npm ci

# 再拷其餘原始碼並打包
COPY . .
RUN npm run build

# ---- runtime --------------------------------------------------------------
FROM node:22-slim AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    NUXT_TELEMETRY_DISABLED=1 \
    HOST=0.0.0.0 \
    PORT=3000

# 只帶打包產物（Nitro 已把 server 需要的相依一起 bundle 進 .output）
COPY --from=build /app/.output ./.output

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
