import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")

@app.task  # an example task
def test_app_task():
    print('test_app_task has run')
    return

app.autodiscover_tasks()