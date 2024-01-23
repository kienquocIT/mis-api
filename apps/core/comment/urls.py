from django.urls import path

from apps.core.comment.views import CommentList

urlpatterns = [
    path('doc/<str:pk_doc>/<str:pk_app>/list', CommentList.as_view(), name='CommentList'),
]
