# Docker Build Instructions - edf_catalogotablas

## Building the Docker Image

### Prerequisites
- Docker 20.10+ installed
- Docker Hub access or local Docker daemon
- ~4GB free disk space for the build

### Build Commands

#### Option 1: Using docker-compose (Recommended)

```bash
cd /Volumes/ESSAGER/__01.-Proyectos/edf_catalogotablas

# Configure environment
cp .env.example .env
# Edit .env with your values (SECRET_KEY, MONGO_ROOT_PASSWORD, etc)

# Build and start all services
docker-compose up --build

# Or build only
docker-compose build
```

#### Option 2: Manual Docker Build

```bash
cd /Volumes/ESSAGER/__01.-Proyectos/edf_catalogotablas

# Build the image
docker build -t edf-catalogotablas:latest \
  --build-arg APP_ENV=production \
  .

# Tag for registry
docker tag edf-catalogotablas:latest edfrutos/edf-catalogotablas:latest
```

#### Option 3: Build with Buildx (Multi-platform)

```bash
# Create builder
docker buildx create --name edf-builder

# Build for multiple platforms
docker buildx build --builder edf-builder \
  -t edfrutos/edf-catalogotablas:latest \
  --platform linux/amd64,linux/arm64 \
  --push .
```

### Build Details

#### What the Dockerfile Does

1. **Stage 1 (Builder)**
   - Uses `python:3.10-slim` base image
   - Installs build dependencies (gcc, make, libssl-dev, etc)
   - Compiles all Python wheels from requirements.txt
   - Total: ~800MB intermediate image

2. **Stage 2 (Runtime)**
   - Uses clean `python:3.10-slim` base
   - Installs only runtime dependencies (curl)
   - Copies pre-compiled wheels from builder
   - Creates non-root user `appuser` (UID 1001)
   - Sets up health check
   - Final image: ~350-400MB

#### Build Arguments

```dockerfile
ARG APP_ENV=production    # Set to 'development' for dev builds
```

### Verifying the Build

After building, verify the image:

```bash
# Check image size
docker images edf-catalogotablas

# Test the image
docker run --rm edf-catalogotablas:latest --version

# Test with environment (requires mongoDB running)
docker run --rm \
  -e SECRET_KEY="test-secret-key-12345" \
  -e MONGO_URI="mongodb://localhost:27017/test" \
  edf-catalogotablas:latest \
  python -m py_compile wsgi.py
```

### Troubleshooting Build Failures

#### "Failed to fetch oauth token"
- Docker Hub authentication issue
- Solution: `docker logout && docker login`
- Or use local build without pushing to registry

#### "build-essential not found"
- Should not occur with python:3.10-slim
- If it does: Check apt cache is updated
- The Dockerfile already includes `apt-get update && apt-get install -y build-essential`

#### "ImportError: No module named..."
- A dependency is missing from requirements.txt
- Verify all imports in Python files are in requirements.txt
- Check for new packages added to the project

#### Build takes >10 minutes
- First build compiles all wheels (expected: 5-7 minutes)
- Subsequent builds use cache (expected: <1 minute)
- To disable cache: `docker build --no-cache`

### CI/CD Build Pipeline

For GitHub Actions automated builds:

```yaml
name: Docker Build & Push

on:
  push:
    branches: [ main ]
    tags: [ v* ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: edfrutos/edf-catalogotablas:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

### Image Registry

#### Docker Hub

```bash
# Tag
docker tag edf-catalogotablas:latest edfrutos/edf-catalogotablas:latest

# Push
docker push edfrutos/edf-catalogotablas:latest

# Pull for deployment
docker pull edfrutos/edf-catalogotablas:latest
```

#### GitHub Container Registry

```bash
# Tag
docker tag edf-catalogotablas:latest ghcr.io/edfrutos/edf-catalogotablas:latest

# Login
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u edfrutos --password-stdin

# Push
docker push ghcr.io/edfrutos/edf-catalogotablas:latest
```

### Performance Optimization

#### Reduce Image Size

```bash
# Current: ~350-400MB
# Strategies:
# 1. Use python:3.10-alpine instead of slim (~180MB)
#    Risk: Some packages may not compile on Alpine
# 
# 2. Remove development dependencies
#    Already done: --no-deps --wheel-dir
#
# 3. Strip compiled files
#    find /usr/local/lib/python* -type d -name __pycache__ -exec rm -rf {} +
```

#### Cache Optimization

```dockerfile
# Order in Dockerfile matters for layer caching
# 1. FROM (least changed)
# 2. RUN apt-get
# 3. COPY requirements.txt (more stable than code)
# 4. RUN pip install (most time-consuming, cached well)
# 5. COPY . (most frequently changed, should be last)
```

### Security Scanning

```bash
# Scan with Trivy (vulnerability scanner)
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image edf-catalogotablas:latest

# Scan with Grype
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  anchore/grype:latest edf-catalogotablas:latest
```

### Deployment

Once built and pushed, deploy with:

```bash
# Using docker-compose
docker-compose pull
docker-compose up -d

# Using docker run directly
docker run -d \
  -e SECRET_KEY="your_secret_key" \
  -e MONGO_URI="mongodb://mongodb:27017/edf_catalogotablas" \
  -p 5002:5002 \
  --name edf-app \
  edfrutos/edf-catalogotablas:latest

# Using Kubernetes
kubectl apply -f edf-catalogotablas-deployment.yaml
```

---

See [DOCKER.md](./DOCKER.md) for full Docker usage instructions.
