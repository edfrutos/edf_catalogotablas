# Soluciones para "401 Unauthorized" al hacer pull de python:3.10-slim

## Opción 1: Usar Docker en línea (Recomendado para CI/CD)

Si tienes acceso a internet pero Docker Hub no funciona:

```bash
# Limpiar credenciales viejas
docker logout
docker login

# Retry con login fresco
docker-compose build --no-cache
```

## Opción 2: Pre-descargar imagen manualmente

```bash
# En una máquina con acceso a Docker Hub
docker pull python:3.10-slim
docker save python:3.10-slim > python-3.10-slim.tar

# Transferir el archivo a la máquina sin acceso
scp python-3.10-slim.tar user@target:/tmp/

# En la máquina destino
docker load < /tmp/python-3.10-slim.tar

# Verificar
docker images | grep python
```

## Opción 3: Usar Dockerfile sin acceso a Docker Hub (Offline)

Crear un Dockerfile que funcione con imágenes locales:

```dockerfile
# Usar Alpine que ya está descargada
FROM alpine:latest

RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    libffi-dev \
    openssl-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "wsgi:app"]
```

**⚠️ Limitaciones:**
- Alpine + Python puede tener problemas con paquetes C
- Imagen más grande (~800MB vs 350MB)

## Opción 4: Usar Docker Build Cache (Sin Internet)

```bash
# Primer build (requiere internet)
DOCKER_BUILDKIT=1 docker build -t edf-catalogotablas:latest .

# Guardacache localmente
docker buildx build --cache-to type=local,dest=/tmp/cache .

# Builds posteriores sin internet (usa cache)
DOCKER_BUILDKIT=1 BUILDKIT_CACHE_TYPE=local \
  docker build --cache-from type=local,src=/tmp/cache \
  -t edf-catalogotablas:latest .
```

## Opción 5: Usar Docker Hub Offline (Enterprise/Private)

Si tienes Docker Hub privado o registry local:

```bash
# Cambiar base image en Dockerfile
FROM your-private-registry.com/python:3.10-slim

# Build con autenticación
docker build --secret type=docker,id=myauth,src=$HOME/.docker/config.json \
  -t edf-catalogotablas:latest .
```

## Opción 6: Usar imagen base más ligera (Alpine)

```bash
# Modificar Dockerfile para usar Alpine
# FROM python:3.10-alpine (si está disponible localmente)
# O esperar conexión a Docker Hub

# Alpine ya existe localmente (5.1MB descargada)
```

## ✅ Solución Recomendada para tu caso:

Dado que `alpine:latest` ya está disponible, ejecutar:

```bash
# 1. Crear Dockerfile.offline (ver abajo)
docker build -f Dockerfile.offline -t edf-catalogotablas:offline .

# 2. O esperar y retry cuando Docker Hub esté disponible
docker logout
docker login
docker-compose build --no-cache
```

## Dockerfile.offline (Funciona sin Docker Hub)

```dockerfile
FROM alpine:latest

# Instalar Python 3.10 desde Alpine repos
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    libffi-dev \
    openssl-dev \
    gcc \
    g++ \
    make \
    && ln -sf python3 /usr/bin/python

WORKDIR /app

# Copy y build wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Runtime stage
RUN adduser -D -u 1001 appuser

COPY --from=0 /wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5002/health || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5002", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]
```

## Verificar Conectividad

```bash
# Test conectar a Docker Hub
curl -I https://auth.docker.io/v2/

# Si falla: revisar proxy/firewall
curl -I --proxy [your-proxy] https://auth.docker.io/v2/

# Usar mirror de Docker Hub (China/regiones específicas)
docker pull mirror.gcr.io/library/python:3.10-slim
```

## Para CI/CD (GitHub Actions, etc):

En GitHub Actions, las imágenes se descargan automáticamente sin login:

```yaml
- name: Build Docker image
  run: docker build -t edf-catalogotablas:latest .
  # GitHub proporciona acceso a Docker Hub automáticamente
```

---

**¿Cuál prefieres?** Recomiendo Opción 1 (login fresco) o Opción 6 (Alpine local).
