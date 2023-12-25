from rest_framework import serializers

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from accounts.tasks import send_verification_mail
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    # 클라이언트들에게 전달 x
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'fullname')

    # User 객체 생성
    # CRUD 중 Create 함수 오버라이딩
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        self._send_verification_email(user)
        return user

    # Email 전송은 Celery-Worker로 전달
    def _send_verification_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)
        verification_url = f"http://127.0.0.1:8000/api/v1/accounts/activate/{uid}/{token}"
        send_verification_mail.delay(user.username, user.email, verification_url)
    
    # Update 함수 오버라이딩
    def update(self, instance, validated_data):
        # patch 를 위해 key값이 있는 필드별로 업데이트
        for key, value in validated_data.items():
            # User 정보 수정시 비밀번호는 hashing 하여 저장해야함.
            if key == "password":
                instance.set_password(value)

            else:
                setattr(instance, key, value)

        instance.save()
        return instance
