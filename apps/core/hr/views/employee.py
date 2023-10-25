from datetime import timedelta
from typing import Union

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, serializers, exceptions
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

# special import
from apps.sales.opportunity.models import OpportunitySaleTeamMember
# -- special import

from apps.core.hr.filters import EmployeeListFilter
from apps.core.hr.models import Employee, PlanEmployeeApp
from apps.core.hr.serializers.employee_serializers import (
    EmployeeListSerializer, EmployeeCreateSerializer,
    EmployeeDetailSerializer, EmployeeUpdateSerializer,
    EmployeeListByOverviewTenantSerializer, EmployeeListMinimalByOverviewTenantSerializer,
    EmployeeUploadAvatarSerializer, ApplicationOfEmployeeSerializer,
)
from apps.shared import (
    BaseUpdateMixin, mask_view, BaseRetrieveMixin, BaseListMixin, BaseCreateMixin, HRMsg,
    ResponseController, HttpMsg, TypeCheck,
)
from apps.shared.media_cloud_apis import APIUtil, MediaForceAPI


class EmployeeUploadAvatar(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(request_body=EmployeeUploadAvatarSerializer)
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, **kwargs):
        employee_obj = request.user.employee_current
        if employee_obj:
            ser = EmployeeUploadAvatarSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            uploaded_file = request.FILES.get('file')
            resp = MediaForceAPI.call_upload_avatar(employee_obj=employee_obj, f_img=uploaded_file)
            if resp.state:
                employee_obj.media_avatar_hash = resp.result['media_path_hash']
                employee_obj.save(update_fields=['media_avatar_hash'])
                return ResponseController.success_200(
                    data={'detail': HttpMsg.SUCCESSFULLY, 'media_path_hash': resp.result['media_path_hash']}
                )
            return ResponseController.bad_request_400(msg=resp.errors)
        return ResponseController.forbidden_403()


