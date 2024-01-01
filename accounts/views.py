from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts import schemas
from accounts.authentication import JWTCookieAuthentication
from accounts.mixin import JWTCookieHandlerMixin
from accounts.permissions import IsPostOrIsAuthenticated
from accounts.serializers import EmailVerificationSerializer, UserSerializer


@extend_schema(tags=["user"])
@extend_schema_view(post=extend_schema(auth=[]))
class UserAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    """
    request를 보낸 사용자 리소스에 대한 CRUD API
    """

    permission_classes = [IsPostOrIsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return self.blacklisted_token(response)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.blacklisted_token(response)

    def blacklisted_token(self, response: Response) -> Response:
        # JWT 인증 토큰 초기화
        refresh = self.request.COOKIES.get("refresh", None)
        if refresh:
            RefreshToken(refresh).blacklist()

        response.delete_cookie("refresh")
        response.delete_cookie("access")

        return response


class LoginAPIView(JWTCookieHandlerMixin, TokenObtainPairView):
    """
    사용자 인증을 위한 HttpOnly 속성의 access, refresh 토큰 발급 API
    """

    @extend_schema(
        responses={200: schemas.SuccessResponseSerializer},
        request=None,
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.perform_serializer(data=request.data)
        return self.set_cookie_response(**serializer.validated_data)


class CustomTokenRefreshView(JWTCookieHandlerMixin, TokenRefreshView):
    """
    refresh 토큰을 통해 새로운 HttpOnly 속성의 access 토큰 발급 API
    """

    @extend_schema(
        responses={200: schemas.SuccessResponseSerializer},
        request=None,
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        refresh = self.get_refresh_cookie(request)
        serializer = self.perform_serializer(data={"refresh": refresh})
        return self.set_cookie_response(**serializer.validated_data)


class LogoutAPIView(JWTCookieHandlerMixin, TokenBlacklistView):
    """
    쿠키에 저장된 access, refresh 토큰을 삭제하고, refresh 토큰 blacklisted API
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]

    @extend_schema(
        responses={200: schemas.SuccessResponseSerializer},
        request=None,
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        refresh = self.get_refresh_cookie(request)
        self.perform_serializer(data={"refresh": refresh})
        return self.delete_cookie_response()


class EmailVerificationView(APIView):
    """
    회원가입시 작성한 Email로 전송된 인증 링크를 통해 사용자 계정을 활성시키는 API
    """

    authentication_classes = ()

    @extend_schema(
        responses={200: schemas.EmailVerifiationSuccessSerializer},
        tags=["auth"],
        auth=[],
    )
    def get(self, request, uidb64, token):
        serializer = EmailVerificationSerializer(
            data={"uidb64": uidb64, "token": token}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.is_active = True
        user.save()

        return Response(
            {"detail": f"{user.username}님의 이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK
        )
