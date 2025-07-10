import sys
from app.tasks.locking import celery

# 🧠 Correct arguments: simulate running `celery worker --loglevel=info`
sys.argv = ['worker', '--loglevel=info']

# ✅ Start Celery worker
celery.worker_main()
