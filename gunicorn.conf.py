import os
base_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(base_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

errorlog = os.path.join(logs_dir, "gunicorn_error.log")
accesslog = os.path.join(logs_dir, "gunicorn_access.log")
workers = 1  # Solo 1 worker para depuración de sesión