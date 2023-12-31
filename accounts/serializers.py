from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.models import User
from accounts.tasks import send_verification_mail
from accounts.utils import decode_uid, encode_uid


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "username", "fullname")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self._send_verification_email(user)
        return user

    # Celery-Worker로 Email 전송 Task 전달
    def _send_verification_email(self, user):
        uid = encode_uid(user.id)
        token = default_token_generator.make_token(user)
        verification_url = (
            f"http://localhost:8000/api/v1/accounts/activate/{uid}/{token}"
        )
        send_verification_mail.delay(user.username, user.email, verification_url)

    # 비밀번호는 hashing하고 저장
    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data) -> User:
        uid = decode_uid(data["uidb64"])
        user = get_object_or_404(User, pk=uid)

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("잘못된 토큰입니다.")

        data["user"] = user
        return data
