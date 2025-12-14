#!/bin/bash

# setup_vps.sh
# Automated setup script for Flizlen App on Ubuntu 20.04/22.04 VPS

set -e  # Exit on error

APP_DIR=$(pwd)
USER_NAME=$(whoami)

echo "🌿 Starting Flizlen VPS Setup..."
echo "📍 App Directory: $APP_DIR"
echo "👤 User: $USER_NAME"

# 1. Update System & Install Dependencies
echo "🔄 Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx git acl

# 2. Setup Python Virtual Environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "ℹ️ Virtual environment already exists."
fi

# Activate and install requirements
source venv/bin/activate
echo "📦 Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure Systemd Service
echo "⚙️ Configuring Systemd Service..."

# Check if flizlen.service file exists
if [ ! -f "flizlen.service" ]; then
    echo "❌ flizlen.service file not found! Please create it first."
    exit 1
fi

# Update user/path placeholders in service file if needed (dynamic replacement capability)
# For now, we assume the user might need to edit it manually or we use sed.
# Let's replace placeholders if they exist in the template
sed -i "s|User=REPLACE_USER|User=$USER_NAME|g" flizlen.service
sed -i "s|WorkingDirectory=REPLACE_PATH|WorkingDirectory=$APP_DIR|g" flizlen.service
sed -i "s|ExecStart=REPLACE_PATH|ExecStart=$APP_DIR|g" flizlen.service

# Copy to systemd
sudo cp flizlen.service /etc/systemd/system/flizlen.service
sudo systemctl daemon-reload
sudo systemctl enable flizlen
echo "✅ Systemd service enabled."

# 4. Configure Nginx
echo "🌐 Configuring Nginx..."

if [ ! -f "nginx.conf.template" ]; then
    echo "❌ nginx.conf.template not found!"
    exit 1
fi

# Create actual config
cp nginx.conf.template flizlen.nginx
sed -i "s|server_name _;|server_name $1;|g" flizlen.nginx  # $1 argument is domain/IP if provided

sudo cp flizlen.nginx /etc/nginx/sites-available/flizlen
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi
sudo ln -sf /etc/nginx/sites-available/flizlen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
echo "✅ Nginx configured and restarted."

# 5. Start Application
echo "🚀 Starting Flizlen App..."
sudo systemctl restart flizlen

echo "🎉 Deployment Setup Complete!"
echo "➡️  Check status with: sudo systemctl status flizlen"
echo "➡️  View logs with: journalctl -u flizlen -f"
