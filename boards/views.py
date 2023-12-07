from rest_framework import status, pagination
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404
from boards.models import PostModel, CommentModel
from .serializers import PostModelSerializer, CommentModelSerializer
from .permissions import IsOwnerOrReadOnly


# Post API (게시글 API)
class PostAPIView(APIView):
    # 권한처리
    permission_classes = [IsOwnerOrReadOnly]

    # 토큰 또는 세션 을 통한 인증
    authentication_classes = [JWTAuthentication]

    # 페이징 처리
    pagination_class = pagination.PageNumberPagination

    # Read (CRUD 의 READ 부분)
    def get(self, request, pk=None):
        if pk is None:
            # PostModel 내 저장된 모든 게시글 데이터
            queryset = PostModel.objects.all()
            page = self.pagination_class()
            Post_data_page = page.paginate_queryset(queryset, request)

            # 데이터 일부분만 보여주는 쿼리문 => URI?page=1
            if Post_data_page is not None:
                serializer = PostModelSerializer(Post_data_page, many=True)
                return page.get_paginated_response(serializer.data)
            
            serializer = PostModelSerializer(queryset, many=True)

        else:
            # 해당 PK를 가진 "게시글" 데이터과 "댓글" 목록을 가져옴
            queryset = get_object_or_404(PostModel, id= pk)
            serializer = PostModelSerializer(instance= queryset)
            comment_queryset = queryset.post_comment.all() # related_name 으로 역참조
            comment_serializer = CommentModelSerializer(instance= comment_queryset, many= True)

            data = {
                "board": serializer.data,
                "comment": comment_serializer.data
            }
            return Response(data, status= status.HTTP_200_OK)

        return Response(serializer.data, status= status.HTTP_200_OK)
    

    # Create (CRUD 의 CREATE 부분)
    def post(self, request, pk=None):
        # Create는 pk 정보가 없을때만 작동
        if pk is None:
            # serializer에 데이터를 보낼 때, request.data 에
            # 사용자 정보(pk)를 추가해서 처리 
            # 이유 => owner는 외래키(fk)로 User 모델과 연결 되어있음.
            user = request.user
            new_data = {**request.data, 'owner': user.pk}
            print(new_data)
            serializer = PostModelSerializer(data= new_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status= status.HTTP_201_CREATED)

            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
    
    # Upate - 해당하는 데이터의 "일부"만 업데이트 (CRUD 의 UPDATE 부분)
    def patch(self, request, pk=None):
        if pk is not None:
            queryset = get_object_or_404(PostModel, id= pk)

            # object의 접근 권한 확인 (해당 게시글을 작성한 사람만 가능)
            self.check_object_permissions(request= request, obj= queryset)
            serializer = PostModelSerializer(instance= queryset, data= request.data, partial= True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status= status.HTTP_200_OK)

            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        

    # Upate - 해당하는 데이터의 "전체"를 업데이트 (CRUD 의 UPDATE 부분)
    def put(self, request, pk=None):
        if pk is not None:
            queryset = get_object_or_404(PostModel, id= pk)

            # object의 접근 권한 확인 (해당 게시글을 작성한 사람만 가능)
            self.check_object_permissions(request= request, obj= queryset)
            serializer = PostModelSerializer(instance= queryset, data= request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status= status.HTTP_200_OK)

            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        

    # Delete - (CRUD 의 DELETE 부분)
    def delete(self, request, pk=None):
        if pk is not None:
            queryset = get_object_or_404(PostModel, id= pk)

            # object의 접근 권한 확인 (해당 게시글을 작성한 사람만 가능)
            self.check_object_permissions(request= request, obj= queryset)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        

# comment API (댓글 API)
class CommentAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]


    def get(self, request, pk):
        queryset = get_object_or_404(CommentModel, id= pk)
        serializer = CommentModelSerializer(instance= queryset)

        return Response(serializer.data, status= status.HTTP_200_OK)


    # POST 메소드는 해당 게시글(post)의 pk를 request로 받아서
    # 게시글에 댓글을 저장시 CommentModel에서 PostModel을 참조하고 있는
    # board 필드를 지정해서 저장하게 끔 구현
    def post(self, request, pk):
        try:
            new_data = {**request.data, 'board': pk, 'owner': request.user.pk}
            serializer = CommentModelSerializer(data= new_data)
            serializer.is_valid(raise_exception= True)
            serializer.save()

            return Response(serializer.data, status= status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(status= status.HTTP_400_BAD_REQUEST)


    # PATCH 메소드는 댓글의 PK 를 받는다.
    def patch(self, request, pk):
        queryset = get_object_or_404(CommentModel, id= pk)
        # object의 접근 권한 확인
        self.check_object_permissions(request= request, obj= queryset)

        serializer = CommentModelSerializer(instance= queryset, data= request.data, partial= True)
        serializer.is_valid(raise_exception= True)
        serializer.save()

        return Response(serializer.data, status= status.HTTP_200_OK)


    def put(self, request, pk):
        queryset = get_object_or_404(CommentModel, id= pk)
        # object의 접근 권한 확인
        self.check_object_permissions(request= request, obj= queryset)

        serializer = CommentModelSerializer(instance= queryset, data= request.data)
        serializer.is_valid(raise_exception= True)
        serializer.save()

        return Response(serializer.data, status= status.HTTP_200_OK)


    def delete(self, request, pk):
        queryset = get_object_or_404(CommentModel, id= pk)
        # object의 접근 권한 확인
        self.check_object_permissions(request= request, obj= queryset)
        queryset.delete()

        return Response(status= status.HTTP_204_NO_CONTENT)
