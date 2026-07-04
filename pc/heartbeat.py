import socket
import time
import requests
import os

PI_SERVER = os.getenv("PI_SERVER", "http://192.168.1.180:5000")

NAME = socket.gethostname()
INTERVAL = 10

print(f"Heartbeat started: {NAME}")

while True:
    try:
        requests.post(
            f"{PI_SERVER}/heartbeat",
            json={"name": NAME},
            timeout=5
        )
    except Exception:
        pass

    time.sleep(INTERVAL)