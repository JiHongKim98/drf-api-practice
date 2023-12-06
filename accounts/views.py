from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from .serializers import UserSerializer
from .permissions import IsPostOrIsAuthenticated
from accounts.models import User


# CBV (Class-Base-Views) 클래스 기반 뷰
# User 설정 관련 API
class UserAPIView(APIView):
    permission_classes = [IsPostOrIsAuthenticated]
    authentication_classes = [SessionAuthentication] # JWT 방식으로 변경해야함!


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