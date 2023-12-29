from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)

from drf_spectacular.utils import extend_schema, extend_schema_view

from boards.models import PostModel, CommentModel
from boards.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer
)
from boards.permissions import IsOwnerOrReadOnly
from boards.paginations import PostCurosrPagination


@extend_schema(tags= ['post'])
@extend_schema_view(get= extend_schema(auth= []))
class PostListCreateAPIView(ListCreateAPIView):
    """
    게시물을 생성하고 조회하는 API
    """

    queryset = PostModel.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PostCurosrPagination

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


@extend_schema(tags= ['post'])
@extend_schema_view(get= extend_schema(auth= []))
class PostDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    특정 게시글을 조회, 수정, 삭제하는 API
    """

    queryset = PostModel.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]


@extend_schema(tags= ['comment'])
class CommentCreateAPIView(CreateAPIView):
    """
    댓글을 생성하는 API
    """

    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


@extend_schema(tags= ['comment'])
@extend_schema_view(get= extend_schema(auth= []))
class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    댓글을 조회, 수정, 삭제하는 API
    """

    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

