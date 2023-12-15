from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenBlacklistSerializer
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
        self.valid_and_save(serializer) # 유효성 검사후 저장
        return Response(serializer.data, status= status.HTTP_201_CREATED)


    # 회원정보 수정 (일부)
    def patch(self, request):
        return self.partial_update(request, partial= True)
    

    # 회원정보 수정 (전체)
    def put(self, request):
        return self.partial_update(request, partial= False)

    
    def delete(self, request):
        queryset = User.objects.get(username= request.user.username)
        queryset.delete() # User 객체 삭제
        return self.handle_response(request)
    
    
    # 유효성 검사후 save (중복 코드 개선)
    def valid_and_save(self, serializer):
        serializer.is_valid(raise_exception= True)
        serializer.save()

    # JWT 토큰 삭제 후 재로그인 유도 응답 (중복 코드 개선)
    def handle_response(self, request, serializer=None):
        # update시 데이터와 함께 200 코드 반환, delete시 204 코드만 반환
        response = Response(serializer.data ,status= status.HTTP_200_OK) if serializer else Response(status= status.HTTP_204_NO_CONTENT)
        # JWT 토큰을 삭제해 다시 로그인 하도록 유도
        response.delete_cookie("refresh")
        response.delete_cookie("access")

        # refresh token 미보유 예외처리
        try:
            refresh_token = request.COOKIES["refresh"]
            RefreshToken(refresh_token).blacklist() # 보유한 refresh 토큰을 blacklist
            
        except Exception as e: pass

        return response

    # PUT 과 PATCH 에서의 중복된 코드를 하나로 통일 (중복 코드 개선)
    def partial_update(self, request, partial=True):
        queryset = User.objects.get(username= request.user.username)
        serializer = UserSerializer(instance= queryset, data= request.data, partial= partial)
        self.valid_and_save(serializer) # 유효성 검사후 저장
        return self.handle_response(request, serializer)
    

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
            refresh_token = request.COOKIES["refresh"]
            data = {"refresh": refresh_token}
            serializer = TokenRefreshSerializer(data= data)
            serializer.is_valid(raise_exception= True)

            # 내가 커스텀 하려고 한 이유인 HttpOnly 추가
            response = Response(serializer.data, status= status.HTTP_200_OK)
            response.set_cookie("access", serializer.data["access"])
            # SIMPLE JWT 세팅을 rotation 시 refresh token 도 blacklist에 넣기로 했기 때문에
            # TokenRefreshSerializer 에서 refresh token 도 반환해줌.
            response.set_cookie("refresh", serializer.data["refresh"])
        
        # refresh 토큰이 없거나 토큰이 유효하지 않을 경우 예외
        except (KeyError, TokenError) as e:
            print(f"refresh 토큰 오류 : {e}")
            response = Response(status= status.HTTP_401_UNAUTHORIZED)

        return response
    


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
@api_view(['POST'])
def logout(request):
    try:
        refresh_token = str(request.COOKIES["refresh"])
        serializer = TokenBlacklistSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception= True)
        response = Response(status= status.HTTP_204_NO_CONTENT)

    except TokenError as e:
        data = {"detail": str(e)}
        response = Response(data= data, status= status.HTTP_400_BAD_REQUEST)
    
    # refresh 토큰과 access 토큰 삭제
    response.delete_cookie("refresh")
    response.delete_cookie("access")

    return response

