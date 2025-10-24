# Render.com Deployment Troubleshooting Log

## Problem
Render.com was deploying the Flask backend (`python app.py`) instead of the Angular frontend, resulting in outdated CSS and missing frontend changes.

## Root Cause
Render's auto-detection prioritizes Python runtime when it finds `requirements.txt`, even when Docker configuration is specified. The service was created with Python runtime and cannot be changed to Docker runtime after creation.

## Attempted Solutions (All Failed)

### 1. Update render.yaml with dockerCommand
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    runtime: docker
    plan: free
    dockerCommand: cd frontend && npm run serve:ssr:frontend
    dockerfilePath: ./Dockerfile
```

**Result:** Render ignored `dockerCommand` and still ran `gunicorn app:app`

**Why it failed:** Render was still using Python runtime detection

### 2. Remove dockerCommand, rely on Dockerfile CMD
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    runtime: docker
    plan: free
    dockerfilePath: ./Dockerfile
```

**Result:** Still ran Python runtime

**Why it failed:** `runtime: docker` was invalid syntax at the time

### 3. Remove invalid 'runtime: docker' field
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    plan: free
    dockerfilePath: ./Dockerfile
```

**Result:** Still ran Python runtime (`pip install -r requirements.txt`)

**Why it failed:** Auto-detection saw `requirements.txt` and assumed Python project

### 4. Rename requirements.txt to avoid Python detection
**What we tried:**
- Renamed `requirements.txt` → `requirements-docker.txt`
- Updated Dockerfile to use renamed file
- Kept `dockerfilePath: ./Dockerfile`

**Result:** Build failed with "Could not open requirements file: requirements.txt"

**Why it failed:** Render was still trying to use Python runtime

### 5. Add explicit env: docker
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
```

**Result:** Still tried Python runtime

**Why it failed:** `env: docker` is incorrect syntax

### 6. Correct syntax with runtime: docker
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    runtime: docker
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
```

**Result:** Still ignored Docker config and tried Python runtime

**Why it failed:** Existing service was created with Python runtime, cannot be changed

## Key Findings

1. **Runtime cannot be changed after service creation** - Once a Render service is created with Python runtime, it cannot be switched to Docker runtime via render.yaml updates

2. **Auto-detection priority** - Render prioritizes `requirements.txt` detection over `dockerfilePath` configuration

3. **Blueprint limitations** - Certain fields in render.yaml are ignored when updating existing services

## Working Solution Options (Not Attempted)

### Option A: Create New Service
Delete current service and create a new one with Docker runtime from the start:
1. Delete existing `ai-trading-bot` service in Render dashboard
2. Create new service selecting "Docker" as runtime
3. Connect to same GitHub repository
4. Use render.yaml with `runtime: docker`

### Option B: Manual Service Creation
Create service manually in Render dashboard:
1. Choose "New" → "Web Service"  
2. Select "Deploy an existing image" or "Build from Dockerfile"
3. Configure to use Dockerfile directly
4. Skip render.yaml entirely

### Option C: Use Different Deployment Platform
Consider platforms that better support Docker deployments:
- Railway.app
- Fly.io  
- DigitalOcean App Platform
- Heroku (with Container Registry)

## Files Modified During Troubleshooting

### render.yaml
- Removed `runtime: docker` (thought it was invalid)
- Added `dockerCommand` 
- Tried `env: docker`
- Added `dockerContext: .`

### Dockerfile  
- Updated port configuration from static to dynamic
- Updated health check endpoints
- Changed requirements.txt reference to requirements-docker.txt

### File Renames
- `requirements.txt` → `requirements-docker.txt`

### 7. Python deployment with inline Angular build commands
**What we tried:**
```yaml
services:
  - type: web
    name: ai-trading-bot
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
      sudo apt-get install -y nodejs
      cd frontend && npm install && npm run build
    startCommand: python app.py
```

**Result:** Only `pip install -r requirements.txt` executed, all Node.js/Angular steps ignored

**Why it failed:** Render's Python auto-detection overrode custom buildCommand. Multi-line commands in render.yaml were completely ignored.

### 8. Python deployment with build script
**What we tried:**
- Created `build.sh` script with Node.js installation and Angular build
- Updated render.yaml: `buildCommand: chmod +x build.sh && ./build.sh`
- Script contained same steps as attempt #7

**Result:** Build script was **completely ignored**. Log starts with `pip install` cached packages, no sign of script execution.

**Why it failed:** Render's Python auto-detection completely overrode the custom `buildCommand`. The build script was never executed - Render went straight to `pip install -r requirements.txt`.

## Current State

- **Service type:** Python runtime (cannot be changed)
- **Deployment:** Flask backend running on port 10000  
- **Frontend:** Flask serves Angular build from `frontend/dist/frontend/browser/`
- **CSS issue:** Still present - Angular build is outdated (styles-5INURTSO.css is 0 bytes)
- **Root problem:** Angular build never refreshes because Render won't run Node.js build steps

## Key Insights

1. **Render ignores custom build commands** when it detects a Python project
2. **Angular build is stale** - the CSS file is empty (0 bytes) from failed local build
3. **Flask is serving correctly** - it's serving from `frontend/dist/frontend/browser/` as intended
4. **The issue is build-time, not runtime** - we need fresh Angular build with CSS

## Next Steps

To actually get latest CSS, we need to either:
1. **Create new Render service** with Docker runtime from scratch, OR
2. **Use different deployment platform** that better supports mixed Python/Node.js builds, OR  
3. **Fix the Angular build locally** and commit working dist files, OR
4. **Use Render's native Node.js runtime** for frontend only (separate from Python backend)

**Note:** All attempts to modify existing Python service to build Angular have failed due to Render's auto-detection limitations.