from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from http.cookies import SimpleCookie
from accounts.models import User

# client에 access, refresh 토큰 설정이 중복되어 Mixin 클래스로 모듈화함
from accounts.test.common import JWTSetupMixin


BASE_API_URL = '/api/v1/accounts'

# Login API test case
class UserLoginTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

    def test_authentication_with_valid_data(self):
        """
        case: 정상적으로 로그인 하는 경우

        1. 200 OK 응답.
        2. refresh, access 토큰이 쿠키에 포함.
        3. refresh, access 토큰 HttpOnly 옵션.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/login',
            data= {
                "username": "kimjihong",
                "password": "password"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.client.cookies.get('refresh', None))
        self.assertIsNotNone(self.client.cookies.get('access', None))
        self.assertIn('httponly', str(self.client.cookies.get('refresh', None)).lower())
        self.assertIn('httponly', str(self.client.cookies.get('access', None)).lower())

    def test_authentication_with_nonexistent_username(self):
        """
        case: 존재하지 않는 username 으로 로그인 시도한 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/login',
            data= {
                "username": "nonexistent",
                "password": "password"
            }
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'no_active_account')

    def test_authentication_missing_required_fields(self):
        """
        case: 필수 작성 fields(username, password) 가 빠진 경우

        1. 400 Bad Request 응답.
        2. detail 에 해당 필드 오류 메시지 포함.
        """

        # 필수 fields 정의
        required_fields = ['username', 'password']

        data = {
            "username": "kimjihong",
            "password": "password"
        }

        for pop_field in required_fields:
            data.pop(pop_field)
            response = self.client.post(
                path= f'{BASE_API_URL}/login',
                data= data
            )

            # response 의 ErrorDetail code
            response_error_code = response.data[pop_field][0].code

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_error_code, 'required')

    def test_authentication_with_wrong_password(self):
        """
        case: username 이 존재하지만, password 가 틀린 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/login',
            data= {
                "username": "kimjihong",
                "password": "wrong-password"
            }
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'no_active_account')


# Logout & Refresh (JWT-blacklist) API test case
class TokenBlacklistTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

    def test_user_logout_and_blacklisted_token(self):
        """
        case: 정상적으로 로그아웃이 진행된 경우
        
        1. 200 Ok 응답.
        2. refresh 토큰은 blacklist 에 등록.
        3. cookie 에 저장된 refresh, access 토큰 정보 삭제. 
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        refresh_token, access_token = self.api_authentication(self.client, self.user)

        response = self.client.post(
            path= f'{BASE_API_URL}/logout'
        )

        # OutstandingToken 에서 refresh 토큰의 id 추출 (blacklist 에서 확인하기 위함)
        refresh_instance = OutstandingToken.objects.get(token= refresh_token)
        refresh_id = refresh_instance.id

        cookies = self.client.cookies

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BlacklistedToken.objects.filter(token_id= refresh_id).exists())
        self.assertNotIn(refresh_token, cookies.get('refresh', None))
        self.assertNotIn(access_token, cookies.get('access', None))

    def test_user_logout_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 로그아웃 요청을 보낸 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/logout'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')

    def test_token_refresh_rotate(self):
        """
        case: refresh 토큰을 통해 token refresh 가 정상적으로 진행된 경우

        1. 200 OK 응답.
        2. 기존 refresh 토큰은 blacklist 에 등록.
        3. cookie 에 새로운 refresh, access 토큰으로 변경.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        refresh_token, access_token = self.api_authentication(self.client, self.user)
        
        response = self.client.post(
            path= f'{BASE_API_URL}/refresh'
        )
        
        # OutstandingToken 에서 refresh 토큰의 id 추출 (blacklist 에서 확인하기 위함)
        refresh_instance = OutstandingToken.objects.get(token= refresh_token)
        refresh_id = refresh_instance.id

        cookies = self.client.cookies

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BlacklistedToken.objects.filter(token_id= refresh_id).exists())
        self.assertIsNotNone(cookies.get('refresh', None))
        self.assertIsNotNone(cookies.get('access', None))
        self.assertNotEqual(refresh_token, cookies.get('refresh', None))
        self.assertNotEqual(access_token, cookies.get('access', None))

    def test_token_refresh_without_refresh_token(self):
        """
        case: refresh 토큰이 없는 사용자가 token refresh 를 요청한 경우

        1. 401 Unauthorized 응답.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/refresh'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_with_invalid_token(self):
        """
        case: 유효하지 않는 refresh 토큰으로 token refresh 를 요청한 경우

        1. 401 Unauthorized 응답.
        """
        
        # 유효하지 않은 임의의 refresh 토큰 쿠키에 추가
        cookie = SimpleCookie()
        cookie['refresh'] = '123.456.789'
        self.client.cookies = cookie

        response = self.client.post(
            path= f'{BASE_API_URL}/refresh'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

