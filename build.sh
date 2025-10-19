#!/bin/bash
set -e

echo "==> Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

echo "==> Verifying Node.js installation..."
node --version
npm --version

echo "==> Installing Angular dependencies..."
cd frontend
npm install

echo "==> Building Angular app..."
npm run build

echo "==> Verifying Angular build..."
ls -la dist/

echo "==> Installing Python dependencies..."
cd ..
pip install -r requirements.txt

echo "==> Build complete!"