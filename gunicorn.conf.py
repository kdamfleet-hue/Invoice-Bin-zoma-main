import os

bind = "0.0.0.0:{}".format(os.environ.get("PORT", "3000"))
workers = 3
threads = 3
worker_class = "gthread"
timeout = 120
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
