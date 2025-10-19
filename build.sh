#!/bin/bash
set -e

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Checking Node.js availability..."
which node || echo "Node.js not found"
which npm || echo "npm not found"

echo "==> Installing Node.js via package manager..."
# Try different methods to install Node.js
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    # Method 1: Try apt-get (most common)
    apt-get update && apt-get install -y nodejs npm || echo "apt-get failed"
    
    # Method 2: Try yum (for CentOS/RHEL)
    if ! command -v node &> /dev/null; then
        yum install -y nodejs npm || echo "yum failed"
    fi
    
    # Method 3: Download and install manually
    if ! command -v node &> /dev/null; then
        echo "Installing Node.js manually..."
        curl -fsSL https://nodejs.org/dist/v18.18.0/node-v18.18.0-linux-x64.tar.xz | tar -xJ
        export PATH=$PWD/node-v18.18.0-linux-x64/bin:$PATH
    fi
fi

echo "==> Node.js version:"
node --version || echo "Node.js still not available"
npm --version || echo "npm still not available"

echo "==> Building Angular app..."
cd frontend
npm install
npm run build
cd ..

echo "==> Build complete!"
ls -la frontend/dist/ || echo "No dist directory created"