class EmployeeList(BaseListMixin, BaseCreateMixin):
    queryset = Employee.objects
    search_fields = ["search_content"]
    filterset_class = EmployeeListFilter

    serializer_list = EmployeeListSerializer
    serializer_detail = EmployeeListSerializer
    serializer_create = EmployeeCreateSerializer
    list_hidden_field = ('tenant_id', 'company_id')
    create_hidden_field = ('tenant_id', 'company_id')

    def get_queryset(self):
        return super().get_queryset().select_related('group').prefetch_related('role')

    def error_auth_require(self):
        return self.list_empty()

    @classmethod
    def get_config_from_opp_id_selected(cls, item_data, opp_id) -> Union[dict, None]:
        if item_data and isinstance(item_data, dict) and 'opp' in item_data and isinstance(item_data['opp'], dict):
            if str(opp_id) in item_data['opp']:
                return item_data['opp'][str(opp_id)]
        return None

    @classmethod
    def member_opp_ids_from_opp_id_selected(cls, opp_id) -> list:
        return OpportunitySaleTeamMember.objects.filter_current(
            fill__tenant=True, fill__company=True, opportunity_id=opp_id
        ).values_list('member_id', flat=True)

    @classmethod
    def get_config_from_prj_id_selected(cls, item_data, prj_id) -> Union[dict, None]:
        if item_data and isinstance(item_data, dict) and 'prj' in item_data and isinstance(item_data['prj'], dict):
            if str(prj_id) in item_data['prj']:
                return item_data['prj'][str(prj_id)]
        return None

    @classmethod
    def member_prj_ids_from_prj_id_selected(cls, prj_id) -> list:  # pylint: disable=W0613
        return []

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        """
        Check case get list opp for feature or list by configured.
        query_params: from_app=app_label-model_code
        """
        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        # check permit config exists if from_app not calling...
        if self.cls_check.permit_cls.config_data__exist:
            return self.filter_kwargs_q__from_config()
        return Q(id__in=[])

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:  # pylint: disable=R0914, R0912, R0915
        # permit_data = {"employee": [], "roles": []}
        key_filter = 'id__in'
        value_filter = []
        employee_attr = self.cls_check.employee_attr
        employee_current_id = employee_attr.employee_current_id if employee_attr else None

        if (  # pylint: disable=R1702
                isinstance(arr_from_app, list) and len(arr_from_app) == 3
                and employee_attr and employee_current_id
        ):
            opp_id = self.get_query_params().get('list_from_opp', None)
            prj_id = self.get_query_params().get('list_from_prj', None)
            config_by_code_kwargs = {
                'label_code': arr_from_app[0],
                'model_code': arr_from_app[1],
                'perm_code': arr_from_app[2],
            }

            if opp_id and TypeCheck.check_uuid(opp_id):
                permit_data = self.cls_check.permit_cls.config_data__by_code(**config_by_code_kwargs, has_roles=False)
                if 'employee' in permit_data:
                    config_by_opp = self.get_config_from_opp_id_selected(
                        item_data=permit_data['employee'],
                        opp_id=opp_id
                    )
                    if config_by_opp and isinstance(config_by_opp, dict):
                        if '4' in config_by_opp:
                            value_filter = self.member_opp_ids_from_opp_id_selected(opp_id=opp_id)
                        elif '1' in config_by_opp:
                            value_filter = [str(employee_current_id)]
                    if settings.DEBUG_PERMIT:
                        print('=> config_by_opp                :', '[HAS FROM APP][OPP]', config_by_opp)
            elif prj_id and TypeCheck.check_uuid(prj_id):
                permit_data = self.cls_check.permit_cls.config_data__by_code(**config_by_code_kwargs, has_roles=False)
                if 'employee' in permit_data:
                    config_by_prj = self.get_config_from_prj_id_selected(
                        item_data=permit_data['employee'],
                        prj_id=prj_id
                    )
                    if config_by_prj and isinstance(config_by_prj, dict):
                        if '4' in config_by_prj:
                            value_filter = self.member_prj_ids_from_prj_id_selected(prj_id=prj_id)
                        elif '1' in config_by_prj:
                            value_filter = [str(employee_current_id)]
                    if settings.DEBUG_PERMIT:
                        print('=> config_by_prj                :', '[HAS FROM APP][PRJ]', config_by_prj)
            else:
                permit_data = self.cls_check.permit_cls.config_data__by_code(**config_by_code_kwargs, has_roles=True)
                max_range_allowed = 0
                if 'employee' in permit_data:
                    if 'general' in permit_data['employee']:
                        general_data = permit_data['employee']['general']
                        if general_data and isinstance(general_data, dict):
                            try:
                                max_tmp = max(int(idx) for idx in general_data.keys())
                                if max_tmp > max_range_allowed:
                                    max_range_allowed = max_tmp
                            except ValueError:
                                pass
                if max_range_allowed < 4:
                    if 'roles' in permit_data:
                        roles_data = permit_data['roles']
                        if roles_data and isinstance(roles_data, list):
                            for role_item in roles_data:
                                if max_range_allowed == 4:  # break with is the highest level
                                    break

                                if 'general' in role_item:
                                    general_data = role_item['general']
                                    if general_data and isinstance(general_data, dict):
                                        try:
                                            max_tmp = max(int(idx) for idx in general_data.keys())
                                            if max_tmp > max_range_allowed:
                                                max_range_allowed = max_tmp
                                        except ValueError:
                                            pass
                if settings.DEBUG_PERMIT:
                    print('=> max_range_allowed            :', '[HAS FROM APP][general]', max_range_allowed)

                if max_range_allowed == 1:
                    value_filter = [str(employee_current_id)]
                elif max_range_allowed == 2:
                    value_filter = employee_attr.employee_staff_ids
                elif max_range_allowed == 3:
                    value_filter = employee_attr.employee_same_group_ids
                elif max_range_allowed == 4:
                    key_filter = 'company_id'
                    value_filter = employee_attr.company_id

            if settings.DEBUG_PERMIT:
                print('=> value_filter:                :', '[HAS FROM APP]', value_filter)

        if isinstance(value_filter, list):
            value_filter = list(set(value_filter))
        return Q(**{key_filter: value_filter})

    @swagger_auto_schema(
        operation_summary="Employee list",
        operation_description="Get employee list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
        skip_filter_employee=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create employee",
        operation_description="Create a new employee",
        request_body=EmployeeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='employee', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_obj': request.user.company_current
        }
        return self.create(request, *args, **kwargs)


