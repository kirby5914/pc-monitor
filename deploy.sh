#!/bin/bash
set -e

cd /opt/pc-monitor

echo "🔄 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "🐍 Ensuring virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "📦 Installing dependencies..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "🔁 Restarting service..."
systemctl daemon-reload
systemctl restart pc-monitor.service

sleep 2

echo "📊 Service status:"
systemctl --no-pager status pc-monitor.service

if ! systemctl is-active --quiet pc-monitor.service; then
    echo "❌ Service failed to start"
    journalctl -u pc-monitor.service -n 50 --no-pager
    exit 1
fi

echo "✅ Deploy complete"
echo "🕒 Finished at: $(date)"