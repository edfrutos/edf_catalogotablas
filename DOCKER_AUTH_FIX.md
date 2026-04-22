# Solución: "401 Unauthorized" - Docker Hub Authentication

## Error Común

```
Error response from daemon: authentication required - incorrect username or password
× Image mongo:7.0-alpine Error authentication required - incorrect username or password
! Image redis:7-alpine   Interrupted
```

## ✅ Solución Rápida (Recomendada)

### Usa docker-compose.no-auth.yml

Este archivo usa imágenes `latest` que NO requieren autenticación:

```bash
cd /Volumes/ESSAGER/__01.-Proyectos/edf_catalogotablas

# Usa el compose alternativo (sin versiones específicas)
docker-compose -f docker-compose.no-auth.yml up -d

# Verifica que funcionan
docker-compose -f docker-compose.no-auth.yml logs -f app
```

**Ventajas:**
- ✅ Imágenes `latest` generalmente ya están cacheadas localmente
- ✅ No requiere autenticación explícita
- ✅ Funciona incluso sin Docker Hub access

---

## Alternativa A: Login Fresco a Docker Hub

```bash
# 1. Logout de credenciales viejas
docker logout

# 2. Login con credenciales nuevas
docker login
# Ingresa username y password/token

# 3. Reintentar
docker-compose up -d
```

---

## Alternativa B: Descargar imágenes en máquina con acceso

En máquina **CON** acceso a Docker Hub:

```bash
docker pull mongo:7.0-alpine
docker pull redis:7-alpine
docker save mongo:7.0-alpine | gzip > mongo.tar.gz
docker save redis:7-alpine | gzip > redis.tar.gz
```

Transferir a máquina destino:
```bash
scp mongo.tar.gz redis.tar.gz user@target:/tmp/
```

En máquina destino:
```bash
docker load < /tmp/mongo.tar.gz
docker load < /tmp/redis.tar.gz
docker-compose up -d
```

---

## Alternativa C: Usar Docker Desktop Settings

1. **Docker Desktop → Preferences**
2. **Advanced → Check "Use the default Docker socket"**
3. **Sign Out → Sign In nuevamente**
4. Reintentar: `docker-compose up -d`

---

## Alternativa D: Usar registro proxy

Si tu empresa tiene un registry proxy:

```yaml
# En docker-compose.yml, cambiar:
# mongo:7.0-alpine → your-registry.com/mongo:7.0-alpine
# redis:7-alpine → your-registry.com/redis:7-alpine
```

---

## Verificación

```bash
# Ver imágenes disponibles localmente
docker images | grep -E "mongo|redis"

# Si faltan, intentar pull directo
docker pull mongo:latest
docker pull redis:latest

# Luego:
docker-compose -f docker-compose.no-auth.yml up -d
```

---

## Recomendación Final

**Usa:** `docker-compose.no-auth.yml`

Este archivo está optimizado para funcionar sin requerir autenticación de Docker Hub, usando imágenes `latest` que suelen estar cacheadas.
