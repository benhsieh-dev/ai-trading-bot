## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Build and run the application
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Option 2: Docker Commands
```bash
# Build the Docker image
docker build -t ai-trading-bot .

# Run the container
docker run -p 5001:5001 --name trading-bot ai-trading-bot

# Run in background
docker run -d -p 5001:5001 --name trading-bot ai-trading-bot

# View logs
docker logs trading-bot

# Stop and remove container
docker stop trading-bot && docker rm trading-bot
```

## 🔧 Configuration

### Environment Variables
Set these in `docker-compose.yml` or pass with `-e`:

```bash
# Basic configuration
PORT=5001                    # App port
FLASK_ENV=production        # Flask environment

# Trading API (optional for demo)
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret

# Database (optional)
MONGODB_URI=mongodb://username:password@host:port/database
```

### With API Keys
```bash
docker run -p 5001:5001 \
  -e ALPACA_API_KEY="your_key" \
  -e ALPACA_API_SECRET="your_secret" \
  ai-trading-bot
```

## 📋 Docker Commands Cheat Sheet

### Building
```bash
docker build -t ai-trading-bot .              # Build image
docker build --no-cache -t ai-trading-bot .   # Build without cache
```

### Running
```bash
docker run -p 5001:5001 ai-trading-bot        # Run interactively
docker run -d -p 5001:5001 ai-trading-bot     # Run in background
docker run --rm -p 5001:5001 ai-trading-bot   # Auto-remove when stopped
```

### Managing
```bash
docker ps                          # List running containers
docker ps -a                       # List all containers
docker images                      # List images
docker logs trading-bot            # View container logs
docker exec -it trading-bot bash   # Shell into container
```

### Cleanup
```bash
docker stop trading-bot            # Stop container
docker rm trading-bot              # Remove container
docker rmi ai-trading-bot          # Remove image
docker system prune               # Clean up unused resources
```

## 🏗️ Docker vs Render Comparison

| Feature | Docker | Render |
|---------|--------|--------|
| **Control** | Full control over environment | Managed platform |
| **Cost** | Free (self-hosted) | $7-25/month |
| **Setup** | Manual server/hosting | Automatic |
| **Scaling** | Manual | Automatic |
| **Maintenance** | You manage | Platform managed |
| **Learning** | High (DevOps skills) | Low (just deploy) |


### Basic Container
```bash
# Build and run the basic container
docker build -t trading-bot-v1 .
docker run -p 5001:5001 trading-bot-v1
```
Open http://localhost:5001 and test the app!

### Environment Variables
```bash
# Run with custom port
docker run -p 8080:8080 -e PORT=8080 trading-bot-v1
```
Open http://localhost:8080

### Volume Mounting
```bash
# Mount logs directory
docker run -p 5001:5001 -v ./logs:/app/logs trading-bot-v1
```

### Docker Compose
```bash
# Use docker-compose for easy management
docker-compose up --build
```

