#!/bin/bash

git add .
git commit -m "update"
git push origin main

echo "Deploying on PI (192.168.1.180)"

ssh admin@192.168.1.180 "cd /opt/pc-monitor && bash deploy.sh"

echo "Deployment complete!"