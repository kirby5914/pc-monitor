import os
import socket
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# URL of your Raspberry Pi monitor
PI_SERVER = os.getenv("PI_SERVER")

# Use the computer's hostname automatically
PC_NAME = socket.gethostname()

# How often to send a heartbeat
HEARTBEAT_INTERVAL = 10

print(f"Starting heartbeat for {PC_NAME}")

while True:
    try:
        requests.post(
            f"{PI_SERVER}/heartbeat",
            json={"name": PC_NAME},
            timeout=5,
        )
        print(f"Heartbeat sent from {PC_NAME}")
    except Exception as e:
        print(f"Failed to contact monitor: {e}")

    time.sleep(HEARTBEAT_INTERVAL)