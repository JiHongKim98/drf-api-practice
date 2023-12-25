from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')

# namespace => 'CELERY'는 settings.py 에서
# celery관련 설정들은 모두 'CELERY_' 로 시작함을 알려주는 것
app.config_from_object("django.conf:settings", namespace='CELERY')

# 프로젝트에서 shared_task로 된 모든 작업을 가져옴
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

