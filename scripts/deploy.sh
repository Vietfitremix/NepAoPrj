#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "    VIET-FIT / NẾP ÁO PRODUCTION DEPLOY   "
echo "=========================================="

COMPOSE_FILE="docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

if [ ! -f ".env" ]; then
    echo "Warning: .env file not found, creating from .env.example..."
    cp .env.example .env
    echo "Please configure .env before production use!"
fi

echo "[1/4] Pulling / building container images..."
docker compose -f "$COMPOSE_FILE" pull || docker compose -f "$COMPOSE_FILE" build

echo "[2/4] Starting database & backend services..."
docker compose -f "$COMPOSE_FILE" up -d postgres
echo "Waiting for postgres to become healthy..."
docker compose -f "$COMPOSE_FILE" exec -T postgres sh -c 'until pg_isready -U "${POSTGRES_USER:-viet_fit}" -d "${POSTGRES_DB:-viet_fit}"; do sleep 2; done'

echo "[3/4] Launching all services..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "[4/4] Verifying health checks..."
sleep 5

check_health() {
    local url=$1
    local name=$2
    local retries=15
    local wait_sec=3
    echo "Checking $name at $url..."
    for i in $(seq 1 $retries); do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✓ $name is UP and healthy!"
            return 0
        fi
        echo "Waiting for $name ($i/$retries)..."
        sleep $wait_sec
    done
    echo "✗ $name failed health check."
    return 1
}

check_health "http://localhost:8000/ai/health" "AI Service" || true
check_health "http://localhost:8080/api/health" "Spring Backend" || true
check_health "http://localhost/nginx-health" "Frontend Web Server" || true

echo "=========================================="
echo "  Deploy completed successfully!          "
echo "  Web UI:     http://localhost            "
echo "  API Docs:   http://localhost:8080/api   "
echo "  AI Service: http://localhost:8000/ai    "
echo "=========================================="
