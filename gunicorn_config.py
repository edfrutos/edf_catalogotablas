# Configuración mínima sin errores de logging
bind = "127.0.0.1:8000"
workers = 1

# Logs a consola (sin archivos para evitar errores de permisos)
errorlog = "-"
accesslog = "-"
loglevel = "info"

# Configuración adicional
preload_app = True
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2