from django.urls import path

from apps.core.web_builder.views.public import PublicProductListAPI

urlpatterns = [
    path('products', PublicProductListAPI.as_view(), name='PublicProductListAPI'),
]
