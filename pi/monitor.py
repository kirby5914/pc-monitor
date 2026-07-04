from flask import Flask, request
import time
import threading
import requests
import os
from dotenv import load_dotenv
import json
from pathlib import Path

STATE_FILE = Path("/opt/pc-monitor/state/json")

# Load environment variables (.env)
load_dotenv()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return (
                set(data.get("known_pcs", [])),
                data.get("last_seen", {}),
                set(data.get("alerted", []))
            )
    return set(), {}, set()

def save_state():
    data = {
        "known_pcs": list(known_pcs),
        "last_seen": last_seen,
        "alerted": list(alerted)
    }

    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("State save failed:", e)

app = Flask(__name__)

# ===== CONFIG =====
TIMEOUT = 30        # seconds before OFFLINE
CHECK_INTERVAL = 5  # loop delay

# ===== STATE =====
known_pcs, last_seen, alerted = load_state()


# ===== DISCORD =====
def send_discord(message):
    if not DISCORD_WEBHOOK:
        print("⚠️ Missing DISCORD_WEBHOOK")
        return

    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
    except Exception as e:
        print("Discord error:", e)


# ===== HEARTBEAT ENDPOINT =====
@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json

    if not data or "name" not in data:
        return "missing name", 400

    pc_name = data["name"]

    # register PC
    known_pcs.add(pc_name)
    last_seen[pc_name] = time.time()

    print(f"[{time.strftime('%H:%M:%S')}] heartbeat from {pc_name}", flush=True)

    return "ok"


# ===== MONITOR LOOP =====
def monitor_loop():
    while True:
        now = time.time()

        for pc in list(known_pcs):
            last = last_seen.get(pc, 0)

            # OFFLINE
            if now - last > TIMEOUT:
                if pc not in alerted:
                    send_discord(f"🚨 **OFFLINE:** `{pc}` is not responding")
                    alerted.add(pc)

            # ONLINE / RECOVERY
            else:
                if pc in alerted:
                    send_discord(f"✅ **ONLINE:** `{pc}` is back online")
                    alerted.remove(pc)

        time.sleep(CHECK_INTERVAL)


# ===== START =====
if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

    
