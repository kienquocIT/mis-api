from django.urls import path

from apps.core.comment.views import CommentList, CommentRepliesList, RoomRepliesList

urlpatterns = [
    path('doc/<str:pk_doc>/<str:pk_app>/list', CommentList.as_view(), name='CommentList'),
    path('reply/<str:pk>/list', CommentRepliesList.as_view(), name='CommentRepliesList'),
    path('room/<str:pk>/list', RoomRepliesList.as_view(), name='RoomRepliesList'),
]
