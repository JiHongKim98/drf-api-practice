from celery import shared_task

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from django.db import transaction
from django.utils import timezone


# 만료된 JWT를 작제하는 TASK
@shared_task
@transaction.atomic
def clean_expiry_token():
    now_date = timezone.now()
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt= now_date)
    print(f"만료된 refresh 토큰 수 => {len(expired_tokens)}")

    if expired_tokens != 0:
        for Outstand_instance in expired_tokens:
            token_id = Outstand_instance.id
            try:
                blacklist_instance= BlacklistedToken.objects.get(id= token_id)
                blacklist_instance.delete()
            except:
                pass

            Outstand_instance.delete()

