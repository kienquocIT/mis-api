from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import UserUpdateSerializer, UserCreateSerializer, UserDetailSerializer

from apps.core.account.mixins import AccountListMixin, AccountCreateMixin
from apps.core.account.models import User
from apps.core.account.serializers import UserListSerializer
from apps.shared import ResponseController


# class UserList(
#     AccountListMixin,
#     AccountCreateMixin,
#     generics.GenericAPIView
# ):
#     permission_classes = [IsAuthenticated]
#     queryset = User.objects.select_related(
#         "tenant_current",
#     )
#     search_fields = ["full_name_search"]
#
#     serializer_class = UserListSerializer
#
#     serializer_create = UserCreateSerializer
class UserList(APIView):
    @swagger_auto_schema(
        operation_summary="User list",
    )
    def get(self, request, *args, **kwargs):
        tenant_current = request.user.tenant_current_id
        user = User.objects.filter(tenant_current=tenant_current)
        ser = UserListSerializer(data=user, many=True)
        ser.is_valid()
        return ResponseController.success_200(data=ser.data, key_data='result')
        # return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create New User', request_body=UserCreateSerializer)
    def post(self, request, *args, **kwargs):
        if request.user:
            data = request.data
            password = data['password']
            user = UserCreateSerializer(data=data)
            if user.is_valid():
                obj = user.save(tenant_current=request.user.tenant_current)
                obj.set_password(password)
                obj.save()
                return ResponseController.created_201(
                    data=user.data,
                )
            return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')
        return ResponseController.unauthorized_401()


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Detail User")
    def get_object(self, request, pk, *args, **kwargs):
        if request.user:
            user = User.objects.get(pk=pk)
            user = UserDetailSerializer(user)
            return ResponseController.success_200(data=user.data, key_data='result')
        return ResponseController.unauthorized_401()

    @swagger_auto_schema(operation_summary='Detail User')
    def get(self, request, pk, *args, **kwargs):
        if request.user:
            user = User.objects.get(pk=pk)
            user = UserDetailSerializer(user)
            return ResponseController.success_200(data=user.data, key_data='result')
        return ResponseController.unauthorized_401()

    @swagger_auto_schema(operation_summary="Update User", request_body=UserUpdateSerializer)
    def put(self, request, pk, *args, **kwargs):
        if request.user:
            user = User.objects.get(pk=pk)
            user = UserUpdateSerializer(instance=user, data=request.data)
            if user.is_valid():
                user.save()
                return ResponseController.success_200(
                    data=user.data,
                    key_data='result',
                )
            return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')
        return ResponseController.unauthorized_401()

    @swagger_auto_schema(operation_summary="Delete User")
    def delete(self, request, pk, *args, **kwargs):
        if request.user:
            user = User.objects.get(pk=pk)
            user.delete()
            return ResponseController.success_200({'detail': 'success'}, key_data='result')
        return ResponseController.unauthorized_401()
