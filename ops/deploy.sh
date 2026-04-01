#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -f ".env.production" ]]; then
  echo "缺少 .env.production，请先基于 .env.production.example 创建。"
  exit 1
fi

mkdir -p backend/downloads backend/models

echo "[1/4] 拉取最新代码"
git pull --ff-only

echo "[2/4] 构建并启动服务"
docker compose pull || true
docker compose build --no-cache api
docker compose up -d

echo "[3/4] 等待健康检查"
sleep 5
docker compose exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5)" >/dev/null || {
  echo "健康检查失败，请执行: docker compose logs --tail=200 api caddy"
  exit 1
}

echo "[4/4] 部署完成"
docker compose ps
