web: gunicorn --workers 2 --threads 4 --worker-class gevent --worker-tmp-dir /dev/shm --bind 0.0.0.0:$PORT app:app
