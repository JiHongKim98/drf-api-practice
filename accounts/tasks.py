from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken
)

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.core.mail import EmailMessage


# 만료된 JWT를 작제하는 TASK
@shared_task
@transaction.atomic
def clean_expiry_token():
    now_date = timezone.now()
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt= now_date)

    if expired_tokens != 0:
        for Outstand_instance in expired_tokens:
            token_id = Outstand_instance.id

            try:
                blacklist_instance= BlacklistedToken.objects.get(id= token_id)
                blacklist_instance.delete()
            except BlacklistedToken.DoesNotExist:
                pass

            Outstand_instance.delete()


# 인증 메일을 보내는 TASK
@shared_task
def send_verification_mail(username: str, email: str, verification_url: str):
    message = f"""이메일 인증을 완료하려면 아래의 링크를 클릭하세요.\n
    URL : {verification_url}
    """

    email = EmailMessage(
        subject= f"{username}님의 이메일 인증 링크입니다.",
        body= message,
        to= [email]
    )
    email.send()

