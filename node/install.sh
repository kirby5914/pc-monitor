#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "== Heartbeat Installer =="

if [ "$EUID" -ne 0 ]; then
    echo "Please run this installer as root."
    exit 1
fi

# Create install directory
mkdir -p /opt/heartbeat

# Copy heartbeat script
cp "$SCRIPT_DIR/heartbeat.py" /opt/heartbeat/

echo "Setting up node configuration..."

read -p "Enter node name (e.g. Plex): " NODE_NAME
read -p "Enter Pi server URL: " PI_SERVER

cat > /opt/heartbeat/.env <<EOF
NODE_NAME=$NODE_NAME
PI_SERVER=$PI_SERVER
EOF

cd /opt/heartbeat

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing Python packages..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install requests python-dotenv

echo "Installing systemd service..."

cp "$SCRIPT_DIR/services/heartbeat.service" /etc/systemd/system/heartbeat.service

systemctl daemon-reload
systemctl enable heartbeat.service
systemctl restart heartbeat.service

echo ""
echo "===================================="
echo "✅ Heartbeat installed successfully!"
echo "===================================="
echo ""
echo "Service status:"
systemctl --no-pager status heartbeat.service