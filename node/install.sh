#!/bin/bash
set -e

echo "== Heartbeat Installer =="

if [ "$EUID" -ne 0 ]; then
    echo "Run as root"
    exit 1
fi

INSTALL_DIR="/opt/heartbeat"
PI_SERVER="http://192.168.1.180:5000"

mkdir -p "$INSTALL_DIR"

echo "Installing system dependencies..."
apt update -y
apt install -y python3 python3-pip python3-venv curl

echo "Enter node name:"
read NODE_NAME

echo "Writing environment file..."
cat > "$INSTALL_DIR/.env" <<EOF
NODE_NAME=$NODE_NAME
PI_SERVER=$PI_SERVER
EOF

echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/.venv"

echo "Installing Python dependencies..."
$INSTALL_DIR/.venv/bin/pip install --upgrade pip
$INSTALL_DIR/.venv/bin/pip install requests python-dotenv

echo "Installing heartbeat service..."
cat > /etc/systemd/system/heartbeat.service <<EOF
[Unit]
Description=Heartbeat Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/heartbeat
EnvironmentFile=/opt/heartbeat/.env
ExecStart=/opt/heartbeat/.venv/bin/python /opt/heartbeat/heartbeat.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable heartbeat.service
systemctl restart heartbeat.service

echo "✅ Installed successfully"
systemctl status heartbeat.service --no-pager