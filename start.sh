#!/usr/bin/env bash
# Démarrage de Melodi Process Manager

PORT="${1:-8001}"
TOKEN="${2:-melodi_secret_token_123}"
MELODI_PORT="${3:-3000}"
MELODI_DIR="${4:-}"

ARGS="--port $PORT --token $TOKEN --melodi-port $MELODI_PORT"
if [ -n "$MELODI_DIR" ]; then
    ARGS="$ARGS --melodi-dir $MELODI_DIR"
fi

if [ -f "dist/melodi_process_manager" ]; then
    echo "Démarrage de l'exécutable compilé..."
    exec ./dist/melodi_process_manager $ARGS
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    exec python3 main.py $ARGS
fi
