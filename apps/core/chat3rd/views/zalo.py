import base64
import hashlib
import json
import os

from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.core.chat3rd.utils import ZaloIntegrate, ZaloEventSerializer
from apps.shared import mask_view, ResponseController
from apps.shared.extends.env import get_env_var


class ZaloWebHooks(APIView):
    @staticmethod
    def generate_code_verifier():
        # Tạo chuỗi ngẫu nhiên dài 43 ký tự
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
        return code_verifier

    @staticmethod
    def generate_code_challenge(code_verifier):
        # Băm code_verifier bằng SHA-256
        sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        # Mã hóa kết quả theo Base64 URL-encoded và loại bỏ ký tự '='
        code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
        return code_challenge

    def get(self, request, *args, **kwargs):
        # code_verifier = xYEomLkJorfJeALHx5dSEeeBNlbnSnA7fynIfo5pEEE
        # code_challenge = hDZL9bVaBN2kYbZrYZJqTVDZm1dtHeQGcEnf9mh-c-U
        # state = KJpDrqApxN7YQFeX
        code_verifier = get_env_var('ZALO_CODE_VERIFIER', default=None)
        if code_verifier:
            ...
        return HttpResponse('Code verifier token mismatch', status=403)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        print('ZaloWebHooks:', data)
        ser = ZaloEventSerializer(data=data)
        ser.is_valid(raise_exception=False)
        if ser.errors:
            ser.save()
        return HttpResponse('Webhooks is ready!', status=200)


class ZaloConnect(APIView):
    @swagger_auto_schema(operation_summary='Get status Connect to Messenger')
    @mask_view(
        login_require=True,
    )
    def get(self, request, *args, **kwargs):
        # user_obj = request.user
        # if user_obj and hasattr(user_obj, 'company_current'):
        #     try:
        #         obj_token = MessengerToken.objects.get(
        #             tenant_id=user_obj.tenant_current_id,
        #             company_id=user_obj.company_current_id,
        #         )
        #     except MessengerToken.DoesNotExist:
        #         return ResponseController.notfound_404()
        #     if obj_token.expires is None or (obj_token.expires and obj_token.expires > timezone.now()):
        #         pages = [
        #             {
        #                 'id': obj.id,
        #                 'name': obj.name,
        #                 'account_id': obj.account_id,
        #                 'picture': obj.picture,
        #                 'link': obj.link,
        #             }
        #             for obj in MessengerPageToken.objects.filter(
        #                 parent=obj_token,
        #                 tenant_id=user_obj.tenant_current_id,
        #                 company_id=user_obj.company_current_id,
        #             )
        #         ]
        #         return ResponseController.success_200(
        #             data={
        #                 'id': obj_token.id,
        #                 'is_syncing': obj_token.is_syncing,
        #                 'is_sync_accounts': obj_token.is_sync_accounts,
        #                 'pages': pages,
        #                 'expires': obj_token.expires.strftime('%Y-%m-%d %H:%M:%S') if obj_token.expires else None,
        #             }
        #         )
        #     raise serializers.ValidationError(
        #         {
        #             'token': 'Expired',
        #         }
        #     )
        return ResponseController.notfound_404()

    @swagger_auto_schema(operation_summary='Build connect to Messenger')
    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'company_current'):
            code = request.data.get('code', None)
            oa_id = request.data.get('oa_id', None)
            if code and oa_id:
                token_obj = ZaloIntegrate(code=code, oa_id=oa_id).get_access_token(
                    tenant_id=user_obj.tenant_current_id,
                    company_id=user_obj.company_current_id,
                    employee_id=user_obj.employee_current_id,
                )
                if token_obj:
                    token_obj.oa_id = oa_id
                    token_obj.is_syncing = True
                    token_obj.save(update_fields=['is_syncing', 'oa_id'])
                    return ResponseController.success_200(
                        data={
                            'result': 'success',
                        }
                    )
            return ResponseController.notfound_404()
        return ResponseController.forbidden_403()
