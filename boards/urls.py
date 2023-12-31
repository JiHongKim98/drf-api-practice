from django.urls import path

from boards.views import (
    CommentCreateAPIView,
    CommentDetailAPIView,
    PostDetailAPIView,
    PostListCreateAPIView,
)

urlpatterns = [
    path("posts", PostListCreateAPIView.as_view()),
    path("posts/<int:pk>", PostDetailAPIView.as_view()),
    path("comments", CommentCreateAPIView.as_view()),
    path("comments/<int:pk>", CommentDetailAPIView.as_view()),
]
