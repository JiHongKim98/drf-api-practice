# drf-api-study

> Django REST FrameWork(DRF) study.

# *Contents*
### [1. Requirements](#requirements) <br/>
### [2. Test Case](#test-case) <br/>
### [3. End Points](#end-points) <br/>
### [4. JWT Authentication](#jwt-authentication) <br/>
### [5. Scheduler](#scheduler) <br/>
### [6. ERD](#erd) <br/>
### [7. Setting & Start](#setting--start) <br/>

<br/>

## *Requirements*

> - **BACKEND**
>   - Python 3.11 
>   - Django 4.2.7
>   - Django REST Framework 3.14.0
>   - Django REST Framework simplejwt 5.3.0
>   - Django APScheduler 0.6.2
> <br/>
>
> - **DATABASE**
>   - SQLite3 3.12.2
<br/>

## *Test Case*

> ### [**Accounts Test Case**](https://github.com/JiHongKim98/drf-api-study/tree/main/accounts/test)
> 
> - **test_user.py**
>
>   사용자 리소스 관련 **CURD 작업**과 해당 작업에 대한 **권한** 및 **예외처리**를 검증하기 위한 TEST CASE
> 
>    - UserRegistrationTestCase
>    - UserDetailTestCase
>    - UserModifyTestCase
>    - UserDeleteTestCase
> 
> - **test_authenticate.py**
>
>   JWT 기반 인증 관련 **HttpOnly 속성의 토큰 발급**과 토큰이 Blacklist 에 등록되는 경우인 **Refresh, Logout API** 및 **예외처리**를 검증하는 TEST CASE
> 
>    - UserLoginTestCase
>    - TokenBlacklistTestCase
>
> ### [**Boards Test Case**](https://github.com/JiHongKim98/drf-api-study/tree/main/boards/test)
>
> - **test_post.py**
> 
>   게시글 리소스 관련 **CRUD 작업**과 해당 작업에 대한 **권한** 및 **예외처리**와 외래키 부분 (**owner 필드**) 검증을 위한 TEST CASE
> 
>    - PostCreateTestCase
>    - PostListPaginationTestCase
>    - PostRetrieveTestCase
>    - PostModifyTestCase
>    - PostDeleteTestCase
> 
> - **test_comment.py**
>
>   댓글 리소스 관련 **CRUD 작업**과 해당 작업에 대한 **권한** 및 **예외처리**와 외래키 부분 (**owner 와 board 필드**) 검증을 위한 TEST CASE
> 
>    - CommentCreateTestCase
>    - CommentRetrieveTestCase
>    - CommentModifyTestCase
>    - CommentDeleteTestCase
>
> ### [common.py](https://github.com/JiHongKim98/drf-api-study/tree/main/boards/test/common.py)
>
> **JWT 인증**이 필요한 TEST CASE를 위해 **Client 의 쿠키에 토큰 정보를 저장**하고 refresh 와 access **토큰을 반환**하는 JWTSetupMixin 클래스를 정의.
>
> JWTSetupMixin class Example Code
> ```python
> # Example 1 (return None):
> mixin = JWTSetupMixin()
> mixin.api_authentication(client, user)
>
> # Example 2 (return Token):
> mixin = JWTSetupMixin()
> refresh_token, access_token = mixin.api_authentication(client, user)
> ```
>
> ### Usage
>
> [Before Usage](#setting--start)
> 
> ```bash
> # Example for MacOS
> 
> # Example (Total TEST):
> python3 manage.py test
>
> # Example (accounts Test):
> python3 manage.py test accounts.test
> ```
<br/>

## *End Points*

> End Point 구축은 최대한 **RESTful 설계 규칙을 준수**함.
>
> ### [**Accounts API**](https://github.com/JiHongKim98/drf-api-study/tree/main/accounts)
>
> **BASE = /api/v1/accounts/**
> 
> - Users resource CRUD API
> 
>   | HTTP | Path | Method | Permission |
>   | --- | --- | --- | --- |
>   |**POST** | BASE/users | CREATE | None |
>   |**GET** | BASE/users | READ | Authenticated |
>   |**PATCH** | BASE/users | UPDATE | Authenticated |
>   |**PUT** | BASE/usesr | UPDATE | Authenticated |
>   |**DELETE** |BASE/users | DELETE | Authenticated |
>
> - JWT Authentication API 
>
>   | HTTP | Path | Method | Permission |
>   | --- | --- | --- | --- |
>   |**POST** | BASE/refresh | CREATE | None |
>   |**POST** | BASE/login | CREATE | None |
>   |**POST** | BASE/logout | CREATE | Authenticated |
>
> ### [**Boards API**](https://github.com/JiHongKim98/drf-api-study/tree/main/boards)
>
> **BASE = /api/v1/boards/**
>
> - Post resource CRUD API
>
>   | HTTP | Path | Method | Permission |
>   | --- | --- | --- | --- |
>   |**POST** | BASE/posts | CREATE | Authenticated |
>   |**GET** | BASE/posts | READ | None |
>   |**GET** | BASE/posts/\<int:pk\> |READ | None |
>   |**PATCH** | BASE/posts | UPDATE | Authenticated & Owner |
>   |**PUT** | BASE/posts | UPDATE | Authenticated & Owner |
>   |**DELETE** | BASE/posts | DELETE | Authenticated & Owner |
> 
> - Comments resource CRUD API
> 
>   | HTTP | Path | Method | Permission |
>   | --- | --- | --- | --- |
>   |**POST** | BASE/comments/\<int:pk\> |CREATE | Access Token |
>   |**GET** | BASE/comments/\<int:pk\> | READ | None |
>   |**PATCH** | BASE/comments/\<int:pk\> | UPDATE | Authenticated & Owner |
>   |**PUT** | BASE/comments/\<int:pk\> | UPDATE | Authenticated & Owner |
>   |**DELETE** | BASE/comments/\<int:pk\> | DELETE | Authenticated & Owner |
<br/>

## *JWT Authentication*

> ### HttpOnly JWT
> 
> 사용자 인증시 HttpOnly 속성의 JWT를 발급 받아 **XSS 공격**과 같은 보안 이슈를 **최소화** 함.
> 
> ```python
> # accounts/views.py
>
> # TokenObtainPairView 클래스에서 JWT 정보를 response 데이터에 포함해서 반환하기 때문에
> # "login success" 로 변경하고, JWT 를 쿠키에 저장.
> class LoginAPIView(TokenObtainPairView):
>   def post(self, request: Request, *args, **kwargs) -> Response:
>     res = super().post(request, *args, **kwargs)
>        
>     response = Response({"detail": "login success"}, status= status.HTTP_200_OK)
>     response.set_cookie("refresh", res.data.get('refresh', None), httponly= True)
>     response.set_cookie("access", res.data.get('access', None), httponly= True)
>
>     return response
> ```
> <br/>
>
> ### MiddleWare for HttpOnly JWT 
>
> HttpOnly 속성으로 인해 클라이언트의 스크립트에서 Authorization 헤더에 **access 토큰을 포함하지 못해** 인증이 제대로 이루어지지 않는 문제 발생.
> 
> 이를 해결하기 위해 **custom-middleware**를 작성
>
> ```python
> # accounts/custom_middleware.py
>
> class JWTAuthenticationMiddleware:
>   def __init__(self, get_response):
>     self.get_response = get_response
>
>   def __call__(self, request):
>     access_token_value = request.COOKIES.get('access')
>
>     if access_token_value:
>       try:
>         access_token = AccessToken(access_token_value)
>         user = access_token.payload.get('user_id')
> 
>         request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token_value}'
>
>         except Exception as e:
>           pass
>
>     response = self.get_response(request)
>     return response
> 
>
> # config/settings.py
>
> # JWT 를 헤더에 포함하는 미들웨어 설정 추가
> MIDDLEWARE = [
>   'accounts.custom_middleware.JWTAuthenticationMiddleware',
>   # ... middlewares ...
> ]
> ```
> Ref. [My Velog](https://velog.io/@kimjihong/issue-drf-jwt-header)
<br/>

## *Scheduler*

> ### BlacklistedToken, OutstandingToken
> 
> 기간이 지난 JWT 정보도 DB가 계속 보유하고 있어</br>
> 매우 **비효율** 적이라고 생각해 이를 어떻게 해결할지 고민.
>
> 따라서, 기간이 지난 JWT 를 자동으로 지우기 위해 <br/>
> Django 의 Apscheduler 를 통해 1시간마다 **BlacklistedToken**, **OutstandingToken** 내<br/>
> 저장된 기간이 지난 토큰을 확인하고 해당 토큰을 **자동으로 삭제하는 작업**을 수행하도록 구현.
>
> ```python
> # config/settings.py
>
> # django_apscheduler 등록
> INSTALLED_APPS = [
> # ... other installed apps ...
>   'django_apscheduler',
> ]
> 
>
> # accounts/scheduler.py
> 
> @transaction.atomic
> def clean_expiry_token():
>   now_date = timezone.now()
>   expired_tokens = OutstandingToken.objects.filter(expires_at__lt= now_date)
>   print(f"기간 지난 refresh 토큰 수 => {len(expired_tokens)}")
>
>   if expired_tokens != 0:
>     # ... Delete Token Logic ...
>
> def start():
>    # 1시간마다 기간지난 토큰을 삭제하는 스케쥴
>    # ... start Fuc for Job setting ...
> 
> 
> # accounts/apps.py
>
> class AccountsConfig(AppConfig):
>   # ...
>   def ready(self) -> None:
>     from .scheduler import start
>     start()
> ```
> <br/>
>
> ### **"database is locked"** Issue
>
>![dbislock](https://github.com/JiHongKim98/drf-api-study/assets/144337839/b523c488-3c0d-4000-b9ae-e2e7fe86e634)
> 
> **Issue** : Scheduler 사용중 **"database is locked"** 오류로 Job 이 제대로 이루어지지 않는 문제가 종종 발생.
>
> **Solution** : SQLite3 는 경량 데이터베이스로 **멀티 쓰레드를 지원하지 않아** 동시에 DB에 접근시 발생하는 오류로 근본적으로 해결하려면 **MySQL과 같은 고수준의 데이터베이스**를 사용해야함.
>
> Ref. [stackoverflow](https://stackoverflow.com/questions/31547234/django-sqlite-database-is-locked)
<br/>

## *ERD*

> ### **DATABASE ERD**
> ![Untitled](https://github.com/JiHongKim98/drf-api-study/assets/144337839/bd882bfc-271b-4dee-80da-09b7d81e18b6)
<br/>

## *Setting & Start*

### Windows

> **프로젝트 디렉토리 생성 및 이동**
> 
> ```shell
> mkdir yourproject
> cd /path/to/yourproject/
> ```
> <br/>
>
> **GIT clone**
>
> ```shell
> git clone https://github.com/JiHongKim98/drf-api-study.git
> cd drf-api-study
> ```
> <br/>
> 
> **가상환경 설정**
> 
> Windos 환경에서는 현재 실행중인 shell 프로세스에 대해서 스크립트 실행 권한을 변경한 뒤 <br/>
> ```Set-ExecutionPolicy RemoteSigned -Scope Process``` <br/>
> venv 환경으로 진입해야 합니다. <br/>
> 
> ```shell
> python -m venv venv
> 
> Set-ExecutionPolicy RemoteSigned -Scope Process
> .\venv\Scripts\activate
> 
> pip install -r requirements.txt
> ```
> <br/>
>
> **Start Django** 
> 
> ```shell
> python manage.py migrate
> python manage.py runserver
> ```

<br/>

### MacOS & Linux

> **프로젝트 디렉토리 생성 및 이동**
> 
> ```bash
> mkdir yourproject
> cd ~/path/to/yourproject/
> ```
> <br/>
> 
> **GIT clone**
>
> ```bash
> git clone https://github.com/JiHongKim98/drf-api-study.git
> cd drf-api-study
> ```
> <br/>
> 
> **가상환경 설정**
> 
> ```bash
> python3 -m venv venv
> 
> source /venv/bin/activate
> 
> pip install -r requirements.txt
> ```
> <br/>
>
> **Start Django** 
> 
> ```bash
> python3 manage.py migrate
> python3 manage.py runserver
> ```

