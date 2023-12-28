from typing import Tuple
from http.cookies import SimpleCookie

from rest_framework_simplejwt.tokens import RefreshToken


class JWTSetupMixin:
    def api_authentication(self, client, user) -> Tuple[str, str]:
        """
        사용자 인증을 위해 JWT를 생성하고 클라이언트의 쿠키에 토큰 정보 저장하고 필요에 따라 저장된 JWT 토큰을 반환.

        Parameters:
        - client : 토큰 정보를 저장할 클라이언트 객체.
        - user : JWT를 발급할 사용자 객체.

        Example 1:
        ```python
        mixin = JWTSetupMixin()
        mixin.api_authentication(client, user)
        ```

        Example 2:
        ```python
        mixin = JWTSetupMixin()
        refresh_token, access_token = mixin.api_authentication(client, user)
        ```
        """

        # refresh, access token 발급
        refresh_token = RefreshToken.for_user(user= user)
        access_token = refresh_token.access_token

        cookie = SimpleCookie()
        cookie['refresh'] = refresh_token
        cookie['access'] = access_token
        client.cookies = cookie

        return refresh_token, access_token

