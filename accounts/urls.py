from django.urls import path
from . import views

urlpatterns = [
    path("users", views.UserAPIView.as_view()),
    path("login", views.LoginAPIView.as_view()),
    path("logout", views.LogoutAPIView.as_view()),
    path("refresh", views.CustomTokenRefreshView.as_view()),
    path("activate/<str:uidb64>/<str:token>", views.EmailVerificationView.as_view()),
]