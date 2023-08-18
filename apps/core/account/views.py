from drf_yasg.utils import swagger_auto_schema

from rest_framework import exceptions

from apps.shared import mask_view, TypeCheck, BaseUpdateMixin, BaseRetrieveMixin, exceptions_more
from apps.core.company.models import CompanyUserEmployee

from .mixins import AccountCreateMixin, AccountDestroyMixin, AccountListMixin
from .serializers import (
    UserUpdateSerializer, UserCreateSerializer, UserDetailSerializer,
    CompanyUserDetailSerializer, UserListSerializer, UserListTenantOverviewSerializer,
    CompanyUserEmployeeUpdateSerializer, UserResetPasswordSerializer,
)
from .models import User


class UserList(AccountListMixin, AccountCreateMixin):
    """
        User List:
            GET: List
            POST: Create a new
        """
    queryset = User.objects
    serializer_list = UserListSerializer
    serializer_list_minimal = UserListSerializer
    use_cache_queryset = True
    use_cache_minimal = True
    serializer_create = UserCreateSerializer
    serializer_detail = UserDetailSerializer
    list_hidden_field = ['tenant_current_id']
    create_hidden_field = ['tenant_current_id']
    search_fields = ('full_name_search', 'email', 'username')
    filterset_fields = ('email', 'username', 'first_name', 'last_name')

    def filter_append_manual(self):
        if self.request.user.company_current_id:
            return {
                'id__in': CompanyUserEmployee.all_user_of_company(self.request.user.company_current_id)
            }
        raise exceptions_more.Empty200

    @swagger_auto_schema(
        operation_summary="User list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create New User', request_body=UserCreateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @staticmethod
    def sync_new_user_to_map(user_obj, company_id):
        if user_obj and isinstance(user_obj, User) and company_id and TypeCheck.check_uuid(company_id):
            user_obj.sync_map(company_id)
            return True
        return False


class UserDetail(BaseRetrieveMixin, BaseUpdateMixin, AccountDestroyMixin):
    queryset = User.objects
    serializer_class = UserUpdateSerializer
    serializer_detail = UserDetailSerializer
    serializer_update = UserUpdateSerializer

    def filter_append_manual(self):
        if self.request.user.company_current_id:
            return {
                'id__in': CompanyUserEmployee.all_user_of_company(self.request.user.company_current_id)
            }
        raise exceptions.NotFound

    @swagger_auto_schema(operation_summary='Detail User')
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update User", request_body=UserUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete User")
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserDetailResetPassword(BaseUpdateMixin):
    queryset = User.objects
    serializer_detail = UserDetailSerializer
    serializer_update = UserResetPasswordSerializer

    def get_queryset(self):
        return super().get_queryset().filter_current(
            fill__tenant=True, fill__map_key={
                'fill__tenant': 'tenant_current_id',
            }
        )

    @swagger_auto_schema(operation_summary="Reset password of User", request_body=UserResetPasswordSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CompanyUserDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = User.objects.select_related('company_current')
    serializer_update = CompanyUserEmployeeUpdateSerializer
    serializer_detail = CompanyUserDetailSerializer

    @swagger_auto_schema(
        operation_summary="User's Companies",
        operation_description="User's Companies",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add Or Delete User For Company",
        operation_description="Add Or Delete User For Company",
        request_body=CompanyUserEmployeeUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class UserOfTenantList(AccountListMixin):
    queryset = User.objects
    serializer_list = UserListTenantOverviewSerializer
    serializer_list_minimal = UserListSerializer
    use_cache_queryset = True
    use_cache_minimal = True
    serializer_create = UserCreateSerializer
    serializer_detail = UserDetailSerializer
    list_hidden_field = ['tenant_current_id']
    create_hidden_field = ['tenant_current_id']
    search_fields = ('username', 'first_name', 'last_name')

    def get_queryset(self):
        return self.queryset.prefetch_related('company_user_employee_set_user').order_by('first_name')

    @swagger_auto_schema()
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
