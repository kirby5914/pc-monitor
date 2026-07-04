#!/bin/bash
set -e

echo "== Heartbeat Installer =="

if [ "$EUID" -ne 0 ]; then
    echo "Run as root"
    exit 1
fi

INSTALL_DIR="/opt/heartbeat"
REPO="https://raw.githubusercontent.com/kirby5914/pc-monitor/main/node"

mkdir -p "$INSTALL_DIR"

echo "Downloading files..."

curl -fsSL "$REPO/heartbeat.py" -o "$INSTALL_DIR/heartbeat.py"
curl -fsSL "$REPO/.env.example" -o "$INSTALL_DIR/.env"

echo "Setting up node configuration..."

read -p "Enter node name (e.g. Plex): " NODE_NAME
read -p "Enter Pi server URL: " PI_SERVER

cat > "$INSTALL_DIR/.env" <<EOF
NODE_NAME=$NODE_NAME
PI_SERVER=$PI_SERVER
EOF

cd "$INSTALL_DIR"

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing dependencies..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install requests python-dotenv

echo "Installing systemd service..."

curl -fsSL "$REPO/services/heartbeat.service" -o /etc/systemd/system/heartbeat.service

systemctl daemon-reload
systemctl enable heartbeat.service
systemctl restart heartbeat.service

echo ""
echo "✅ Heartbeat installed successfully!"
echo "Service status:"
systemctl status heartbeat.service --no-pager