from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.mixin import JWTCookieHandlerMixin
from accounts.serializers import UserSerializer, EmailVerificationSerializer
from accounts.permissions import IsPostOrIsAuthenticated
from accounts.authentication import JWTCookieAuthentication


class UserAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
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
        refresh = self.request.COOKIES.get('refresh', None)
        if refresh:
            RefreshToken(refresh).blacklist()

        response.delete_cookie("refresh")
        response.delete_cookie("access")

        return response


class LoginAPIView(JWTCookieHandlerMixin, TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.perform_serializer(data= request.data)
        return self.set_cookie_response(**serializer.validated_data)


class CustomTokenRefreshView(JWTCookieHandlerMixin, TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = self.get_refresh_cookie(request)
        serializer = self.perform_serializer(data= {'refresh': refresh})
        return self.set_cookie_response(**serializer.validated_data)


class LogoutAPIView(JWTCookieHandlerMixin, TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]

    def post(self, request, *args, **kwargs):
        refresh = self.get_refresh_cookie(request)
        self.perform_serializer(data= {'refresh': refresh})
        return self.delete_cookie_response()


class EmailVerificationView(APIView):
    authentication_classes = ()

    def get(self, request, uidb64, token):
        serializer = EmailVerificationSerializer(data= {'uidb64': uidb64, 'token': token})
        serializer.is_valid(raise_exception= True)
        
        user = serializer.validated_data['user']
        user.is_active = True
        user.save()

        return Response({"detail": f"{user.username}님의 이메일 인증이 완료되었습니다."}, status= status.HTTP_200_OK)

