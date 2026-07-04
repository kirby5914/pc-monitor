#!/bin/bash
set -e

cd /opt/pc-monitor 

echo "🔄 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

echo "🔁 Restarting service..."
sudo systemctl restart dashboard

sleep 2

if ! systemctl is-active --quiet dashboard; then
  echo "❌ Service failed to start"
  exit 1
fi

echo "✅ Deploy complete"
echo "✅ Deploy finished: $(date)"

