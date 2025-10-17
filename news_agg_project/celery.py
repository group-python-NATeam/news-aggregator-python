import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_agg_project.settings')

app = Celery('news_agg_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
