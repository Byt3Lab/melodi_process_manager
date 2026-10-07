#!/usr/bin/env bash
set -e

echo "=== Compilation de Melodi Process Manager (PyInstaller) ==="

# Activer venv si présent
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Nettoyage
rm -rf build dist

# Compilation
pyinstaller --clean melodi_process_manager.spec

chmod +x dist/melodi_process_manager 2>/dev/null || true

echo "=== Compilation terminée ! Exécutable dans dist/melodi_process_manager ==="
