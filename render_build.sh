#!/bin/bash
set -o pipefail

echo "🛠️  Render Build Script Started..."

# 1. Install Dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Permissions
# Ensure the start script is executable
echo "🔑 Setting permissions..."
chmod +x start_render.sh

echo "✅ Build Complete!"
