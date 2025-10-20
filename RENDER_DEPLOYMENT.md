# Deploying Flask + Angular App to Render.com

This document outlines the proper way to deploy a Flask backend with Angular frontend to Render.com using the Python runtime.

## Problem with Docker Runtime

Initially tried using Docker runtime with `env: docker` in render.yaml, but Render consistently ignored this setting and defaulted to Python runtime, running only `pip install -r requirements.txt` instead of executing custom build commands or Dockerfile.

## Solution: Python Runtime with Built Angular Files

### Key Steps:

1. **Remove Angular dist/ from .gitignore**
   - Edit `frontend/.gitignore`: Comment out `/dist` line
   - Edit root `.gitignore`: Add `!frontend/dist/` exception after `dist/` line

2. **Build Angular locally**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. **Commit built files to git**
   ```bash
   git add frontend/dist/
   git commit -m "Add Angular build files for deployment"
   ```

4. **Configure Flask to serve Angular**
   ```python
   # In app.py
   @app.route('/', defaults={'path': ''})
   @app.route('/<path:path>')
   def serve_angular(path=''):
       if path.startswith('api/'):
           return abort(404)
       try:
           if path and ('.' in path):
               return send_from_directory('frontend/dist/frontend/browser', path)
           return send_file('frontend/dist/frontend/browser/index.html')
       except:
           return send_file('frontend/dist/frontend/browser/index.html')
   ```

5. **Configure render.yaml for Python runtime**
   ```yaml
   services:
     - type: web
       name: ai-trading-bot
       env: python  # Use Python runtime, NOT docker
       plan: free
       # No custom buildCommand needed - default pip install works
       envVars:
         - key: FLASK_ENV
           value: production
         - key: PAPER
           value: "True"
         - key: ALPACA_API_KEY
           sync: false
         - key: ALPACA_API_SECRET
           sync: false
       healthCheckPath: /api/status
   ```

## Important Notes:

- **Render's Python runtime ignores custom buildCommand**: Even with `buildCommand` specified, Render runs `pip install -r requirements.txt`
- **Docker runtime requires explicit service creation**: Cannot change runtime type after service creation
- **Committing dist/ files is necessary**: Render builds in clean environment without Node.js in Python runtime
- **File paths matter**: Angular build creates `frontend/dist/frontend/browser/` structure
- **MIME types**: Flask automatically handles JS/CSS MIME types when serving from `send_from_directory`

## Deployment Flow:

1. Build Angular locally → commit dist files → push to GitHub
2. Render pulls code → runs `pip install -r requirements.txt` → starts Flask
3. Flask serves Angular SPA from committed dist files
4. All routes except `/api/*` serve Angular, API routes handled by Flask

## Alternative: Docker Runtime (Updated 2024)

As of 2024, you **CAN** change existing service runtime using Render Blueprints:

1. **Update render.yaml**:
   ```yaml
   services:
     - type: web
       name: ai-trading-bot
       env: docker  # Changed from python to docker
       plan: free
       # No buildCommand needed - Docker uses Dockerfile
   ```

2. **Ensure Dockerfile exists** with Node.js + Python multi-stage build

3. **Commit and deploy** - Render will switch to Docker runtime

Benefits of Docker approach:
- Builds Angular on Render (no need to commit dist files)
- Reproducible builds
- Full control over environment
- No local Node.js version issues

However, the Python runtime approach with committed dist files is simpler for basic deployments.