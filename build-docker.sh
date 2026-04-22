#!/bin/bash
# build-docker.sh - Build edf_catalogotablas Docker image
# Works with or without Docker Hub access

set -e

PROJECT_NAME="edf-catalogotablas"
VERSION="${1:-latest}"
DOCKERFILE="${2:-Dockerfile}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Building Docker image: $PROJECT_NAME:$VERSION                    ║"
echo "║  Using: $DOCKERFILE                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Check if we can reach Docker Hub
check_docker_hub() {
    echo -n "🔍 Checking Docker Hub connectivity... "
    if curl -s --connect-timeout 5 https://auth.docker.io/v2/ > /dev/null 2>&1; then
        echo "✅ Available"
        return 0
    else
        echo "❌ Unavailable"
        return 1
    fi
}

# Build with Dockerfile (requires Docker Hub)
build_slim() {
    echo ""
    echo "📦 Building with python:3.10-slim (requires Docker Hub)..."
    docker build -f Dockerfile \
        -t $PROJECT_NAME:$VERSION \
        -t $PROJECT_NAME:latest \
        .
    echo "✅ Build successful: $PROJECT_NAME:$VERSION"
}

# Build with Alpine (works offline)
build_alpine() {
    echo ""
    echo "📦 Building with Alpine (offline mode)..."
    docker build -f Dockerfile.alpine \
        -t $PROJECT_NAME:$VERSION-alpine \
        -t $PROJECT_NAME:alpine \
        .
    echo "✅ Build successful: $PROJECT_NAME:$VERSION-alpine"
}

# Main build logic
if check_docker_hub; then
    echo "✅ Building with standard Dockerfile (python:3.10-slim)"
    build_slim
    echo ""
    echo "Optional: Also build Alpine version"
    read -p "Build Alpine version too? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_alpine
    fi
else
    echo ""
    echo "⚠️ Docker Hub not available"
    echo ""
    read -p "Build with Alpine instead? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_alpine
        echo ""
        echo "💡 Tip: When Docker Hub is available, run:"
        echo "   ./build-docker.sh $VERSION Dockerfile"
    else
        echo "❌ Build cancelled"
        exit 1
    fi
fi

# Show image info
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Image Info:"
docker images | grep "$PROJECT_NAME"
echo ""
echo "🚀 Next steps:"
echo "   1. Configure .env file:"
echo "      cp .env.example .env"
echo "   2. Start with docker-compose:"
echo "      docker-compose up -d"
echo "   3. Verify health:"
echo "      curl http://localhost:5002/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
