from django.urls import path

from apps.core.web_builder.views.public import PublicProductListAPI, ProductDetailAPI

urlpatterns = [
    path('products', PublicProductListAPI.as_view(), name='PublicProductListAPI'),
    path('product/<str:pk>', ProductDetailAPI.as_view(), name='ProductDetailAPI'),
]
