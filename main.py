import os
import sys
import json
import asyncio
import logging
import argparse
import subprocess
from quart import Quart, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("melodi_process_manager")

app = Quart(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Melodi Process Manager")
parser.add_argument("--token", type=str, default=os.environ.get("MELODI_PROCESS_MANAGER_TOKEN", "melodi_secret_token_123"), help="API authentication token")
parser.add_argument("--port", type=int, default=8001, help="Process Manager port")
parser.add_argument("--melodi-port", type=int, default=3000, help="Melodi application port")
parser.add_argument("--melodi-dir", type=str, default="", help="Path to Melodi project directory")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Bind host")
parser.add_argument("--env", type=str, default="dev", help="Environment (dev/prod)")
args, unknown = parser.parse_known_args()

melodi_port = args.melodi_port
port = args.port
env = args.env
api_token = args.token
host = args.host

# Resolve target MELODI directory
melodi_dir = args.melodi_dir
if not melodi_dir:
    # Try sibling directory '../MELODI'
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(os.path.dirname(parent_dir), "MELODI")
    if os.path.isdir(candidate):
        melodi_dir = candidate
    else:
        melodi_dir = os.getcwd()

config = {
    "api_token": api_token,
    "port": port,
    "melodi_port": melodi_port,
    "melodi_dir": melodi_dir,
    "host": host,
    "env": env,
}


@app.before_request
async def limit_to_localhost():
    remote_ip = request.remote_addr
    if remote_ip not in ("127.0.0.1", "::1", "localhost"):
        logger.warning(f"Forbidden access attempt from non-localhost IP: {remote_ip}")
        return jsonify({"status": "error", "message": "Forbidden: Localhost only"}), 403


def check_auth(headers) -> bool:
    """
    Validates Bearer token in the Authorization header.
    """
    auth_header = headers.get("Authorization")
    if not auth_header:
        return False
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    return parts[1] == config["api_token"]


async def run_action_async(action_name: str):
    await asyncio.sleep(0.1)
    target_dir = config["melodi_dir"]
    target_port = config["melodi_port"]
    target_env = config["env"]

    logger.info(f"[ProcessManager] Executing action '{action_name}' on port {target_port} (dir: {target_dir})")

    script_map = {
        "start": "scripts/start.py",
        "stop": "scripts/stop.py",
        "reload": "scripts/restart.py",
        "restart": "scripts/restart.py",
    }
    script_rel = script_map.get(action_name)
    if not script_rel:
        logger.warning(f"[ProcessManager] Unknown action: {action_name}")
        return

    script_path = os.path.join(target_dir, script_rel)
    if os.path.isfile(script_path):
        cmd = [sys.executable, script_path, "--port", str(target_port), "--env", target_env]
        try:
            subprocess.Popen(cmd, cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"[ProcessManager] Action '{action_name}' launched via script {script_path}")
        except Exception as e:
            logger.error(f"[ProcessManager] Error executing {action_name}: {e}")
    else:
        logger.warning(f"[ProcessManager] Script not found at {script_path}")


def execute_action_background(action_name: str):
    asyncio.create_task(run_action_async(action_name))


@app.route("/api/start", methods=["POST"])
async def api_start():
    if not check_auth(request.headers):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    execute_action_background("start")
    return jsonify({"status": "accepted", "message": "Start initiated"}), 202


@app.route("/api/stop", methods=["POST"])
async def api_stop():
    if not check_auth(request.headers):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    execute_action_background("stop")
    return jsonify({"status": "accepted", "message": "Stop initiated"}), 202


@app.route("/api/reload", methods=["POST"])
@app.route("/api/restart", methods=["POST"])
async def api_reload():
    if not check_auth(request.headers):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    log_path = os.path.join(config["melodi_dir"], "config", "reload_log.txt")
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("Melodi is reloading via Process Manager\n")
    except Exception as e:
        logger.warning(f"[ProcessManager] Could not write reload log: {e}")

    execute_action_background("reload")
    return jsonify({"status": "accepted", "message": "Reload initiated"}), 202


@app.route("/api/health", methods=["GET"])
async def api_health():
    return jsonify({
        "status": "ok",
        "service": "melodi_process_manager",
        "melodi_port": config["melodi_port"],
        "melodi_dir": config["melodi_dir"],
    }), 200


if __name__ == "__main__":
    bind_host = config["host"]
    bind_port = config["port"]
    logger.info(f"Starting Melodi Process Manager on http://{bind_host}:{bind_port}")
    try:
        from hypercorn.config import Config as HyperConfig
        from hypercorn.asyncio import serve
        hconfig = HyperConfig()
        hconfig.bind = [f"{bind_host}:{bind_port}"]
        asyncio.run(serve(app, hconfig))
    except ImportError:
        app.run(host=bind_host, port=bind_port)
