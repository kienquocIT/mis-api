from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path('api/', include('apps.core.urls')),
    path('api/', include('apps.sale.urls')),
    path('api/private-system/', include('apps.sharedapp.urls')),
    path('api/', include('apps.sales.urls')),
    path('django-admin/', admin.site.urls),
]

if getattr(settings, 'SHOW_API_DOCS', False):
    schema_view = get_schema_view(
        openapi.Info(
            title="MIS API",
            default_version='v1',
            description="",
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
    urlpatterns += [
                       path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-json'),
                       path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
                   ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG is True:
    urlpatterns.append(
        path('__debug__/', include('debug_toolbar.urls')),
    )
