import os

bind = "0.0.0.0:{}".format(os.environ.get("PORT", "3000"))
# Keep in step with start.sh (which passes these on the command line and therefore wins).
# Having the file say 3x3 while the launcher said 1x4 made the effective config depend on
# which of the two someone happened to read. One worker: the instance was OOM-killing the
# third of three, and every worker re-runs the full import-time DB bootstrap.
workers = 1
threads = 4
worker_class = "gthread"
timeout = 120
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
