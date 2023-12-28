from django.urls import path
from boards.views import (
    PostListCreateAPIView,
    PostDetailAPIView,
    CommentCreateAPIView,
    CommentDetailAPIView
)

urlpatterns = [
    path("posts", PostListCreateAPIView.as_view()),
    path("posts/<int:pk>", PostDetailAPIView.as_view()),
    path("comments", CommentCreateAPIView.as_view()),
    path("comments/<int:pk>", CommentDetailAPIView.as_view()),
]

