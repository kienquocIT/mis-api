from django.urls import path

from .views import AssetToolConfigDetail

urlpatterns = [
    path('config', AssetToolConfigDetail.as_view(), name='AssetToolConfigDetail'),
]
