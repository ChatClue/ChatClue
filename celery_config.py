from celery import Celery
from config import CELERY_CONFIG

celery_app = Celery(CELERY_CONFIG['APPLICATION_NAME'], broker=CELERY_CONFIG['BROKER_URL'])
celery_app.conf.update(CELERY_CONFIG)

def get_celery_app():
    return celery_app
