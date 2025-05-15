# Gunicorn configuration file
import multiprocessing

# Server socket
bind = '127.0.0.1:8002'
backlog = 2048

# Worker processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
raw_env = []
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/gunicorn_error.log'
loglevel = 'debug'
accesslog = '/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/gunicorn_access.log'
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = None

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def when_ready(server):
    pass

def post_fork(server, worker):
    pass

def pre_fork(server, worker):
    pass

def pre_exec(server):
    pass

def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))

def post_request(worker, req, environ, resp):
    pass

def worker_exit(server, worker):
    pass

def worker_abort(worker):
    pass

def child_exit(server, worker):
    pass
