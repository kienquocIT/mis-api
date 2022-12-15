from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.provisioning.serializers import ProvisioningCreateNewTenant, ProvisioningUserData, TenantListSerializer, \
    TenantListViewSerializer
from apps.core.provisioning.utils import TenantController
from apps.core.tenant.models import Tenant
from apps.shared import ResponseController, ProvisioningMsg


class NewTenant(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary='Tenant List')
    def get(self, request, *args, **kwargs):
        tenants = Tenant.objects.all()
        ser = TenantListViewSerializer(tenants, many=True)
        return ResponseController.success_200(data=ser.data, key_data='result')

    @swagger_auto_schema(
        operation_summary='Allow Provisioning Server call "Create New Tenant".',
        operation_description='''Provisioning config: 
        - settings: ALLOWED_IP_PROVISIONING, PROVISIONING_PATH_PREFIX
        - (no longer supported) table record: AllowedIPProvisioning''',
        request_body=ProvisioningCreateNewTenant
    )
    def post(self, request, *args, **kwargs):
        req_body_eg = {
            'tenant_data': {
                'title': 'Cong Ty Co Phan Minh Tam Solution',
                'code': 'MIS',
                'sub_domain': 'mis',
                'representative_fullname': 'Nguyen Van A',
                'representative_phone_number': '0987654321',
                'user_request_created': {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "full_name": "string",
                    "email": "string",
                    "phone": "string"
                },
                'auto_create_company': True,
                'company_quality_max': 5,
            },
            'employee_data': {
                'first_name': 'Nguyen Van',
                'last_name': 'A',
                'email': 'a@mis.com.vn',
                'phone': '0988776655',
            },
            'user_data': {
                'username': 'mis',
                'password': '111111',
            },
            'create_admin': True,
        }

        ser = ProvisioningCreateNewTenant(data=request.data)
        ser.is_valid(raise_exception=True)

        tenant_code = ser.validated_data['tenant_data'].pop('code')
        auto_create_company = ser.validated_data['tenant_data']['auto_create_company']
        user_data = ser.validated_data['user_data'] if ser.validated_data['create_admin'] else None
        create_employee = ser.validated_data['create_employee']
        plan_data = ser.validated_data['plan_data']

        tenant_controller = TenantController()
        is_success = tenant_controller.setup_new(
            tenant_code=tenant_code,
            tenant_data=ser.validated_data['tenant_data'],
            user_data=user_data,
            create_company=auto_create_company,
            create_employee=create_employee,
            plan_data=plan_data
        )
        if is_success is True:
            return ResponseController.success_200(
                TenantListSerializer(tenant_controller.tenant_obj).data,
                key_data='result',
            )
        return ResponseController.bad_request_400(msg='Setup new tenant was raised undefined error.')


class TenantNewAdmin(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary='Create New Tenant Admin', request_body=ProvisioningUserData)
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            tenant_obj = Tenant.objects.filter(pk=pk).first()
            if tenant_obj:
                if tenant_obj.admin_created is True or tenant_obj.admin:
                    raise serializers.ValidationError({
                        'tenant': ProvisioningMsg.TENANT_ADMIN_READY
                    })
                ser = ProvisioningUserData(data=request.data)
                ser.is_valid(raise_exception=True)
                tenant_controller = TenantController()
                tenant_controller.tenant_obj = tenant_obj
                tenant_controller.setup_user(dict(ser.validated_data))
                return ResponseController.success_200(
                    TenantListSerializer(tenant_controller.tenant_obj).data,
                    key_data='result',
                )
        return ResponseController.notfound_404()
