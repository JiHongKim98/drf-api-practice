from django.urls import path
from . import views

urlpatterns = [
    path("users", views.UserAPIView.as_view()),
    path("login", views.login),
    path("logout", views.logout),
    path("refresh", views.CustomTokenRefreshView.as_view()),
]