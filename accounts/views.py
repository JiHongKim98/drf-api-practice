from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

from rest_framework_simplejwt.tokens import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from .serializers import UserSerializer
from .permissions import IsPostOrIsAuthenticated
from accounts.models import User


# CBV (Class-Base-Views) 클래스 기반 뷰
# User 설정 관련 API
class UserAPIView(APIView):
    permission_classes = [IsPostOrIsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]


    # 본인 회원정보 조회
    def get(self, request):
        queryset = User.objects.get(username= request.user.username)
        serializer = UserSerializer(instance= queryset)

        return Response(serializer.data, status= status.HTTP_200_OK)


    # 회원가입
    def post(self, request):
        serializer = UserSerializer(data= request.data)

        # 유효성 검사
        serializer.is_valid(raise_exception= True)
        # User 객체 저장 (serializer의 create 메소드 호출)
        serializer.save()

        return Response(serializer.data, status= status.HTTP_201_CREATED)


    # 회원정보 수정 (일부)
    def patch(self, request):
        queryset = User.objects.get(username= request.user.username)
        serializer = UserSerializer(instance= queryset, data= request.data, partial= True)

        # 유효성 검사
        serializer.is_valid(raise_exception=True)
        # User 객체 수정사항 저장 (serializer의 update 메소드 호출)
        serializer.save()
        response = Response(serializer.data, status= status.HTTP_200_OK)

        return response
    

    # 회원정보 수정 (전체)
    def put(self, request):
        queryset = User.objects.get(username= request.user.username)
        serializer = UserSerializer(instance= queryset, data= request.data)

        # 유효성 검사
        serializer.is_valid(raise_exception= True)
        # User 객체 수정사항 저장 (serializer의 update 메소드 호출)
        serializer.save()
        response = Response(serializer.data, status= status.HTTP_200_OK)

        return response

    
    def delete(self, request):
        queryset = User.objects.get(username= request.user.username)
        # User 객체 삭제 (serializer의 delete 메소드 호출)
        queryset.delete()
        response = Response(status= status.HTTP_204_NO_CONTENT)

        return response
    

# FBV (Function-Base-Views) 함수 기반 뷰
# 로그인 API
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # 사용자 인증
    user = authenticate(username= request.data.get("username"), password= request.data.get("password"))
    
    # 등록된 사용자인지 확인
    if user is not None:
        serializer = UserSerializer(user)

        # JWT 토큰
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        response = Response(
            {
                "user": serializer.data,
                "detail": "login success",
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            },
            status= status.HTTP_200_OK,
        )

        # JWT 토큰을 브라우저의 쿠키내 저장
        response.set_cookie("access", access_token, httponly=True)
        response.set_cookie("refresh", refresh_token, httponly=True)

        # 최근 로그인 기록 업데이트
        update_last_login(None, user)

        return response
    
    else:
        return Response(status= status.HTTP_400_BAD_REQUEST)
    

# 커스텀 TokenRefreshView (refresh 요청시 token 을 httponly 로 response 받기)
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    # Refresh 는 post 메소드만
    def post(self, request):
        try:
            data = {"refresh": request.COOKIES["refresh"]}
            print(data)
            serializer = TokenRefreshSerializer(data= data)
            serializer.is_valid(raise_exception= True)

            # 내가 커스텀 하려고 한 이유인 HttpOnly 추가
            response = Response(serializer.data, status= status.HTTP_200_OK)
            response.set_cookie("access", serializer.data["access"])
            # SIMPLE JWT 세팅을 rotation 시 refresh token 도 blacklist에 넣기로 했기 때문에
            # TokenRefreshSerializer 에서 refresh token 도 반환해줌.
            response.set_cookie("refresh", serializer.data["refresh"])
        
        # request의 COOKIE 에 refresh token 정보가 없을 때 예외처리
        except KeyError as e:
            print(e)
            response = Response(status= status.HTTP_401_UNAUTHORIZED)

        # 만료되었거나 완전히 이상한 refresh token 예외처리
        except TokenError as e:
            print(e)
            response = Response(status= status.HTTP_401_UNAUTHORIZED)

        return response