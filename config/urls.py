from django.contrib import admin
from django.urls import path, include

api_urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('boards/', include('boards.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
]

