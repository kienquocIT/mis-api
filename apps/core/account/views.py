from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import UserUpdateSerializer, UserCreateSerializer, UserDetailSerializer

from apps.core.account.mixins import AccountListMixin, AccountCreateMixin
from apps.core.account.models import User
from apps.core.account.serializers import UserListSerializer
from apps.shared import ResponseController, mask_view, TypeCheck


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
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        data = request.data
        ser = UserCreateSerializer(data=data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(tenant_current=request.user.tenant_current)
        self.sync_new_user_to_map(obj, request.user.company_current_id)
        return ResponseController.created_201(
            data=UserDetailSerializer(obj).data,
        )

    @staticmethod
    def sync_new_user_to_map(user_obj, company_id):
        if user_obj and isinstance(user_obj, User) and company_id and TypeCheck.check_uuid(company_id):
            user_obj.sync_map(company_id)
            return True
        return False


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
