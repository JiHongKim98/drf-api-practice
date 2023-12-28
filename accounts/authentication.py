from rest_framework.request import Request

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    access, refresh 토큰을 HttpOnly 속성으로 발급하도록 구현하여
    request Cookie에서 먼저 access 토큰을 검사함.
    만약 없을 경우 기존과 같이 header를 검사함.
    """

    def get_access_cookie(self, request: Request) -> bytes|None:
        access = request.COOKIES.get('access', None)

        if isinstance(access, str):
            access = access.encode()

        return access
    
    def authenticate(self, request: Request):
        access = self.get_access_cookie(request)
        if access is None: # header 확인
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(access)
        except InvalidToken:
            return None

        return self.get_user(validated_token), validated_token

