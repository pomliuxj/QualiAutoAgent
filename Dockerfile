# ============================================================
# QualiAutoAgent — 前后端一体 Dockerfile
# Django + FastAPI Agent + Vue Frontend + MySQL + Redis + Nginx
# 构建: docker build -t app .
# ============================================================



# ─── Stage 1: 前端构建 ─────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend
COPY Interfince-front/package.json Interfince-front/package-lock.json ./

RUN npm install --ignore-scripts --legacy-peer-deps

COPY Interfince-front/ ./
RUN npm run build

# ─── Stage 2: Python wheel 构建 ────────────────────────────
FROM python:3.12-slim AS wheel-builder

# 国内源: apt
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libmariadb-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY inferfince-backend/requirements.txt .
# 国内源: pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# ─── Stage 3: 运行时 ───────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="dev@qualiautoagent.io"
LABEL description="QualiAutoAgent — AI 自动化测试平台"

# --- 系统依赖（仅运行时） ---
# 国内源: apt
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-server \
    redis-server \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Python 依赖（从 wheel 安装，无需 gcc） ---
COPY --from=wheel-builder /wheels /wheels
# 国内源: pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# --- 应用代码 ---
WORKDIR /app
COPY inferfince-backend/ /app/
COPY docker-entrypoint.sh /app/

# --- 前端构建产物 ---
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# --- nginx 配置 & 清理默认配置 ---
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf 2>/dev/null; true
COPY Interfince-front/nginx.conf /etc/nginx/conf.d/default.conf

# --- 必要目录 ---
RUN mkdir -p /app/logs /app/data/docs /app/data/qdrant /app/data/logs \
    && chmod +x /app/docker-entrypoint.sh

# --- 框架默认值（具体配置见 .env 文件） ---
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=api_automation_test.settings
ENV PYTHONUNBUFFERED=1

EXPOSE 80
EXPOSE 8000
EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -sf http://127.0.0.1:80/ || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
