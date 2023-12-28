from django.urls import path
from accounts.views import (
    UserAPIView,
    LoginAPIView,
    LogoutAPIView,
    CustomTokenRefreshView,
    EmailVerificationView
)


urlpatterns = [
    path("users", UserAPIView.as_view()),
    path("login", LoginAPIView.as_view()),
    path("logout", LogoutAPIView.as_view()),
    path("refresh", CustomTokenRefreshView.as_view()),
    path("activate/<str:uidb64>/<str:token>", EmailVerificationView.as_view()),
]

