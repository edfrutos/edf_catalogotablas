# Gunicorn configuration file
import multiprocessing
import os

# Obtener el número de núcleos de CPU disponibles
try:
    workers = multiprocessing.cpu_count() * 2 + 1
except:
    workers = 3  # Valor por defecto si no se puede determinar

# Server socket
bind = '127.0.0.1:8002'
backlog = 4096  # Número de conexiones en cola

# Worker processes
workers = workers
worker_class = 'sync'  # Considerar 'gthread' o 'gevent' para aplicaciones con E/S
worker_connections = 1000  # Solo aplica para worker_class='gevent'
threads = 4  # Solo para worker_class='gthread'
timeout = 300  # 5 minutos para operaciones largas
keepalive = 2
max_requests = 1000  # Reiniciar workers después de N peticiones para prevenir fugas de memoria
max_requests_jitter = 50  # Variabilidad en el reinicio para evitar que todos los workers se reinicien a la vez

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
loglevel = 'info'  # Reducir a 'info' en producción para menos ruido
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Forwarded-For}i)s" %(L)ss'

# Process naming
proc_name = 'edefrutos2025_gunicorn'

# Server hooks
def on_starting(server):
    """Ejecutar cuando el maestro arranca"""
    server.log.info("Iniciando servidor Gunicorn para edefrutos2025")


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
    worker.log.debug(f"Petición: {req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """Después de procesar una petición"""
    worker.log.debug(f"Respuesta: {req.method} {req.path} -> {resp.status}")


def child_exit(server, worker):
    """Cuando un worker muere"""
    server.log.warning(f"Worker {worker.pid} ha terminado con código de salida {worker.exitcode}")

# Configuración adicional para depuración
if os.environ.get('FLASK_ENV') == 'development':
    loglevel = 'debug'
    reload = True
    reload_engine = 'auto'
