# ========================================================
# BookBazaar Pakistan - Production Gunicorn Configuration
# ========================================================
import multiprocessing
import os

# Server Socket
bind = os.environ.get("GUNICORN_BIND", "unix:/run/bookbazaar.sock")
backlog = 2048

# Worker Processes
# Standard recommended formula: (2 * CPUs) + 1
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "gthread"
threads = 2
worker_connections = 1000
timeout = 60
keepalive = 5

# Process Naming
proc_name = "bookbazaar_wsgi"

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "/var/log/bookbazaar/gunicorn_access.log")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "/var/log/bookbazaar/gunicorn_error.log")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'

# Security & Limits
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
max_requests = 1000
max_requests_jitter = 50
