from rest_framework import status, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer
from .permissions import IsPostOrIsAuthenticated


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

