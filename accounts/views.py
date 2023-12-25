from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.http import Http404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from accounts.models import User
from accounts.serializers import UserSerializer
from accounts.permissions import IsPostOrIsAuthenticated


# User 설정 관련 API
class UserAPIView(generics.RetrieveUpdateDestroyAPIView,
                  generics.CreateAPIView):
    permission_classes = [IsPostOrIsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return self.blacklisted_token(response)
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.blacklisted_token(response)
    
    def blacklisted_token(self, response):
        # JWT 토큰 삭제 후 재로그인 유도
        response.delete_cookie("refresh")
        response.delete_cookie("access")
        try:
            refresh_token = self.request.COOKIES["refresh"]
            RefreshToken(refresh_token).blacklist()
        except Exception as e:
            pass
        return response


# Email 인증을 위한 End-Point
class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            user = self.get_user(uidb64)
            self.verify_token(user, token)
            return Response({"detail": f"{user.username}님의 이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)

        except (ValueError, Http404):
            return Response({"detail": "잘못된 URL 입니다."}, status=status.HTTP_400_BAD_REQUEST)

    def get_user(self, uidb64):
        uid = force_str(urlsafe_base64_decode(uidb64))
        return get_object_or_404(User, pk=uid)

    # Token 검증
    def verify_token(self, user, token):
        if not default_token_generator.check_token(user, token):
            raise Http404()
        user.is_active = True
        user.save()


class LoginAPIView(TokenObtainPairView):
    # TokenViewBase 의 response 는 refresh, access 토큰 정보를 반환하기 때문에
    # "login success" 로 바꾸고 토큰은 쿠키에 담아서 응답.
    def post(self, request: Request, *args, **kwargs) -> Response:
        res = super().post(request, *args, **kwargs)
        
        response = Response({"detail": "login success"}, status= status.HTTP_200_OK)
        response.set_cookie("refresh", res.data.get('refresh', None), httponly= True)
        response.set_cookie("access", res.data.get('access', None), httponly= True)

        return response

    
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        refresh_token = request.COOKIES.get('refresh', '토큰이 업서용')
        data = {"refresh": refresh_token}
        serializer = self.get_serializer(data= data)

        try:
            serializer.is_valid(raise_exception= True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data
        response = Response({"detail": "refresh success"}, status= status.HTTP_200_OK)
        response.set_cookie("refresh", token['refresh'], httponly= True)
        response.set_cookie("access", token['access'], httponly= True)

        return response


class LogoutAPIView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request: Request, *args, **kwargs) -> Response:
        refresh_token = request.COOKIES.get('refresh', '토큰이 업서용')
        data = {"refresh": str(refresh_token)}
        serializer = self.get_serializer(data= data)

        try:
            serializer.is_valid(raise_exception= True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response({"detail": "token blacklisted"}, status= status.HTTP_200_OK)
        response.delete_cookie("refresh")
        response.delete_cookie("access")

        return response

