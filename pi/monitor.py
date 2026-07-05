from flask import Flask, request
import time
import threading
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

TIMEOUT = 15
last_seen = {}
alerted = set()

def send_discord(msg):
    if not DISCORD_WEBHOOK:
        print("[ERROR] Missing webhook")
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except Exception as e:
        print("[DISCORD ERROR]", e)

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json
    if not data or "name" not in data:
        return "missing name", 400

    name = data["name"]
    last_seen[name] = time.time()

    print(f"[HEARTBEAT] {name}", flush=True)
    return "ok"


def monitor_loop():
    while True:
        now = time.time()

        for node, last in list(last_seen.items()):

            if now - last > TIMEOUT:
                if node not in alerted:
                    send_discord(f"🚨 OFFLINE: {node}")
                    alerted.add(node)

            else:
                if node in alerted:
                    send_discord(f"✅ ONLINE: {node}")
                    alerted.remove(node)

        time.sleep(2)


if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)