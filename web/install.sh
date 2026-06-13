#!/usr/bin/env bash
#
# HoloTamagotchi —— 美術動畫 Review 模擬器 一鍵安裝 / 啟動腳本
# =============================================================
# 用途：把這支 install.sh 單獨丟到一台「完全乾淨」的 VM（Linux / macOS）上執行，
#       不需要先 git clone 整個 repo，腳本會自己：
#         1. 確認 / 安裝 git
#         2. 確認 / 安裝 Node.js（NodeSource apt → nvm → brew 依序嘗試）
#         3. 用 sparse-checkout「只」抓 repo 裡的 web/ 子目錄
#         4. npm 安裝相依、npm run build（正式打包）
#         5. 用 node 起 production server，預設對外（0.0.0.0）開在 3000 埠
#
# 最簡用法（repo 為 public，或 VM 已有可存取 GitHub 的 SSH key）：
#         bash install.sh
#
# 私有 repo 用 token（不裝 SSH key 也能抓）：
#         GITHUB_TOKEN=ghp_xxx bash install.sh
#
# 常用環境變數（都可選）：
#         GITHUB_TOKEN   GitHub PAT，repo 為 private 時用它走 HTTPS
#         REPO_URL       覆寫來源 repo（預設指向本專案）
#         REPO_BRANCH    分支（預設 main）
#         INSTALL_DIR    安裝目錄（預設 ./holotamagotchi-web）
#         PORT           對外埠（預設 3000）
#         HOST           綁定位址（預設 0.0.0.0，對外可連）
#         NODE_VERSION   要裝的 Node 主版本（預設 22）
#         NO_START=1     只安裝 + build，不自動起 server
#
set -euo pipefail

# ---- 設定（可被環境變數覆寫）------------------------------------------------
REPO_OWNER_REPO="normantaipei/HoloTamagotchi"
REPO_URL="${REPO_URL:-}"
REPO_BRANCH="${REPO_BRANCH:-main}"
INSTALL_DIR="${INSTALL_DIR:-$PWD/holotamagotchi-web}"
PORT="${PORT:-3000}"
HOST="${HOST:-0.0.0.0}"
NODE_VERSION="${NODE_VERSION:-22}"
NO_START="${NO_START:-0}"

