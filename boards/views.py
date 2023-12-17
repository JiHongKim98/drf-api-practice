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
    permission_classes = [IsOwnerOrReadOnly] # 권한처리
    authentication_classes = [JWTAuthentication] # 토큰을 통한 인증
    pagination_class = pagination.PageNumberPagination # 페이징 처리

    # Read (CRUD 의 READ 부분)
    def get(self, request, pk=None):
        if pk:
            return self.retrieve_posts(request, pk) # pk exist => 게시글 세부사항
        else:
            return self.list_posts(request) # pk none => 게시글 목록
    

    # Create (CRUD 의 CREATE 부분)
    def post(self, request, pk=None):
        if pk:
            return Response(status= status.HTTP_400_BAD_REQUEST)

        # owner(pk) 정보를 추가하여 serializer를 반환
        request.data['owner'] = request.user.pk
        serializer = PostModelSerializer(data= request.data)
        self.valid_and_save(serializer)
        return Response(serializer.data, status= status.HTTP_201_CREATED)
        
    
    # Upate - 해당하는 데이터의 "일부"만 업데이트 (CRUD 의 UPDATE 부분)
    def patch(self, request, pk=None):
        return self.partial_update(request, pk, partial= True)
        

    # Upate - 해당하는 데이터의 "전체"를 업데이트 (CRUD 의 UPDATE 부분)
    def put(self, request, pk=None):
        request.data['owner'] = request.user.pk
        return self.partial_update(request, pk, partial= False)
        

    # Delete - (CRUD 의 DELETE 부분)
    def delete(self, request, pk=None):
        if pk is None:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
        queryset = get_object_or_404(PostModel, id= pk)
        self.check_object_permissions(request= request, obj= queryset) # 해당 게시글을 작성한 사람만 가능
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    # pk none => 게시글 목록
    def list_posts(self, request):
        queryset = PostModel.objects.all()
        page = self.pagination_class()
        post_data_page = page.paginate_queryset(queryset, request)

        # 게시글 페이징 처리
        if post_data_page:
            serializer = PostModelSerializer(post_data_page, many= True)
            return page.get_paginated_response(serializer.data)
        
        serializer = PostModelSerializer(queryset, many= True)
        return Response(serializer.data, status.HTTP_200_OK)

    # pk exist => 게시글 세부사항
    def retrieve_posts(self, request, pk):
        post_instance = get_object_or_404(PostModel, id= pk)
        serializer = PostModelSerializer(post_instance)
        comment_queryset = post_instance.post_comment.all() # related_name 으로 역참조
        comment_serializer = CommentModelSerializer(comment_queryset, many= True)

        data = {"board": serializer.data, "comment": comment_serializer.data}
        return Response(data, status=status.HTTP_200_OK)
    
    # PUT 과 PATCH 에서의 중복된 코드를 하나로 통일 (중복 코드 개선)
    def partial_update(self, request, pk=None, partial=True):
        if pk is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = get_object_or_404(PostModel, id=pk)
        self.check_object_permissions(request=request, obj=queryset) # 해당 게시글을 작성한 사람만 가능
        serializer = PostModelSerializer(instance= queryset, data= request.data, partial= partial)
        self.valid_and_save(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 유효성 검사후 save (중복 코드 개선)
    def valid_and_save(self, serializer):
        serializer.is_valid(raise_exception= True)
        serializer.save()


# comment API (댓글 API)
class CommentAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]


    def get(self, request, pk=None):
        if pk is None:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
        queryset = get_object_or_404(CommentModel, id= pk)
        serializer = CommentModelSerializer(instance= queryset)
        return Response(serializer.data, status= status.HTTP_200_OK)


    def post(self, request, pk=None):
        if pk:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
        # owner(pk) 정보를 추가하여 serializer를 반환
        request.data['owner'] = request.user.pk
        serializer = CommentModelSerializer(data= request.data)
        self.valid_and_save(serializer)
        return Response(serializer.data, status= status.HTTP_201_CREATED)


    def patch(self, request, pk=None):
        return self.partial_update(request, pk, partial= True)


    def put(self, request, pk=None):
        request.data['owner'] = request.user.pk
        return self.partial_update(request, pk, partial= False)


    def delete(self, request, pk=None):
        if pk is None:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_comment_and_check_permission(request, pk)
        queryset.delete()
        return Response(status= status.HTTP_204_NO_CONTENT)
    

    # 유효성 검사후 save (중복 코드 개선)
    def valid_and_save(self, serializer):
        serializer.is_valid(raise_exception= True)
        serializer.save()

    # Comment 정보를 가져오고 권한 검사 (중복 코드 개선)
    def get_comment_and_check_permission(self, request, pk):
        queryset = get_object_or_404(CommentModel, id= pk)
        self.check_object_permissions(request= request, obj= queryset) # object의 접근 권한 확인
        return queryset

    # PUT 과 PATCH 에서의 중복된 코드를 하나로 통일 (중복 코드 개선)
    def partial_update(self, request, pk=None, partial=True):
        if pk is None:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_comment_and_check_permission(request, pk)
        if request.method == 'PUT':
            request.data['board'] = queryset.board.pk

        serializer = CommentModelSerializer(instance= queryset, data= request.data, partial= partial)
        self.valid_and_save(serializer)
        return Response(serializer.data, status= status.HTTP_200_OK)

