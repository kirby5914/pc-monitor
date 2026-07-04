from flask import Flask, request
import time
import threading
import requests
import os
from dotenv import load_dotenv

# Load .env (webhook lives here)
load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

app = Flask(__name__)

# How long before we say a PC is down (seconds)
TIMEOUT = 30

# heartbeat storage
last_seen = {}

# track alert state so we don’t spam Discord
alerted = set()


def send_discord(message):
    if not DISCORD_WEBHOOK:
        print("⚠️ No webhook set in .env")
        return

    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
    except Exception as e:
        print("Discord error:", e)


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json

    if not data or "name" not in data:
        return "missing name", 400

    pc_name = data["name"]
    last_seen[pc_name] = time.time()

    return "ok"


def monitor_loop():
    while True:
        now = time.time()

        for pc, last in list(last_seen.items()):

            # OFFLINE DETECTION
            if now - last > TIMEOUT:
                if pc not in alerted:
                    send_discord(f"🚨 **OFFLINE:** `{pc}` is not responding")
                    alerted.add(pc)

            # RECOVERY DETECTION
            else:
                if pc in alerted:
                    send_discord(f"✅ **ONLINE:** `{pc}` is back online")
                    alerted.remove(pc)

        time.sleep(5)


if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)