from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from boards.models import CommentModel, PostModel

# client에 access, refresh 토큰 설정이 중복되어 Mixin 클래스로 모듈화함
from boards.test.common import JWTSetupMixin


BASE_API_URL = '/api/v1/boards'

# Comments create test case (CREATE)
class CommentCreateTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

        cls.user_post = PostModel.objects.create(
            title= "title",
            contents= "contents",
            owner= cls.user
        )
    
    def test_create_comment_success(self):
        """
        case: 정상적으로 특정 게시글에 새로운 댓글이 생성될 경우
        
        1. 201 Created 응답.
        2. owner 는 요청을 보낸 사용자로 자동 생성 (반환값은 pk가 아닌 username).
        3. created_date와 updated_date 정보 자동 생성.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.post(
            path= f'{BASE_API_URL}/comments',
            data= {
                "contents": "댓글 내용",
                "board": self.user_post.pk
            },
            format= 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['board'], self.user_post.pk)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertIn('created_date', response.data)
        self.assertIn('updated_date', response.data)

    def test_create_comment_with_changed_owner_field(self):
        """
        case: owner 필드를 임의로 변경해 생성하려는 경우

        1. 201 Created 응답.
        2. owner 필드는 항상 request의 사용자 정보로 등록 (owner 필드 정보 무시).
        """

        dummy_user = User.objects.create_user(
            username= "dummy",
            password= "dummy-pw",
            email= "dummy@gmail.com",
            fullname= "dummy"
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)
            
        response = self.client.post(
            path= f'{BASE_API_URL}/comments',
            data= {
                "contents": "게시글 내용",
                "board": self.user_post.pk,
                "owner": dummy_user.pk
            },
            format= 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.username)

    def test_create_comment_wrong_post_pk(self):
        """
        case: 잘못된 게시글의 pk 정보로 댓글을 생성하려는 경우

        1. 400 Bad Reqeust 응답.
        2. 게시글 pk 정보 오류 메시지 반환.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.post(
            path= f'{BASE_API_URL}/comments',
            data= {
                "contents": "댓글 내용",
                "board": 0
            },
            format= 'json'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['board'][0].code

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_error_code, 'does_not_exist')

    def test_create_comment_with_missing_required_fields(self):
        """
        case: 필수 작성 fields 가 누락된 경우

        1. 400 Bad Request
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        required_fields = ['contents', 'board']

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        for pop_field in required_fields:
            data = {
                "contents": "댓글 내용",
                "board": self.user_post.pk
            }
            data.pop(pop_field)

            response = self.client.post(
                path= f'{BASE_API_URL}/comments',
                data= data,
                format= 'json'
            )

            # response 의 ErrorDetail code
            response_error_code = response.data[pop_field][0].code

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_error_code, 'required')

    def test_create_comment_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 새 게시글을 생성하려는 경우
        
        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.post(
            path= f'{BASE_API_URL}/comments',
            data= {
                "contents": "댓글 내용",
                "board": 0
            },
            format= 'json'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')


# Comments retrieve test case (READ)
class CommentRetrieveTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

        cls.user_post = PostModel.objects.create(
            title= "post-title",
            contents= "post-contents",
            owner= cls.user
        )

        cls.user_comment = CommentModel.objects.create(
            contents= "comment-contents",
            owner= cls.user,
            board= cls.user_post
        )

    def test_retrieve_comment_success(self):
        """
        case: 특정 댓글의 pk를 포함해 세부 정보를 요청할 경우

        1. 200 Ok 응답.
        2. owner 필드는 작성자의 username으로 반환.
        3. board 필드는 post의 pk 번호로 반환.
        """

        response = self.client.get(
            path= f'{BASE_API_URL}/comments/{self.user_comment.pk}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['board'], self.user_post.pk)

    def test_retrieve_nonexistent_post(self):
        """
        case: 존재하지 않는 comment의 세부 정보를 요청할 경우

        1. 404 Not Found 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.get(
            path= f'{BASE_API_URL}/comments/99999'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "찾을 수 없습니다.")


