#!/bin/bash

set -o pipefail

APP_DIR=$(pwd)
USER_NAME=$(whoami)

echo "🌿 Starting Flizlen VPS Setup..."
echo "📍 App Directory: $APP_DIR"
echo "👤 User: $USER_NAME"

# 1. System deps
echo "🔄 Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx git acl

# 2. Python venv
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "ℹ️ Virtual environment already exists."
fi

source venv/bin/activate
echo "📦 Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

chmod +x start_monolith.sh start_backend.sh start_frontend.sh

# 3. Nginx
echo "🌐 Configuring Nginx..."

if [ ! -f "nginx.conf.template" ]; then
    echo "❌ nginx.conf.template not found!"
    exit 1
fi

SERVER_NAME=${1:-_}
cp nginx.conf.template flizlen.nginx
sed -i "s|server_name _;|server_name $SERVER_NAME;|g" flizlen.nginx

sudo cp flizlen.nginx /etc/nginx/sites-available/flizlen
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/flizlen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Setup complete."
echo "➡️ Start the app with: ./start_monolith.sh"
