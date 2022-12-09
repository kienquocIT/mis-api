from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.provisioning.serializers import ProvisioningCreateNewTenant
from apps.core.provisioning.utils import TenantController
from apps.shared import ResponseController


class NewTenant(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_client_ip(request):
        """No longer supported , replace with middleware check"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def is_allowed_ip(ip_client):
        """No longer supported , replace with middleware check"""
        if ip_client in settings.ALLOWED_IP_PROVISIONING:
            return True
        return False

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
        }

        ser = ProvisioningCreateNewTenant(data=request.data)
        ser.is_valid(raise_exception=True)

        tenant_code = ser.validated_data['tenant_data'].pop('code')
        is_success = TenantController().setup_new(
            tenant_code=tenant_code,
            tenant_data=ser.validated_data['tenant_data'],
            employee_data=ser.validated_data['employee_data'],
            user_data=ser.validated_data['user_data'],
        )
        if is_success is True:
            return ResponseController.success_200({'data': 'successful'}, key_data='result')
        return ResponseController.bad_request_400(msg='Setup new tenant was raised undefined error.')
