from flask import Flask, request
import time
import threading
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

app = Flask(__name__)

# ===== CONFIG =====
TIMEOUT = 6
CHECK_INTERVAL = 1

# ===== STATE =====
last_seen = {}
status = {}  # "online" / "offline"


# ===== DISCORD =====
def send_discord(msg):
    if not DISCORD_WEBHOOK:
        print("Missing webhook")
        return

    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except Exception as e:
        print("Discord error:", e)


# ===== HEARTBEAT ENDPOINT =====
@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json

    if not data or "name" not in data:
        return "missing name", 400

    pc = data["name"]

    last_seen[pc] = time.time()

    # mark as online if previously offline
    if status.get(pc) == "offline":
        status[pc] = "online"
        send_discord(f"✅ ONLINE: {pc}")

    else:
        status[pc] = "online"

    print(f"heartbeat: {pc}", flush=True)

    return "ok"


# ===== MONITOR LOOP =====
def monitor():
    while True:
        now = time.time()

        for pc, last in list(last_seen.items()):
            if now - last > TIMEOUT:
                if status.get(pc) != "offline":
                    status[pc] = "offline"
                    send_discord(f"🚨 OFFLINE: {pc}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)