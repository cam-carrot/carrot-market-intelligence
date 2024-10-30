import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"  # Use environment PORT or default to 5000
backlog = 2048

# Worker processes
workers = 2
worker_class = "gevent"  # Changed from aiohttp to gevent
threads = 4
worker_connections = 1000
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "market_analyzer"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Maximum requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Preload app code before forking workers
preload_app = True

# Timeout configuration
graceful_timeout = 30
keepalive = 2

def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    pass

def on_reload(server):
    """Called before code is reloaded."""
    pass