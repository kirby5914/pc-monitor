#!/bin/bash
set -e

cd /opt/pc-monitor

echo "🔄 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "🐍 Setting up virtual environment (if needed)..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔁 Restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart pc-monitor

sleep 2

if ! systemctl is-active --quiet pc-monitor; then
  echo "❌ Service failed to start"
  exit 1
fi

echo "✅ Deploy complete"
echo "✅ Finished at: $(date)"