# Comments update test case (UPDATE)
class CommentModifyTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

        cls.user_post = PostModel.objects.create(
            title= "post-title",
            contents= "post-contents",
            owner= cls.user
        )

        cls.user_comment = CommentModel.objects.create(
            contents= "comment-contents",
            owner= cls.user,
            board= cls.user_post
        )

    def test_modify_own_comment(self):
        """
        case: 작성자 본인의 댓글 전체 리소스를 수정하는 경우 (put)

        1. 200 Ok 응답.
        2. contents 필드 내용 변경.
        3. updated_date 갱신.
        """

        before_updated_date = self.user_comment.updated_date
        data = {
            "contents": "modify-comment"
        }

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path= f'{BASE_API_URL}/comments/{self.user_post.pk}',
            data= data,
            format= 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contents'], data['contents'])
        self.assertNotEqual(response.data['updated_date'], before_updated_date)

    def test_partial_modify_own_comment(self):
        """
        case: 작성자 본인의 댓글 일부 리소스를 수정하는 경우 (patch)

        1. 200 Ok 응답.
        2. contents 필드 내용 변경.
        3. updated_date 갱신.
        """

        before_updated_date = self.user_comment.updated_date
        data = {
            "contents": "modify-comment"
        }
        
        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.patch(
            path= f'{BASE_API_URL}/comments/{self.user_post.pk}',
            data= data,
            format= 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contents'], data['contents'])
        self.assertNotEqual(response.data['updated_date'], before_updated_date)

    def test_modfiy_comment_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 댓글을 수정하려는 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.put(
            path= f'{BASE_API_URL}/comments/{self.user_comment.pk}',
            data= {
            "contents": "modify-comment"
            },
            format= 'json'
        )
        
        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')

    def test_modify_other_users_comment(self):
        """
        case: 다른 사용자의 댓글을 수정하려는 경우

        1. 403 Forbidden 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        dummy_user = User.objects.create_user(
            username= "dummy",
            password= "dummy-pw",
            email= "dummy@gmail.com",
            fullname= "dummy"
        )

        dummy_users_comment = CommentModel.objects.create(
            contents= "dummy-users-comment",
            owner= dummy_user,
            board= self.user_post
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path= f'{BASE_API_URL}/comments/{dummy_users_comment.pk}',
            data= {
            "contents": "modify-comment"
            },
            format= 'json'
        )
        
        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_error_code, 'permission_denied')


# Comments delte test case (DELETE)
class CommentDeleteTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username= "kimjihong",
            password= "password",
            email= "kinjihong9598@gmail.com",
            fullname= "kimjihong"
        )

        cls.user_post = PostModel.objects.create(
            title= "post-title",
            contents= "post-contents",
            owner= cls.user
        )

        cls.user_comment = CommentModel.objects.create(
            contents= "comment-contents",
            owner= cls.user,
            board= cls.user_post
        )

    def test_delete_own_comment(self):
        """
        case: 작성자 본인의 댓글을 삭제하는 경우

        1. 204 No Content 응답.
        2. CommentModel 에서 해당 게시글 삭제.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.delete(
            path= f'{BASE_API_URL}/comments/{self.user_comment.pk}'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CommentModel.objects.filter(pk= self.user_comment.pk).exists())

    def test_delete_other_users_comment(self):
        """
        case: 다른 사용자의 게시글을 삭제하려는 경우

        1. 403 Forbidden 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        dummy_user = User.objects.create_user(
            username= "dummy",
            password= "dummy-pw",
            email= "dummy@gmail.com",
            fullname= "dummy"
        )

        dummy_users_comment = CommentModel.objects.create(
            contents= "dummy-users-comment",
            owner= dummy_user,
            board= self.user_post
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path= f'{BASE_API_URL}/comments/{dummy_users_comment.pk}'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_error_code, 'permission_denied')

    def test_delete_comment_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 댓글을 삭제하려는 경우

        1. 401 Unauthorized 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.delete(
            path= f'{BASE_API_URL}/comments/{self.user_comment.pk}'
        )

        # response 의 ErrorDetail code
        response_error_code = response.data['detail'].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, 'not_authenticated')

