from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import TokenError


class JWTCookieHandlerMixin:
    """
    HttpOnly 속성의 JWT 토큰을 통해 요청을 받거나 응답할 때 사용하기 위한 Mixin 클래스
    """

    def get_refresh_cookie(self, request: Request) -> str:
        """
        request cookie에 저장된 refresh 토큰을 반환
        """
        
        refresh = request.COOKIES.get('refresh', None)
    
        if refresh is None:
            raise InvalidToken
        
        return refresh
    
    def perform_serializer(self, *args, **kwargs) -> Serializer:
        serializer = self.get_serializer(*args, **kwargs)

        try:
            serializer.is_valid(raise_exception= True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return serializer
    
    def set_cookie_response(self, *args, **kwargs) -> Response:
        response = Response({"detail": "success"}, status= status.HTTP_200_OK)
        for key, value in kwargs.items():
            response.set_cookie(key, value, httponly=True)

        return response
    
    def delete_cookie_response(self) -> Response:
        response = Response({"detail": "success"}, status= status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

        return response

