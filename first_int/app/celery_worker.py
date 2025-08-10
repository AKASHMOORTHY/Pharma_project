import sys
from app.tasks.celery_utils import celery_app


if __name__ == "__main__":
    celery_app.worker_main()



# Start Celery worker
# celery -A app.celery_worker.celery_app worker --loglevel=info
# celery -A app.celery_worker.celery_app worker --pool=solo --loglevel=info

# Start Celery beat (scheduler)
# celery -A app.celery_worker.celery_app beat --loglevel=info
