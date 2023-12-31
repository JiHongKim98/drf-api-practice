from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from boards.models import CommentModel, PostModel
from tests.utils import JWTSetupMixin

BASE_API_URL = "/api/v1/boards"


# posts create test case (CREATE)
class PostCreateTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="kimjihong",
            password="password",
            email="kinjihong9598@gmail.com",
            fullname="kimjihong",
            is_active=True,
        )

    def test_create_post_success(self):
        """
        case: 정상적으로 새로운 게시글이 생성될 경우

        1. 201 Created 응답.
        2. owner 는 요청을 보낸 사용자로 자동 생성 (반환값은 pk가 아닌 username).
        3. response 데이터에 해당 게시글의 달린 댓글의 정보 comments 필드도 포함되어야함.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.post(
            path=f"{BASE_API_URL}/posts",
            data={"title": "게시글 제목", "contents": "게시글 내용"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.user.username)
        self.assertIn("comments", response.data)

    def test_create_post_with_changed_owner_field(self):
        """
        case: owner 필드를 임의로 변경해 생성하려는 경우

        1. 201 Created 응답.
        2. owner 필드는 항상 request의 사용자 정보로 등록 (owner 필드 정보 무시).
        """

        dummy_user = User.objects.create_user(
            username="dummy",
            password="dummy-pw",
            email="dummy@gmail.com",
            fullname="dummy",
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.post(
            path=f"{BASE_API_URL}/posts",
            data={"title": "게시글 제목", "contents": "게시글 내용", "owner": dummy_user.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.user.username)

    def test_create_post_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 새 게시글을 생성하려는 경우

        1. 401 Unauthorized 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        response = self.client.post(
            path=f"{BASE_API_URL}/posts",
            data={"title": "게시글 제목", "contents": "게시글 내용"},
            format="json",
        )

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, "not_authenticated")

    def test_create_post_with_missing_required_fields(self):
        """
        case: 필수 작성 fields 가 누락된 경우

        1. 400 Bad Request 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        # 필수 fields 정의
        required_fields = ["title", "contents"]

        for pop_field in required_fields:
            data = {"title": "게시글 제목", "contents": "게시글 내용"}
            data.pop(pop_field)

            response = self.client.post(
                path=f"{BASE_API_URL}/posts", data=data, format="json"
            )

            response_error_code = response.data[pop_field][0].code

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_error_code, "required")


# posts list pagination test case (READ)
class PostListPaginationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="kimjihong",
            password="password",
            email="kinjihong9598@gmail.com",
            fullname="kimjihong",
            is_active=True,
        )

        # 50 dummy posts
        for i in range(50):
            PostModel.objects.create(
                title="dummy-title", contents="dummy-contents", owner=user
            )

    def test_post_list_success(self):
        """
        case: 게시글들의 정보 요청할 경우

        1. 200 Ok 응답.
        2. 최근 게시글 10개의 정보만 반환.
        3. 다음 페이지의 커서 파라미터를 next에 포함.
        """

        response = self.client.get(path=f"{BASE_API_URL}/posts")

        posts_list = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(posts_list), 10)
        self.assertIn("?cursor", response.data["next"])

    def test_post_pagination_with_invalid_cursor(self):
        """
        case: 유효하지 않은 커서로 게시글들의 정보 요청할 경우

        1. 404 Not Found 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환
        """

        response = self.client.get(path=f"{BASE_API_URL}/posts?cursor=123A2B3d")

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_error_code, "not_found")


