# 🐳 AI Audio Pipeline - Docker Setup

This directory contains the Docker configuration for running the AI Audio Pipeline in containers.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for the container
- 10GB+ disk space for models and dependencies

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Option 2: Using Docker directly

```bash
# Build the image
docker build -t ai-audio-pipeline .

# Run the container
docker run -d \
  --name ai-audio-pipeline \
  -p 5000:5000 \
  -v ai_model_cache:/root/.cache/huggingface \
  ai-audio-pipeline
  


# View logs
docker logs -f ai-audio-pipeline

# Stop the container
docker stop ai-audio-pipeline
docker rm ai-audio-pipeline
```

## 🌐 Access the Application

Once running, access the web interface at:
- **Local**: http://localhost:5000
- **Network**: http://[your-docker-host-ip]:5000

## 🔧 Configuration

### Environment Variables

You can customize the behavior with environment variables in `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=production
  - WHISPER_MODEL=openai/whisper-base  # Change model size
  - LANGUAGE_MODEL=microsoft/DialoGPT-medium
  - CUDA_VISIBLE_DEVICES=0  # Specify GPU
```

### GPU Support (NVIDIA)

To enable GPU acceleration:

1. Install [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Uncomment the GPU section in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Rebuild and restart:
```bash
docker-compose down
docker-compose up --build
```

### Volume Mounts

- `model_cache`: Persistent storage for Hugging Face models (prevents re-downloading)
- `./temp`: Temporary audio files (optional, maps to host directory)

## 📊 Monitoring

### Health Checks
The container includes health checks that verify the service is running:

```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:5000/health
```

### Resource Usage
Monitor container resource usage:

```bash
# View resource usage
docker stats ai-audio-pipeline

# View detailed container info
docker inspect ai-audio-pipeline
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Out of Memory
If the container runs out of memory:
```bash
# Increase Docker memory limit (Docker Desktop)
# Or add memory limits to docker-compose.yml:
mem_limit: 8g
```

#### 2. Models Not Loading
```bash
# Check logs for download progress
docker-compose logs -f

# Clear model cache and restart
docker volume rm ai-audio-pipeline_model_cache
docker-compose up --build
```

#### 3. Empty Response / Server Not Responding
If you get "Empty reply from server" or "ERR_EMPTY_RESPONSE":

```bash
# Check if container is running
docker ps

# Check container logs
docker logs ai-audio-pipeline

# If container exited, check why
docker ps -a
docker logs ai-audio-pipeline

# Common fixes:
# 1. Container name conflict - remove old container
docker rm ai-audio-pipeline
docker-compose up -d

# 2. Wait for models to load (first run takes 5-10 minutes)
docker logs ai-audio-pipeline -f

# 3. Test health endpoint when ready
curl http://localhost:5000/health
```

**Note**: The first startup takes 5-10 minutes as AI models (2-3GB) are downloaded and loaded into memory.

#### 4. Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

#### 5. Audio Issues
The container doesn't need host audio devices since it processes uploaded files.
Audio playback happens in the web browser, not the container.

### Performance Optimization

#### For CPU-only systems:
```yaml
# In docker-compose.yml, add:
environment:
  - TORCH_NUM_THREADS=4
  - OMP_NUM_THREADS=4
```

#### For GPU systems:
```yaml
# Ensure GPU support is properly configured
environment:
  - CUDA_VISIBLE_DEVICES=0
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build
```

### Cleaning Up
```bash
# Remove containers and images
docker-compose down --rmi all

# Remove volumes (this will delete cached models!)
docker-compose down -v

# Clean up Docker system
docker system prune
```

## 📁 File Structure

```
/
├── Dockerfile              # Main container definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Files to exclude from build
├── requirements.txt        # Python dependencies
├── app.py                 # Main application
├── templates/             # Web UI templates
└── temp/                  # Temporary files (mounted)
```

## 🚀 Production Deployment

For production deployments, consider:

1. **Reverse Proxy**: Use nginx or traefik
2. **SSL/TLS**: Add HTTPS support
3. **Scaling**: Use Docker Swarm or Kubernetes
4. **Monitoring**: Add Prometheus/Grafana
5. **Backup**: Regular backups of model cache volume

### Example with Nginx
```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - ai-audio-pipeline
```

## 📝 Notes

- First run will take longer as models are downloaded (~2-3GB)
- Models are cached in a Docker volume for subsequent runs
- The application runs as root inside the container for simplicity
- For production, consider creating a non-root user
- Container logs include model loading progress and any errors
