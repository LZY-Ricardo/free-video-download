FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# NOTE:
# VPS 当前到 deb.debian.org 链路不稳定，先不在镜像层安装 ffmpeg，
# 保证服务可启动；后续可通过可用镜像源或预构建镜像补齐 ffmpeg。

COPY requirements.txt /app/requirements.txt
RUN pip install --retries 20 --timeout 300 --prefer-binary -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/downloads /app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
