from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="T900 WEB API",
        default_version='v1',
    ),
    url=settings.API_URL
)
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # http://localhost:8000/
    # path('', index_view, name='index'),

    # http://localhost:8000/api/v1/<router-viewsets>
    path('api/v1/', include('api.api')),

    # http://localhost:8000/api/admin/
    path('', admin.site.urls),

    # http://localhost:8000/api/admin/
    # re_path('^.*$', index_view, name='index'),

]


