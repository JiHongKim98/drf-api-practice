from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)

from boards.models import PostModel, CommentModel
from boards.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer
)
from boards.permissions import IsOwnerOrReadOnly
from boards.paginations import PostCurosrPagination


class PostListCreateAPIView(ListCreateAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PostCurosrPagination

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


class PostDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]


class CommentCreateAPIView(CreateAPIView):
    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

