import socket
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv("/opt/heartbeat/.env")

PI_SERVER = os.getenv("PI_SERVER", "http://192.168.1.180:5000")
NODE_NAME = os.getenv("NODE_NAME", socket.gethostname())

INTERVAL = 5

print(f"[HEARTBEAT] Started for {NODE_NAME}")

while True:
    try:
        requests.post(
            f"{PI_SERVER}/heartbeat",
            json={"name": NODE_NAME},
            timeout=5
        )
        print(f"[HEARTBEAT] sent from {NODE_NAME}")
    except Exception as e:
        print(f"[ERROR] heartbeat failed: {e}")

    time.sleep(INTERVAL)