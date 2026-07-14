#!/bin/bash
echo "========================================"
echo " API Automation Test Platform          "
echo "========================================"

# ── 加载 .env 环境变量 ──
if [ -f /app/.env ]; then
    set -a
    . /app/.env
    set +a
    echo "[entry] 已加载 /app/.env"
else
    echo "[entry] WARN: /app/.env 不存在，使用系统环境变量"
fi

# ---- MySQL (MariaDB) ----
echo "[entry] MySQL..."
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASSWORD:-root123}"
if [ ! -d /var/lib/mysql/mysql ]; then
    mysql_install_db --user=root --datadir=/var/lib/mysql 2>/dev/null || \
    mariadb-install-db --user=root --datadir=/var/lib/mysql 2>/dev/null || true
fi
mkdir -p /run/mysqld 2>/dev/null || true
(mysqld --user=root --datadir=/var/lib/mysql --socket=/run/mysqld/mysqld.sock --port=3306 &) 2>/dev/null || \
(mariadbd --user=root --datadir=/var/lib/mysql --socket=/run/mysqld/mysqld.sock --port=3306 &) 2>/dev/null || true

MYSQL_OK=false
for i in $(seq 1 60); do
    if mysqladmin ping -u root --socket=/run/mysqld/mysqld.sock --silent 2>/dev/null; then MYSQL_OK=true; break
    elif mariadb-admin ping -u root --socket=/run/mysqld/mysqld.sock --silent 2>/dev/null; then MYSQL_OK=true; break
    fi; sleep 2
done

if [ "$MYSQL_OK" = true ]; then
    echo "[entry] MySQL OK, 设置密码..."
    mysql -u root --socket=/run/mysqld/mysqld.sock 2>/dev/null \
        -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_PASS}'; FLUSH PRIVILEGES;" || \
    mariadb -u root --socket=/run/mysqld/mysqld.sock 2>/dev/null \
        -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_PASS}'; FLUSH PRIVILEGES;" || true
    echo "[entry] 创建数据库..."
    mysql -u "${DB_USER}" -p"${DB_PASS}" --socket=/run/mysqld/mysqld.sock 2>/dev/null \
        -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME:-api}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || \
    mariadb -u "${DB_USER}" -p"${DB_PASS}" --socket=/run/mysqld/mysqld.sock 2>/dev/null \
        -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME:-api}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || true
else
    echo "[entry] WARN: MySQL 不可用"
fi

# ---- Redis ----
echo "[entry] Redis..."
redis-server --port 6379 --requirepass "${REDIS_PASSWORD:-123456}" --daemonize yes 2>/dev/null || \
redis-server --port 6379 --requirepass "${REDIS_PASSWORD:-123456}" &
for i in $(seq 1 30); do
    if redis-cli -a "${REDIS_PASSWORD:-123456}" ping 2>/dev/null | grep -q PONG; then
        echo "[entry] Redis OK"; break
    fi
    sleep 1
done
redis-cli -a "${REDIS_PASSWORD:-123456}" ping 2>/dev/null | grep -q PONG || echo "[entry] WARN: Redis 不可用"

# ---- Django ----
cd /app
if [ "$MYSQL_OK" = true ]; then
    echo "[entry] Django migrate..."
    for try in $(seq 1 5); do
        if python3 manage.py migrate --noinput 2>/dev/null; then
            echo "[entry] migrate OK (attempt $try)"; break
        fi
        echo "[entry] migrate retry $try/5..."
        sleep 3
    done
fi
python3 manage.py collectstatic --noinput 2>/dev/null || true

# ---- Gunicorn :8000（先启动，后续注册要用） ----
echo "[entry] Gunicorn :8000..."
cd /app
gunicorn api_automation_test.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - &
GUNICORN_PID=$!

# 等待 Gunicorn 就绪
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8000/admin/ 2>/dev/null > /dev/null; then
        echo "[entry] Gunicorn OK"; break
    fi
    sleep 1
done

# ---- 注册 agent 用户，获取 Token ----
REGISTER_RESP=$(curl -s -X POST http://127.0.0.1:8000/api/user/register \
    -H "Content-Type: application/json" \
    -d '{"username":"agent","password":"Agent@2024!Internal"}')
REGISTER_CODE=$(echo "$REGISTER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code'))" 2>/dev/null)

if [ "$REGISTER_CODE" = "999999" ]; then
    AGENT_TOKEN=$(echo "$REGISTER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['key'])" 2>/dev/null)
    echo "[entry] Agent registered, token: ${AGENT_TOKEN:0:8}..."
else
    AGENT_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/user/login \
        -H "Content-Type: application/json" \
        -d '{"username":"agent","password":"Agent@2024!Internal"}' \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['key'])" 2>/dev/null)
    echo "[entry] Agent login, token: ${AGENT_TOKEN:0:8}..."
fi
export AUTOMATION_AUTH_TOKEN="$AGENT_TOKEN"

# ---- Agent :9000 ----
echo "[entry] Agent :9000..."
cd /app/agent
nohup python server.py --host 0.0.0.0 --port 9000 --log-level warning > /tmp/agent.log 2>&1 &

# ---- Nginx :80 ----
echo "[entry] Nginx :80..."
cd /app
mkdir -p /var/log/nginx /var/lib/nginx/body 2>/dev/null || true
nginx -t && nginx -g 'daemon off;' &
NGINX_PID=$!

# ---- 保持 Gunicorn 前台运行 ----
echo "[entry] All services started."
wait $GUNICORN_PID
