#!/bin/bash
set -e

echo "== PC Monitor Deploy =="

# Must run as root (prevents sudo issues later)
if [ "$EUID" -ne 0 ]; then
    echo "Run this with: sudo ./deploy.sh"
    exit 1
fi

cd /opt/pc-monitor

echo "🔄 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "🐍 Ensuring virtual environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Repair broken venv if pip is missing
if [ ! -f ".venv/bin/pip" ]; then
    echo "⚠️ Broken venv detected — rebuilding..."
    rm -rf .venv
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
    echo "❌ Service failed to start!"
    echo "---- Recent logs ----"
    journalctl -u pc-monitor.service -n 50 --no-pager
    exit 1
fi

echo "✅ Deploy complete"
echo "🕒 Finished at: $(date)"