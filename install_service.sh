#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install_service.sh)"
  exit 1
fi

echo "Installing JARVIS Service..."
cp jarvis.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable jarvis.service
systemctl start jarvis.service

echo "JARVIS Service installed and started!"
echo "Check status with: systemctl status jarvis.service"
