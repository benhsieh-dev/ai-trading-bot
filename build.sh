#\!/bin/bash
set -e

echo "🏗️ Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js 18
echo "📦 Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js installation
echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Install Angular dependencies and build
echo "📦 Installing Angular dependencies..."
cd frontend
npm install

echo "🏗️ Building Angular frontend..."
npm run build

echo "✅ Build completed successfully\!"
ls -la dist/frontend/browser/
EOF < /dev/null