class EmployeeDetail(BaseRetrieveMixin, BaseUpdateMixin, generics.GenericAPIView):
    queryset = Employee.objects
    serializer_detail = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    def error_auth_require(self):
        if (
                self.request.method == 'GET' and self.cls_auth_check and self.request.user.employee_current_id and
                self.kwargs.get('pk', None) == str(self.request.user.employee_current_id)
        ):
            self.state_skip_is_admin = True
            result_filter = {'id': self.request.user.employee_current_id}
            self.cls_auth_check.set_perm_filter_dict(result_filter)
            return result_filter
        return ResponseController.forbidden_403()

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee",
        operation_description="Update employee by ID",
        request_body=EmployeeUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EmployeeCompanyList(BaseListMixin, generics.GenericAPIView):
    queryset = Employee.objects
    filterset_fields = {'company_id': ['exact']}

    serializer_list = EmployeeListSerializer
    serializer_detail = EmployeeListSerializer
    list_hidden_field = ['tenant_id']

    def get_queryset(self):
        return super().get_queryset().select_related('group').prefetch_related('role')

    @swagger_auto_schema(
        operation_summary="Employee Company list",
        operation_description="Get employee Company list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EmployeeTenantList(BaseListMixin, generics.GenericAPIView):
    queryset = Employee.objects

    serializer_list = EmployeeListByOverviewTenantSerializer
    serializer_list_minimal = EmployeeListMinimalByOverviewTenantSerializer
    use_cache_minimal = True
    list_hidden_field = ['tenant_id']
    filterset_fields = {
        'company_id': ['exact', 'in'],
        'user': ['isnull'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'user'
        ).order_by('first_name')

    @swagger_auto_schema(
        operation_summary="Employee Company list",
        operation_description="Get employee Company list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
        skip_filter_employee=True,
    )
    def get(self, request, *args, **kwargs):
        if request.query_params.get('company_id', None) or request.query_params.get('company_id__in', None):
            return self.list(request, *args, **kwargs)
        raise serializers.ValidationError(
            {
                'detail': HRMsg.FILTER_COMPANY_ID_REQUIRED
            }
        )


class EmployeeMediaToken(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        if request.user.employee_current:
            employee_obj = request.user.employee_current
            access_token = employee_obj.media_access_token
            access_expired = employee_obj.media_access_token_expired
            if access_expired and access_expired > (timezone.now() + timedelta(minutes=10)) and access_token:
                return ResponseController.success_200(
                    data={
                        'access_token': employee_obj.media_access_token
                    }
                )
            refresh_token = employee_obj.media_refresh_token_expired
            refresh_expired = employee_obj.media_refresh_token_expired
            if refresh_token and refresh_expired and refresh_expired > (timezone.now() + timedelta(minutes=10)):
                access_token = APIUtil.get_new_token(
                    media_refresh_token=employee_obj.media_refresh_token,
                    employee_obj=employee_obj,
                )
                if access_token:
                    return ResponseController.success_200(
                        data={
                            'access_token': access_token
                        }
                    )
            access_token = APIUtil.get_new_token_by_login(employee_obj)
            if access_token:
                return ResponseController.success_200(
                    data={
                        'access_token': employee_obj.media_access_token
                    }
                )

        return ResponseController.forbidden_403()


class EmployeeAppList(BaseListMixin):
    queryset = PlanEmployeeApp.objects
    search_fields = ["application__title"]
    serializer_list = ApplicationOfEmployeeSerializer

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            'plan_employee__employee_id': self.kwargs['pk'],
        }

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        employee_id = self.kwargs['pk']
        try:
            employee_obj = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            raise exceptions.NotFound

        state = self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True)
        if state is True:
            return Q()
        return self.list_empty()

    @swagger_auto_schema(
        operation_summary="Application List of Employee",
        operation_description="Application List of Employee",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.list(request, *args, pk, **kwargs)
