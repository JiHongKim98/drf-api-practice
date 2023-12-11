from django.urls import path
from . import views

urlpatterns = [
    path("posts", views.PostAPIView.as_view()),
    path("posts/<int:pk>", views.PostAPIView.as_view()),
    path("comments", views.CommentAPIView.as_view()),
    path("comments/<int:pk>", views.CommentAPIView.as_view()),
]