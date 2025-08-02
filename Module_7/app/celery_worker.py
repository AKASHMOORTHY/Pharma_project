from .celery_utils import celery_app
import app.tasks.report_tasks

celery = celery_app

if __name__ == "__main__":
    celery.worker_main()


# to run:   celery -A app.celery_worker worker --loglevel=info
# celery -A app.celery_worker.celery worker --pool=solo --loglevel=info
# celery -A app.celery_worker beat --loglevel=info
# celery -A app.celery_utils.celery_app beat --loglevel=info
