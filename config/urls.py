from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularYAMLAPIView
)


api_urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('boards/', include('boards.urls')),
]

docs_urlpatterns = [
    path("json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
    path("yaml/", SpectacularYAMLAPIView.as_view(), name="swagger-yaml"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema-json"), name="swagger-ui",),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema-json"), name="redoc",),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
    path('docs/', include(docs_urlpatterns)),
]