# posts retrieve test case (READ)
class PostRetrieveTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="kimjihong",
            password="password",
            email="kinjihong9598@gmail.com",
            fullname="kimjihong",
            is_active=True,
        )

        cls.user_post = PostModel.objects.create(
            title="title", contents="contents", owner=cls.user
        )

        # 5 comments
        for i in range(5):
            CommentModel.objects.create(
                owner=cls.user, post=cls.user_post, contents="comments"
            )

    def test_retrieve_post_success(self):
        """
        case: 특정 게시글의 pk를 포함해 세부 정보를 요청할 경우

        1. 200 Ok 응답.
        2. owner 필드는 작성자의 username으로 반환.
        3. 해당 게시글에 달린 댓글들은 comments 필드에 포함.
        """

        response = self.client.get(path=f"{BASE_API_URL}/posts/{self.user_post.pk}")

        comments_response_len = len(response.data["comments"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["owner"], self.user.username)
        self.assertIn("comments", response.data)
        self.assertEqual(comments_response_len, 5)

    def test_retrieve_nonexistent_post(self):
        """
        case: 존재하지 않는 게시글의 세부 정보를 요청할 경우

        1. 404 Not Found 응답.
        2. detail 필드에 오류 메시지를 포함하여 반환.
        """

        response = self.client.get(path=f"{BASE_API_URL}/posts/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "찾을 수 없습니다.")


# posts update test case (UPDATE)
class PostModifyTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="kimjihong",
            password="password",
            email="kinjihong9598@gmail.com",
            fullname="kimjihong",
            is_active=True,
        )

        cls.user_post = PostModel.objects.create(
            title="title", contents="contents", owner=cls.user
        )

    def test_modify_own_post(self):
        """
        case: 작성자 본인의 게시글의 전체 리소스를 수정하는 경우 (put)

        1. 200 Ok 응답.
        2. title, contents 필드 내용 변경.
        3. updated_date 갱신.
        """

        before_updated_date = self.user_post.updated_date

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path=f"{BASE_API_URL}/posts/{self.user_post.pk}",
            data={"title": "post-title", "contents": "post-contents"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "post-title")
        self.assertEqual(response.data["contents"], "post-contents")
        self.assertNotEqual(before_updated_date, response.data["updated_date"])

    def test_partial_modify_own_post(self):
        """
        case: 작성자 본인의 게시글의 일부 리소스를 수정하는 경우 (patch)

        1. 200 Ok 응답.
        2. 해당 필드 내용 변경.
        3. updated_date 갱신.
        """

        before_updated_date = self.user_post.updated_date

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        update_fields = ["title", "contents"]

        for partical_field in update_fields:
            response = self.client.patch(
                path=f"{BASE_API_URL}/posts/{self.user_post.pk}",
                data={partical_field: "patch-test"},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data[partical_field], "patch-test")
            self.assertNotEqual(before_updated_date, response.data["updated_date"])

    def test_modfiy_post_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 게시글을 수정하려는 경우

        1. 401 Unauthorized 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        response = self.client.put(
            path=f"{BASE_API_URL}/posts/{self.user_post.pk}",
            data={"title": "post-title", "contents": "post-contents"},
            format="json",
        )

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, "not_authenticated")

    def test_modify_other_users_post(self):
        """
        case: 다른 사용자의 게시글을 수정하려는 경우

        1. 403 Forbidden 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        dummy_user = User.objects.create_user(
            username="dummy",
            password="dummy-pw",
            email="dummy@gmail.com",
            fullname="dummy",
        )

        dummy_users_post = PostModel.objects.create(
            title="title", contents="contents", owner=dummy_user
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.put(
            path=f"{BASE_API_URL}/posts/{dummy_users_post.pk}",
            data={"title": "post-title", "contents": "post-contents"},
            format="json",
        )

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_error_code, "permission_denied")

    def test_modify_post_owner_info(self):
        """
        case: 게시글의 onwer 정보를 수정하려는 경우

        1. 200 Ok 응답.
        2. owner 필드는 변경되지 않음.
        3. updated_date 갱신.
        """

        dummy_user = User.objects.create_user(
            username="dummy",
            password="dummy-pw",
            email="dummy@gmail.com",
            fullname="dummy",
        )

        before_updated_date = self.user_post.updated_date

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.patch(
            path=f"{BASE_API_URL}/posts/{self.user_post.pk}",
            data={"owner": dummy_user.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["owner"], dummy_user.username)
        self.assertNotEqual(before_updated_date, response.data["updated_date"])


# posts deletion test case (DELETE)
class PostDeleteTestCase(APITestCase, JWTSetupMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="kimjihong",
            password="password",
            email="kinjihong9598@gmail.com",
            fullname="kimjihong",
            is_active=True,
        )

        cls.user_post = PostModel.objects.create(
            title="title", contents="contents", owner=cls.user
        )

    def test_delete_own_post(self):
        """
        case: 작성자 본인의 게시글을 삭제하는 경우

        1. 204 No Content 응답.
        2. PostModel 에서 해당 게시글 삭제.
        """

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.delete(path=f"{BASE_API_URL}/posts/{self.user_post.pk}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PostModel.objects.filter(pk=self.user_post.pk).exists())

    def test_delete_other_users_post(self):
        """
        case: 다른 사용자의 게시글을 삭제하려는 경우

        1. 403 Forbidden 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        dummy_user = User.objects.create_user(
            username="dummy",
            password="dummy-pw",
            email="dummy@gmail.com",
            fullname="dummy",
        )

        dummy_users_post = PostModel.objects.create(
            title="title", contents="contents", owner=dummy_user
        )

        # client 에 refresh, access 토큰 설정 (JWTSetupMixin)
        self.api_authentication(self.client, self.user)

        response = self.client.delete(
            path=f"{BASE_API_URL}/posts/{dummy_users_post.pk}"
        )

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_error_code, "permission_denied")

    def test_delete_post_with_unauthorized(self):
        """
        case: 인증되지 않은 사용자가 게시글을 삭제하려는 경우

        1. 401 Unauthorized 응답.
        2. response 데이터에 해당 필드 오류 메시지 포함.
        """

        response = self.client.delete(path=f"{BASE_API_URL}/posts/{self.user_post.pk}")

        response_error_code = response.data["detail"].code

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_error_code, "not_authenticated")