# ---- 小工具 ----------------------------------------------------------------
log()  { printf '\033[1;36m▶ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

SUDO=""
if [ "$(id -u)" -ne 0 ] && have sudo; then SUDO="sudo"; fi

OS="$(uname -s)"

# ---- 1. 套件管理器偵測（給裝 git / node 用）--------------------------------
pkg_install() {
  # 用系統套件管理器安裝一個套件，盡量跨發行版
  local pkg="$1"
  if have apt-get; then
    $SUDO apt-get update -y && $SUDO apt-get install -y "$pkg"
  elif have dnf; then
    $SUDO dnf install -y "$pkg"
  elif have yum; then
    $SUDO yum install -y "$pkg"
  elif have pacman; then
    $SUDO pacman -Sy --noconfirm "$pkg"
  elif have apk; then
    $SUDO apk add --no-cache "$pkg"
  elif have brew; then
    brew install "$pkg"
  else
    return 1
  fi
}

# ---- 2. 確保 git ------------------------------------------------------------
ensure_git() {
  if have git; then ok "git 已存在：$(git --version)"; return; fi
  log "未偵測到 git，開始安裝…"
  pkg_install git || die "無法自動安裝 git，請手動安裝後重跑。"
  ok "git 安裝完成：$(git --version)"
}

# ---- 3. 確保 Node.js（>=20）------------------------------------------------
node_major() { node -v 2>/dev/null | sed 's/^v//; s/\..*//'; }

ensure_node() {
  if have node && [ "$(node_major)" -ge 20 ] 2>/dev/null; then
    ok "Node 已存在：$(node -v)"; return
  fi
  log "未偵測到合適的 Node.js（需 >=20），開始安裝 Node ${NODE_VERSION}…"

  # 3a. Debian/Ubuntu：走 NodeSource（最穩）
  if have apt-get; then
    if curl -fsSL "https://deb.nodesource.com/setup_${NODE_VERSION}.x" | $SUDO -E bash -; then
      $SUDO apt-get install -y nodejs && { ok "Node 安裝完成：$(node -v)"; return; }
    fi
    warn "NodeSource 安裝失敗，改試 nvm…"
  fi

  # 3b. macOS：先試 brew
  if [ "$OS" = "Darwin" ] && have brew; then
    brew install "node@${NODE_VERSION}" && brew link --overwrite --force "node@${NODE_VERSION}" \
      && { ok "Node 安裝完成：$(node -v)"; return; }
    warn "brew 安裝失敗，改試 nvm…"
  fi

  # 3c. 通用 fallback：nvm（裝在使用者家目錄，免 root）
  export NVM_DIR="$HOME/.nvm"
  if [ ! -s "$NVM_DIR/nvm.sh" ]; then
    have curl || pkg_install curl || die "需要 curl 來安裝 nvm"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  fi
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
  nvm install "${NODE_VERSION}" && nvm use "${NODE_VERSION}" \
    || die "Node 安裝失敗，請手動安裝 Node >=20 後重跑。"
  ok "Node 安裝完成：$(node -v)"
}

# ---- 4. 解析 repo URL（含 token 注入）-------------------------------------
resolve_repo_url() {
  if [ -n "$REPO_URL" ]; then echo "$REPO_URL"; return; fi
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "https://${GITHUB_TOKEN}@github.com/${REPO_OWNER_REPO}.git"
  else
    # 無 token：優先用 SSH（VM 若有 key 最方便），無 key 時 git 會自己報錯提示
    if [ -f "$HOME/.ssh/id_ed25519" ] || [ -f "$HOME/.ssh/id_rsa" ]; then
      echo "git@github.com:${REPO_OWNER_REPO}.git"
    else
      echo "https://github.com/${REPO_OWNER_REPO}.git"
    fi
  fi
}

# ---- 5. sparse-checkout 只抓 web/ ------------------------------------------
fetch_web() {
  local url; url="$(resolve_repo_url)"
  local shown="${url/$GITHUB_TOKEN/***}"  # log 時遮蔽 token
  log "抓取來源：${shown}（branch: ${REPO_BRANCH}，只取 web/）"

  if [ -d "$INSTALL_DIR/.git" ]; then
    log "偵測到既有安裝目錄，改為更新：$INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch --depth 1 origin "$REPO_BRANCH"
    git -C "$INSTALL_DIR" reset --hard "origin/${REPO_BRANCH}"
  else
    git clone --depth 1 --filter=blob:none --sparse --branch "$REPO_BRANCH" \
      "$url" "$INSTALL_DIR" \
      || die "git clone 失敗。若為私有 repo，請改用：GITHUB_TOKEN=xxx bash install.sh"
    git -C "$INSTALL_DIR" sparse-checkout set web
  fi
  [ -d "$INSTALL_DIR/web" ] || die "抓取後找不到 web/ 目錄，請確認 repo 結構。"
  ok "原始碼就緒：$INSTALL_DIR/web"
}

# ---- 6. 安裝相依 + build ----------------------------------------------------
build_app() {
  cd "$INSTALL_DIR/web"
  log "安裝 npm 相依（這步最久，請耐心等）…"
  if [ -f package-lock.json ]; then npm ci; else npm install; fi
  ok "相依安裝完成"

  log "正式打包：npm run build"
  npm run build
  [ -f ".output/server/index.mjs" ] || die "build 後找不到 .output/server/index.mjs"
  ok "打包完成 → .output/"
}

# ---- 7. 起 production server ------------------------------------------------
start_server() {
  cd "$INSTALL_DIR/web"
  cat <<EOF

$(ok "全部就緒！")
  伺服器即將啟動：
    HOST = ${HOST}   PORT = ${PORT}
    本機開：  http://localhost:${PORT}
    VM 對外： http://<VM-IP>:${PORT}   （記得放行防火牆 / 安全群組 ${PORT} 埠）

  下次只想直接啟動（免重新 build）：
    cd "${INSTALL_DIR}/web" && HOST=${HOST} PORT=${PORT} node .output/server/index.mjs

EOF
  log "啟動中…（Ctrl-C 結束）"
  exec env HOST="$HOST" PORT="$PORT" node .output/server/index.mjs
}

# ---- main ------------------------------------------------------------------
main() {
  log "HoloTamagotchi web 一鍵安裝開始（OS: ${OS}）"
  have curl || pkg_install curl || warn "缺 curl，部分安裝路徑可能受影響"
  ensure_git
  ensure_node
  fetch_web
  build_app
  if [ "$NO_START" = "1" ]; then
    ok "已完成安裝與 build（NO_START=1），未啟動 server。"
    echo "手動啟動： cd \"${INSTALL_DIR}/web\" && HOST=${HOST} PORT=${PORT} node .output/server/index.mjs"
  else
    start_server
  fi
}

main "$@"
