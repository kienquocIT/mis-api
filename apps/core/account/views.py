from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from .mixins import AccountCreateMixin, AccountDestroyMixin, AccountListMixin
from .serializers import UserUpdateSerializer, UserCreateSerializer, UserDetailSerializer, CompanyUserUpdateSerializer, \
    CompanyUserDetailSerializer
from apps.core.account.models import User
from apps.core.account.serializers import UserListSerializer
from apps.shared import mask_view, TypeCheck, BaseListMixin, BaseCreateMixin, BaseUpdateMixin, \
    BaseRetrieveMixin, BaseDestroyMixin


class UserList(AccountListMixin, AccountCreateMixin):
    """
        User List:
            GET: List
            POST: Create a new
        """
    queryset = User.objects.select_related('tenant_current')
    serializer_list = UserListSerializer
    serializer_create = UserCreateSerializer
    serializer_detail = UserDetailSerializer
    list_hidden_field = ['tenant_current_id']
    create_hidden_field = ['tenant_current_id']

    @swagger_auto_schema(
        operation_summary="User list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create New User', request_body=UserCreateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @staticmethod
    def sync_new_user_to_map(user_obj, company_id):
        if user_obj and isinstance(user_obj, User) and company_id and TypeCheck.check_uuid(company_id):
            user_obj.sync_map(company_id)
            return True
        return False


class UserDetail(BaseRetrieveMixin, BaseUpdateMixin, AccountDestroyMixin):

    permission_classes = [IsAuthenticated]
    queryset = User.objects.select_related('tenant_current')
    serializer_class = UserUpdateSerializer
    serializer_detail = UserDetailSerializer

    @swagger_auto_schema(operation_summary='Detail User')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update User", request_body=UserUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = UserUpdateSerializer
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete User")
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CompanyUserDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = User.objects.select_related('company_current')
    serializer_update = CompanyUserUpdateSerializer
    serializer_detail = CompanyUserDetailSerializer

    @swagger_auto_schema(
        operation_summary="User's Companies",
        operation_description="User's Companies",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add Or Delete User For Company",
        operation_description="Add Or Delete User For Company",
        request_body=CompanyUserUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = CompanyUserUpdateSerializer
        return self.update(request, *args, **kwargs)
