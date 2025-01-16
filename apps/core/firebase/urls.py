from django.urls import path
from .views import FirebaseOfUser

urlpatterns = [
    path('control', FirebaseOfUser.as_view(), name='FirebaseOfUser'),
]
