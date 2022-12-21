from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import User
from .serializers import UserListSerializer, UserUpdateSerializer, UserCreateSerializer, UserDetailSerializer

from apps.shared import ResponseController


class UserList(APIView):

    @swagger_auto_schema(operation_summary='User List')
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        users = UserListSerializer(users, many=True)
        return ResponseController.success_200(data=users.data, key_data='result')

    @swagger_auto_schema(operation_summary='Create New User', request_body=UserCreateSerializer)
    def post(self, request, *args, **kwargs):
        user = UserCreateSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return ResponseController.success_200(
                data=user.data,
                key_data='result',
            )
        return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Detail User")
    def get_object(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            user = UserDetailSerializer(user)
            return ResponseController.success_200(data=user.data, key_data='result')
        except:
            return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')

    @swagger_auto_schema(operation_summary='Detail User')
    def get(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        user = UserDetailSerializer(user)
        return ResponseController.success_200(data=user.data, key_data='result')

    @swagger_auto_schema(operation_summary="Update User", request_body=UserUpdateSerializer)
    def put(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        user = UserUpdateSerializer(instance=user, data=request.data)
        if user.is_valid():
            user.save()
            return ResponseController.success_200(
                data=user.data,
                key_data='result',
            )
        return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')

    @swagger_auto_schema(operation_summary="Delete User")
    def delete(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            user = UserDetailSerializer(user)
            return ResponseController.success_200(data=user.data, key_data='result')
        except:
            return ResponseController.bad_request_400(msg='User does not exist')
