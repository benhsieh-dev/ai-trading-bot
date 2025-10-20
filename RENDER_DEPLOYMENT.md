# Deploying Flask + Angular App to Render.com

This document outlines the proper way to deploy a Flask backend with Angular frontend to Render.com.

## ✅ Recommended Solution: Docker Runtime (2024)

**UPDATE**: As of 2024, Render supports changing service runtime via Blueprints. Docker deployment is now the recommended approach.

## Docker Runtime Setup (Recommended)

### Key Steps:

1. **Create Dockerfile** with Node.js + Python multi-stage build:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   
   # Install Node.js
   RUN apt-get update && apt-get install -y \
       gcc g++ curl \
       && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
       && apt-get install -y nodejs \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy and install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY frontend/package*.json frontend/
   RUN cd frontend && npm install
   
   # Copy code and build Angular
   COPY . .
   RUN cd frontend && npm run build
   
   # Create non-root user
   RUN useradd --create-home --shell /bin/bash appuser && \
       chown -R appuser:appuser /app
   USER appuser
   
   EXPOSE $PORT
   CMD ["python", "app.py"]
   ```

2. **Configure Flask to serve Angular**
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

3. **Configure render.yaml for Docker runtime**
   ```yaml
   services:
     - type: web
       name: ai-trading-bot
       env: docker  # Use Docker runtime
       plan: free
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

4. **Deploy to Render**
   ```bash
   git add .
   git commit -m "Add Docker deployment setup"
   git push
   ```

## Docker Deployment Benefits:

- **Builds Angular on Render**: No need to commit dist files or manage local Node.js versions
- **Reproducible builds**: Guaranteed consistent environment
- **Runtime flexibility**: Can change service runtime via Blueprints (2024 feature)
- **Full environment control**: Install any OS packages needed
- **Clean separation**: Development uses gitignored dist/, production builds fresh

## Deployment Flow:

1. Push code to GitHub → Render pulls → Docker builds image
2. Docker installs Node.js → builds Angular → installs Python deps
3. Flask serves Angular SPA from container's built files
4. All routes except `/api/*` serve Angular, API routes handled by Flask

## Legacy: Python Runtime with Committed Dist Files

For reference, the previous approach using Python runtime:

### Issues with Python Runtime:
- **Custom buildCommand ignored**: Render always runs `pip install -r requirements.txt`
- **No Node.js available**: Cannot build Angular during deployment
- **Requires local build**: Must commit dist files to git
- **Local Node.js dependency**: Need compatible Node.js version locally

### Python Runtime Process:
1. Build Angular locally → commit dist files → push to GitHub
2. Render runs `pip install -r requirements.txt` → starts Flask
3. Flask serves Angular from committed dist files

**Recommendation**: Use Docker runtime instead for cleaner, more reliable deployments.