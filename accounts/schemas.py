from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers


class CookieSimpleJWTScheme(SimpleJWTScheme):
    target_class = "accounts.authentication.JWTCookieAuthentication"
    name = "jwtAuth"
    priority = 0

    def get_security_definition(self, auto_schema: AutoSchema):
        return {"type": "apiKey", "in": "cookie", "name": "access"}


class SuccessResponseSerializer(serializers.Serializer):
    """
    response 에 access, refresh 토큰 정보를 포함하지 않음.
    """

    detail = serializers.CharField(default="success")


class EmailVerifiationSuccessSerializer(serializers.Serializer):
    detail = serializers.CharField(default="{user.username}님의 이메일 인증이 완료되었습니다.")
