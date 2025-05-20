# Gunicorn configuration file
import multiprocessing
import os

# Obtener el número de núcleos de CPU disponibles pero limitar el número de workers
try:
    cpu_count = multiprocessing.cpu_count()
    # Usar workers = número de CPUs + 1 para reducir el consumo de recursos
    # La fórmula anterior (2*CPUs+1) es muy intensiva en recursos
    workers = cpu_count + 1
except:
    workers = 2  # Valor por defecto más conservador

# Server socket
bind = '127.0.0.1:8002'
backlog = 2048  # Reducido para menor consumo de memoria en conexiones pendientes

# Worker processes - Configuración optimizada para menor consumo de recursos
workers = workers
worker_class = 'gthread'  # gthread ofrece mejor rendimiento con menos recursos que sync
worker_connections = 500  # Reducido para menor consumo de memoria
threads = 2  # Reducido para menor carga de CPU
timeout = 180  # 3 minutos para operaciones, balance entre rendimiento y recursos
keepalive = 2
max_requests = 1500  # Incrementado para reducir la frecuencia de reinicio de workers
max_requests_jitter = 100  # Mayor variabilidad para distribuir mejor los reinicios
# Agregar configuración para limitar uso de memoria
worker_tmp_dir = '/dev/shm'  # Usar RAM para archivos temporales mejora rendimiento
# Limitar la memoria a usar por worker (soft limit en MB)
worker_max_memory_per_child = 150  # Reinicia workers que superen este límite

# Server mechanics
daemon = False
raw_env = [
    'PYTHONPATH=/var/www/vhosts/edefrutos2025.xyz/httpdocs',
    'FLASK_APP=wsgi.py',
    'FLASK_ENV=production'
]
pidfile = '/var/www/vhosts/edefrutos2025.xyz/tmp/gunicorn.pid'
umask = 0o002  # Permisos de archivo: 775 para directorios, 664 para archivos
user = 'www-data'
group = 'www-data'
tmp_upload_dir = '/var/www/vhosts/edefrutos2025.xyz/tmp/uploads'

# Logging
log_dir = '/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

errorlog = os.path.join(log_dir, 'gunicorn_error.log')
accesslog = os.path.join(log_dir, 'gunicorn_access.log')
loglevel = 'warning'  # Reducido a 'warning' para disminuir I/O de disco y tamaño de logs
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Forwarded-For}i)s" %(L)ss'

# Process naming
proc_name = 'edefrutos2025_gunicorn'

# Server hooks optimizados
def on_starting(server):
    """Ejecutar cuando el maestro arranca"""
    server.log.info("Iniciando servidor Gunicorn para edefrutos2025")
    # Establecer límites de sistema para el proceso
    import resource
    # Limitar el número de archivos abiertos (evita fugas de recursos)
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
    # Limitar el uso de memoria virtual (en bytes, 350MB)
    resource.setrlimit(resource.RLIMIT_AS, (350 * 1024 * 1024, 400 * 1024 * 1024))


def when_ready(server):
    """Ejecutar cuando los workers están listos"""
    server.log.info(f"Workers listos. Sirviendo en {bind}")


def post_fork(server, worker):
    """Después de que un worker se ha bifurcado"""
    server.log.info(f"Worker {worker.pid} iniciado")


def worker_int(worker):
    """Cuando un worker recibe una señal de interrupción"""
    worker.log.info("Worker recibió señal de interrupción")


def worker_abort(worker):
    """Cuando un worker es abortado"""
    worker.log.warning("Worker abortado")


def pre_request(worker, req):
    """Antes de procesar una petición"""
    # Solo registrar en modo debug para reducir I/O
    if os.environ.get('FLASK_ENV') == 'development':
        worker.log.debug(f"Petición: {req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """Después de procesar una petición"""
    # Solo registrar en modo debug para reducir I/O
    if os.environ.get('FLASK_ENV') == 'development':
        worker.log.debug(f"Respuesta: {req.method} {req.path} -> {resp.status}")


def child_exit(server, worker):
    """Cuando un worker muere"""
    server.log.warning(f"Worker {worker.pid} ha terminado con código de salida {worker.exitcode}")

# Configuración adicional para depuración
if os.environ.get('FLASK_ENV') == 'development':
    loglevel = 'debug'
    reload = True
    reload_engine = 'auto'
