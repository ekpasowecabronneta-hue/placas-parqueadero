#!/bin/bash
# Inicia servidor y generador en el VPS (puerto 8080)
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
BIN="${DIR}/build"
SERVER="${BIN}/parking_server"
GENERATOR="${BIN}/parking_generator"
PORT="${1:-8080}"
INTERVAL="${2:-2}"

if [[ ! -x "$SERVER" ]]; then
  echo "Compile primero: bash scripts/deploy_vps.sh"
  exit 1
fi

pkill -9 -f "${SERVER}" 2>/dev/null || true
pkill -9 -f "${GENERATOR}" 2>/dev/null || true
sleep 1

nohup "${SERVER}" "$PORT" > /tmp/parking_server.log 2>&1 &
sleep 1
nohup "${GENERATOR}" 127.0.0.1 "$PORT" "$INTERVAL" > /tmp/parking_generator.log 2>&1 &
echo "Servidor y generador en puerto $PORT"
echo "Logs: /tmp/parking_server.log /tmp/parking_generator.log"
