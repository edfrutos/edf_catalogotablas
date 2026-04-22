# Docker Setup - EDF Catálogo de Tablas

## Requisitos Previos

- Docker 20.10+
- Docker Compose 2.0+
- Mínimo 2GB RAM disponible
- Puerto 5002 disponible (aplicación)
- Puerto 27017 disponible (MongoDB)
- Puerto 6379 disponible (Redis)

## Quick Start

### 1. Configurar Variables de Entorno

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tus valores
nano .env
```

**Variables requeridas:**
```env
SECRET_KEY=your_secure_key_here_minimum_32_chars
MONGO_ROOT_PASSWORD=your_mongodb_password
REDIS_PASSWORD=your_redis_password
```

**Generar SECRET_KEY segura:**
```bash
openssl rand -base64 32
```

### 2. Construir la Imagen

```bash
# Opción A: Usar script helper (recomendado)
./build-docker.sh latest
# Este script detecta si Docker Hub está disponible
# Si no: sugiere build con Alpine (offline)

# Opción B: Build con docker-compose (requiere Docker Hub)
docker-compose build

# Opción C: Build manual con Dockerfile estándar
docker build -t edf-catalogotablas:latest .

# Opción D: Build con Alpine si no tienes acceso a Docker Hub
docker build -f Dockerfile.alpine -t edf-catalogotablas:alpine .
```

**⚠️ Si ves "401 Unauthorized" en Docker Hub:**
- Lee [DOCKER_OFFLINE.md](./DOCKER_OFFLINE.md) para soluciones
- Opción rápida: `docker build -f Dockerfile.alpine ...`
```

### 3. Iniciar los Contenedores

```bash
# Desarrollo (con logs en tiempo real)
docker-compose up

# Producción (en background)
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

### 4. Verificar que Todo Funciona

```bash
# Esperar ~30 segundos a que MongoDB y Redis estén listos

# Verificar health check
curl -v http://localhost:5002/health

# Ver logs de la app
docker-compose logs app

# Verificar MongoDB
docker exec edf_catalogotablas_mongodb mongosh -u admin -p $MONGO_ROOT_PASSWORD

# Verificar Redis
docker exec edf_catalogotablas_redis redis-cli PING
```

## Uso en Desarrollo

### Hot Reload (Desarrollo)

Para desarrollo con cambios automáticos:

```bash
# Modificar docker-compose.yml para usar development:
FLASK_ENV=development docker-compose up
```

Luego añadir a docker-compose.yml en el servicio `app`:
```yaml
command: flask --app wsgi run --host 0.0.0.0 --port 5002
volumes:
  - .:/app  # Bind mount para hot reload
```

### Entrar a la Shell del Contenedor

```bash
# Acceso root
docker-compose exec app bash

# Como usuario appuser
docker-compose exec -u appuser app bash
```

### Ejecutar Comandos

```bash
# Tests
docker-compose exec app pytest

# Migraciones (si las hay)
docker-compose exec app python manage.py migrate

# Shell interactivo
docker-compose exec app python
```

## Producción

### Variables de Entorno Críticas

```env
FLASK_ENV=production
SECRET_KEY=<generada con openssl rand -base64 32>
MONGO_ROOT_PASSWORD=<contraseña fuerte>
REDIS_PASSWORD=<contraseña fuerte>
```

### Verificaciones Pre-Deploy

```bash
# Verificar que no hay errores en la imagen
docker build -t edf-catalogotablas:prod . && \
docker run --rm edf-catalogotablas:prod python -m py_compile wsgi.py

# Verificar health check
docker-compose up -d && sleep 40 && \
curl -v http://localhost:5002/health || echo "Health check failed"
```

### Escalado

```bash
# Aumentar workers de Gunicorn en Dockerfile
CMD ["gunicorn", "--workers", "8", ...]

# O en docker-compose.yml
environment:
  GUNICORN_WORKERS: 8
```

## Backup y Restauración

### Backup de MongoDB

```bash
# Crear backup
docker-compose exec mongodb mongodump \
  --username admin \
  --password $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin \
  --out /backup

# Extraer del contenedor
docker cp edf_catalogotablas_mongodb:/backup ./mongodb_backup
```

### Restore de MongoDB

```bash
# Copiar backup al contenedor
docker cp ./mongodb_backup edf_catalogotablas_mongodb:/backup

# Restaurar
docker-compose exec mongodb mongorestore \
  --username admin \
  --password $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin \
  /backup
```

### Backup de Redis

```bash
# Copiar archivo dump.rdb
docker cp edf_catalogotablas_redis:/data/dump.rdb ./redis_backup.rdb

# Restaurar
docker cp ./redis_backup.rdb edf_catalogotablas_redis:/data/dump.rdb
```

## Troubleshooting

### Contenedor no arranca

```bash
# Ver logs detallados
docker-compose logs app

# Verificar que SECRET_KEY está set
docker-compose config | grep SECRET_KEY

# Reiniciar contenedor
docker-compose restart app
```

### MongoDB no responde

```bash
# Verificar conectividad
docker-compose exec app \
  mongosh -u admin -p $MONGO_ROOT_PASSWORD mongodb:27017/edf_catalogotablas

# Reiniciar MongoDB
docker-compose restart mongodb
```

### Redis no responde

```bash
# Verificar conectividad
docker-compose exec app redis-cli -h redis ping

# Reiniciar Redis
docker-compose restart redis
```

### Problemas de permisos

```bash
# Fix: Set correct ownership en volúmenes
docker-compose exec app chown -R appuser:appuser /app/uploads /app/logs

# Crear directorios si no existen
mkdir -p app/static/uploads logs data
```

## Limpieza

### Parar contenedores

```bash
docker-compose down
```

### Parar y eliminar volúmenes (⚠️ Cuidado - borra datos)

```bash
docker-compose down -v
```

### Eliminar imagen

```bash
docker rmi edf-catalogotablas:latest
```

## Seguridad

- ✅ No hay credenciales en el código
- ✅ Usuario no-root (appuser:1001)
- ✅ SECRET_KEY obligatorio en producción (>32 chars)
- ✅ Headers de seguridad activados
- ✅ Health checks configurados
- ✅ Logs centralizados

## Redes

Los contenedores se comunican en red `edf_network`:
- `mongodb:27017` — accesible como `mongodb` desde `app`
- `redis:6379` — accesible como `redis` desde `app`

## Recursos

- **RAM**: ~800MB (app) + 500MB (MongoDB) + 100MB (Redis) = ~1.4GB
- **Disk**: ~2-3GB (imagen compilada + datos)
- **CPU**: Sin límite (ajustable en docker-compose.yml si es necesario)

## Referencias

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [MongoDB Docker](https://hub.docker.com/_/mongo)
- [Redis Docker](https://hub.docker.com/_/redis)
- [Flask + Gunicorn](https://flask.palletsprojects.com/en/latest/deploying/wsgi-standalone/)
