# Melodi Process Manager

Gestionnaire de processus autonome pour superviser, lancer, arrêter et recharger l'instance principale de **MELODI ERP**.

## Fonctionnalités

- Supervision du cycle de vie du processus MELODI (`/api/health`, `/api/start`, `/api/stop`, `/api/reload`).
- Exécution de commandes de reload propre via `scripts/reload.py` ou arrêt/redémarrage du serveur.
- Restriction de sécurité locale (localhost uniquement) et authentification par Bearer Token.
- Totalement découplé du core de MELODI.
- Compilable en exécutable autonome avec PyInstaller.

## Prérequis et Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lancement

En mode développement :
```bash
./start.sh [PORT] [TOKEN] [MELODI_PORT] [MELODI_DIR]
# ou
python3 main.py --port 8001 --token melodi_secret_token_123 --melodi-port 3000 --melodi-dir /chemin/vers/MELODI
```

## Compilation PyInstaller

Pour générer l'exécutable autonome dans `dist/melodi_process_manager` :

```bash
chmod +x build.sh
./build.sh
# ou
python3 build.py
```
