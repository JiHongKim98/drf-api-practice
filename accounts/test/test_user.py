from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from http.cookies import SimpleCookie
from accounts.models import User

# client에 access, refresh 토큰 설정이 중복되어 Mixin 클래스로 모듈화함
from accounts.test.common import JWTSetupMixin


BASE_API_URL = '/api/v1/accounts'

# CREATE test case
class UserRegistrationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dummy_user = User.objects.create_user(
            username= "dummy",
            password= "dummy-pw",
            email= "dummy@gmail.com",
            fullname= "dummy"
        )

    def setUp(self):
        self.new_user = {
            "username": "kimjihong",
            "password": "password",
            "email": "kinjihong9598@gmail.com",
            "fullname": "kimjihong"
        }

        self.new_user_info = {
            "id": 2,
            "username": "kimjihong",
            "password": "password",
            "email": "kinjihong9598@gmail.com",
            "fullname": "kimjihong"
        }

    def test_registration_success(self):
        """
        case: 정상적으로 새로운 user 가 생성된 경우

        1. 201 Created 응답.
        2. 생성된 사용자의 password 정보는 보내지 않음.
        """
        
        response = self.client.post(
            path= f'{BASE_API_URL}/users',
            data= self.new_user
        )
        
        self.new_user_info.pop('password')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(response.data, self.new_user_info)

    def test_registration_unique_username_validate(self):
        """
        case: 이미 사용중인 username 인 경우

        1. 400 Bad Request 응답.
        2. response 데이터에 username 필드 오류 메시지 포함.
        """

        # 이미 사용중인 username 으로 변경
        self.new_user['username'] = self.dummy_user.username

        response = self.client.post(
            path= f'{BASE_API_URL}/users',
            data= self.new_user
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['username'][0].code
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_error_code, 'unique')

    def test_registration_with_missing_required_fields(self):
        """
        case: 필수 작성 fields 가 빠진 경우

        1. 400 Bad Request 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        # 필수 fields 정의
        required_fields = ['username', 'password', 'email', 'fullname']

        for pop_field in required_fields:
            new_data = self.new_user.copy()
            new_data.pop(pop_field)

            response = self.client.post(
                path= f'{BASE_API_URL}/users',
                data= new_data
            )

            # response 의 ErrorDetail code
            response_error_code = response.data[pop_field][0].code

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_error_code, 'required')


# READ test case
class UserDetailTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

    def setUp(self):
        self.user_info = {
            "id": 1,
            "username": "kimjihong",
            "password": "password",
            "email": "kinjihong9598@gmail.com",
            "fullname": "kimjihong"
        }
    
    def test_user_detail_authorized(self):
        """
        case: 인증된 사용자가 사용자 세부 정보를 요청한 경우
        
        1. 200 OK 응답.
        2. 요청을 보낸 사용자의 password 정보는 미포함.
        """
        
        self.user_info.pop('password')

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.get(
            path= f'{BASE_API_URL}/users'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.user_info)

    def test_user_detail_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 세부 정보를 요청한 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """
        # cookie 정보 초기화 (token 초기화)
        cookie = SimpleCookie()
        self.client.cookies = cookie

        response = self.client.get(
            path= f'{BASE_API_URL}/users'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')


# UPDATE test case
class UserModifyTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

    def setUp(self):
        self.update_user = {
            "username": "update",
            "password": "update-pw",
            "email": "update@gmail.com",
            "fullname": "update"
        }

        self.update_user_info = {
            "id": 1,
            "username": "update",
            "password": "update-pw",
            "email": "update@gmail.com",
            "fullname": "update"
        }
    
    def test_modify_user_info_success(self):
        """
        case: 사용자 정보의 전체 리소스를 수정하는 경우 (put)

        1. 200 OK 응답.
        2. 전체 필드 내용이 변경됨.
        3. 요청을 보낸 user의 password 정보는 미포함.
        4. 업데이트 완료 후 사용자 강제 로그아웃 (2 - logic)
           - refresh token blacklisted
           - delete refresh, access token in cookies
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        refresh_token, _ = self.api_authentication(self.client, self.user)

        response = self.client.put(
            path= f'{BASE_API_URL}/users',
            data= self.update_user
        )

        self.update_user_info.pop('password')

        # OutstandingToken 에서 refresh 토큰의 id 추출 (blacklist 에서 확인하기 위함)
        refresh_instance = OutstandingToken.objects.get(token= refresh_token)
        refresh_id = refresh_instance.id

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.update_user_info)
        self.assertTrue(BlacklistedToken.objects.filter(token_id= refresh_id).exists())

    def test_partial_modify_user_info_success(self):
        """
        case: 사용자 정보의 일부 리소스를 수정하는 경우 (patch)

        1. 200 OK 응답
        2. 해당 필드 내용만 변경됨.
        3. 요청을 보낸 user의 password 정보는 미포함.
        4. 업데이트 완료 후 로그아웃 (2 - logic)
           - refresh token blacklisted
           - delete refresh, access token in cookies
        """

        # 업데이트 fields 정의
        update_fields = ['username', 'password', 'email', 'fullname']

        self.update_user_info.pop('password')

        for update_field in update_fields:
            # 매 업데이트 마다 토큰이 사라지므로 새 토큰 갱신
            refresh_token, _ = self.api_authentication(self.client, self.user)

            response = self.client.patch(
                path= f'{BASE_API_URL}/users',
                data= {
                    update_field: self.update_user[update_field]
                    }
            )

            refresh_instance = OutstandingToken.objects.get(token= refresh_token)
            refresh_id = refresh_instance.id

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data[update_field], self.update_user[update_field]) if update_field != 'password' else None
            self.assertTrue(BlacklistedToken.objects.filter(token_id= refresh_id).exists())

    def test_modify_user_details_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 UPDATE 요청을 한 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.put(
            path= f'{BASE_API_URL}/users',
            data= self.update_user
        )
        
        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')

    def test_modify_unique_username_validate(self):
        """
        case: 이미 사용중인 username 으로 UPDATE 요청한 경우

        1. 400 Bad Request 응답.
        2. response 데이터에 username 필드 오류 메시지 포함.
        """

        dummy_user = User.objects.create_user(
            username= "dummy",
            password= "dummy-pw",
            email= "dummy@gmail.com",
            fullname= "dummy"
        )

        # 이미 사용중인 username 으로 변경
        self.update_user['username'] = dummy_user.username

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path= f'{BASE_API_URL}/users',
            data= self.update_user
        )
        
        # response 의 ErrorDetail code
        response_error_code = response.data['username'][0].code

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_error_code, 'unique')



# DELETE test case
class UserDeleteTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )
        
    def test_delete_user_success(self):
        """
        case: 정상적으로 user 정보가 삭제된 경우
        
        1. 204 No Content 응답.
        2. refresh, access 토큰 쿠키에서 삭제
        3. refresh token blacklisted
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        refresh_token, access_token = self.api_authentication(self.client, self.user)

        response = self.client.delete(
            path= f'{BASE_API_URL}/users'
        )

        refresh_instance = OutstandingToken.objects.get(token= refresh_token)
        refresh_id = refresh_instance.id

        cookies = self.client.cookies

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(refresh_token, cookies.get('refresh', None))
        self.assertNotIn(access_token, cookies.get('access', None))
        self.assertTrue(BlacklistedToken.objects.filter(token_id= refresh_id).exists())

    def test_delete_user_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 delete 요청한 경우
        
        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.delete(
            path= f'{BASE_API_URL}/users'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')

