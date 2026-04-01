#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOWNLOAD_DIR="${ROOT_DIR}/backend/downloads"
EXPIRE_HOURS="${EXPIRE_HOURS:-24}"

if [[ ! -d "${DOWNLOAD_DIR}" ]]; then
  echo "目录不存在: ${DOWNLOAD_DIR}"
  exit 0
fi

echo "清理 ${DOWNLOAD_DIR} 中超过 ${EXPIRE_HOURS} 小时的临时文件..."

find "${DOWNLOAD_DIR}" -type f -mmin "+$((EXPIRE_HOURS * 60))" \
  \( -name "*.mp4" -o -name "*.mkv" -o -name "*.webm" -o -name "*.mov" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.part" -o -name "*.vtt" -o -name "*.srt" \) \
  -print -delete

echo "清理完成。"

