from django.conf import settings
from django.conf.urls.static import static as base_static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import media_proxy

urlpatterns = [
    path('api/', include('apps.core.urls')),
    path('api/', include('apps.masterdata.urls')),
    path('api/private-system/', include('apps.sharedapp.urls')),
    path('api/', include('apps.sales.urls')),
    path('api/', include('apps.eoffice.urls')),
    path('django-admin/', admin.site.urls),
]

if getattr(settings, 'SHOW_API_DOCS', False):
    class CustomSchemaGenerator(OpenAPISchemaGenerator):
        def get_schema(self, request=None, public=False):
            schema = super().get_schema(request, public)

            paths = list(schema.paths.keys())
            for path_str in paths:
                try:
                    if path_str.startswith('/api/'):
                        operations = schema.paths[path_str]
                        for method, operation in operations.items():
                            if operation and hasattr(operation, 'tags'):
                                tags = operation.tags
                                if tags:
                                    new_path_str = path_str.replace('/api/', '')
                                    if new_path_str:
                                        new_tag = f"""ᓚᘏᗢ ↣ {path_str.replace('/api/', '').split('/')[0]}"""
                                        operation.tags = [new_tag]
                except Exception as errs:
                    print('[CustomSchemaGenerator][get_schema] Errors: ' + str(errs))

            return schema
    schema_view = get_schema_view(
        openapi.Info(
            title="MIS API",
            default_version='v1',
            description="",
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
        generator_class=CustomSchemaGenerator,
    )
    urlpatterns += \
        [
            path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-json'),
            path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        ]

if settings.DEBUG is True:
    urlpatterns.append(
        path('__debug__/', include('debug_toolbar.urls')),
    )

urlpatterns += base_static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not settings.USE_S3:
    urlpatterns += media_proxy.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
