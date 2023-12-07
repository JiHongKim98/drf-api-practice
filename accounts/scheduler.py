from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from django.db import transaction
from django.conf import settings
from django.utils import timezone


# This is the function you want to schedule - add as many as you want and then register them in the start() function below
# 기간이 지난 jwt 토큰을 삭제하는 메소드
@transaction.atomic
def clean_expiry_token():
    now_date = timezone.now()
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt= now_date)
    print(f"기간 지난 refresh 토큰 수 => {len(expired_tokens)}")

    if expired_tokens != 0:
        for instance in expired_tokens:
            token_id = instance.id

            try:
                blacklist_instance= BlacklistedToken.objects.get(id= token_id)
                blacklist_instance.delete()

            except:
                pass

            instance.delete()


def start():
    # 1시간마다 기간지난 토큰을 삭제하는 스케쥴
    job_id = 'clean_expiry_jwt'

    scheduler = BackgroundScheduler(timezone= settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # django scheduler 이벤트 등록
    register_events(scheduler)
    
    try:
        scheduler.start()
        # replace_existing => djangojob 에 중복 저장 막기
        scheduler.add_job(clean_expiry_token, 'cron', hour='*/1', id=job_id, jobstore='default', replace_existing=True)
        print("Scheduler started...")

    except Exception as e:
        print(e)
        scheduler.shutdown()

