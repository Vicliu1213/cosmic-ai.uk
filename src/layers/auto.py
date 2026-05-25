"""一鍵部署 — 引擎 + 隧道 + API 網關"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("auto_deploy")

WS = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path.home() / ".hermes"
_engine_proc = None  # global for wait_for_api health check
ENV_FILE = CONFIG_DIR / ".env"
NGROK_YML = WS / "config" / "ngrok.yml"
NGROK_HOME_CONFIG = Path.home() / ".config" / "ngrok" / "ngrok.yml"


def load_env():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def save_env(key: str, value: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().splitlines()
    lines = [l for l in lines if not l.startswith(f"{key}=")]
    lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


def write_ngrok_config(token: str):
    content = f"""version: "3"
agent:
  authtoken: "{token}"
tunnels:
  cosmic-synergy-panel:
    proto: http
    addr: 8788
    inspect: true
    host_header: "localhost:8788"
"""
    NGROK_YML.write_text(content)
    (Path.home() / ".config" / "ngrok").mkdir(parents=True, exist_ok=True)
    if NGROK_HOME_CONFIG.exists() or True:
        NGROK_HOME_CONFIG.unlink(missing_ok=True)
        NGROK_HOME_CONFIG.symlink_to(NGROK_YML)
    logger.info(f"✓ ngrok.yml written to {NGROK_YML}")


def setup_ngrok():
    env = load_env()
    token = env.get("NGROK_AUTHTOKEN", "")

    if not token:
        print("╔════════════════════════════════════════════╗")
        print("║  Need ngrok Authtoken                       ║")
        print("║  https://dashboard.ngrok.com                 ║")
        print("║    → get-started → your-authtoken            ║")
        print("╚════════════════════════════════════════════╝")
        token = input("Paste your ngrok Authtoken: ").strip()
        if not token:
            logger.error("No token provided")
            return False
        save_env("NGROK_AUTHTOKEN", token)

    write_ngrok_config(token)

    # Validate
    result = subprocess.run(["ngrok", "config", "check"], capture_output=True, text=True)
    if "Valid" not in result.stdout:
        logger.error(f"ngrok config invalid: {result.stderr}")
        return False
    logger.info("✓ ngrok config valid")
    return True


def start_engine(keep_running: bool = True) -> subprocess.Popen:
    env = os.environ.copy()
    if keep_running:
        env["COSMIC_KEEP_RUNNING"] = "1"

    proc = subprocess.Popen(
        [sys.executable, str(WS / "main.py")],
        cwd=str(WS),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    logger.info(f"✓ Engine started (PID={proc.pid})")
    return proc


def wait_for_api(port: int = 8788, timeout: int = 120) -> bool:
    import urllib.request
    url = f"http://localhost:{port}/api/synergy/status"
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        global _engine_proc
        if _engine_proc and _engine_proc.poll() is not None:
            logger.error("Engine died prematurely")
            return False
        time.sleep(2)
    return False


def start_ngrok() -> Optional[str]:
    # Kill all stale ngrok processes
    pids = [p for p in os.popen("pgrep -f ngrok").read().strip().split() if p]
    if pids:
        subprocess.run(["kill", "-9"] + pids, capture_output=True)
        time.sleep(2)

    proc = subprocess.Popen(
        ["ngrok", "start", "cosmic-synergy-panel", "--log=stdout"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(6)

    import urllib.request
    for i in range(15):
        try:
            with urllib.request.urlopen("http://localhost:4040/api/tunnels") as r:
                data = json.loads(r.read())
                tunnels = data.get("tunnels", [])
                if tunnels:
                    url = tunnels[0]["public_url"]
                    logger.info(f"✓ ngrok tunnel: {url}")
                    return url
        except Exception:
            pass
        time.sleep(2)
    logger.warning("⚠ ngrok tunnel not ready")
    return None


def auto_deploy():
    print("╔════════════════════════════════════════════╗")
    print("║  Cosmic Engine v3.0 — Auto Deploy          ║")
    print("╚════════════════════════════════════════════╝")

    # 1. ngrok setup
    if not setup_ngrok():
        return

    # 2. Start engine
    global _engine_proc
    _engine_proc = start_engine()
    print("  Engine starting... (waiting for API)")

    # 3. Wait for API
    if wait_for_api():
        print("✓ Synergy API ready on port 8788")
    else:
        print("✗ API timeout")
        return

    # 4. Start ngrok tunnel
    url = start_ngrok()

    # 5. Print summary
    print("")
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Cosmic Engine Deployed                              ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  Engine PID:  {_engine_proc.pid}")
    print(f"║  Local API:   http://localhost:8788")
    print(f"║  Public URL:  {url or '— (ngrok not ready)'}")
    print(f"║  Synergy:     http://localhost:8788/pages/synergy_panel.html")
    print(f"║  API Levels:  http://localhost:8788/api/synergy/levels")
    print("╚══════════════════════════════════════════════════════╝")
    print("")

    if url:
        save_env("NGROK_URL", url)

    _engine_proc.wait()


if __name__ == "__main__":
    auto_deploy()
