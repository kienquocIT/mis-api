import abc
import datetime

import requests
from django.utils import timezone

from rest_framework import serializers

from apps.core.chat3rd.models import ZaloToken
from apps.core.chat3rd.utils.zalo_serializer import ZaloEventSerializer
from apps.shared.extends.env import get_env_var


class ZaloAccessTokenSerializer(serializers.Serializer):  # noqa
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expire_in = serializers.CharField()


class ZaloAbstract(abc.ABC):
    schema: str
    domain: str
    fb_version: str
    _url: str or None

    @property
    def url(self):
        if self._url is None:
            self._url = f'{self.schema.lower()}://{self.domain.lower()}/{self.fb_version.lower()}'
        return self._url

    def __init__(self, schema: str = 'https', domain: str = 'oauth.zaloapp.com', fb_version: str = 'v4', **kwargs):
        self.schema = schema
        self.domain = domain
        self.fb_version = fb_version
        self._url = None


class ZaloIntegrate(ZaloAbstract):
    code: str
    oa_id: str

    def __init__(self, code: str, oa_id: str, **kwargs):
        self.code = code
        self.oa_id = oa_id
        super().__init__(**kwargs)

    def get_access_token(self, tenant_id, company_id, employee_id):
        final_url = f'{self.url}/oa/access_token'
        data = {
            "code": self.code,
            "app_id": get_env_var('ZALO_APP_ID', ''),
            "grant_type": "authorization_code",
            "code_verifier": get_env_var('ZALO_CODE_VERIFIER', ''),
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "secret_key": get_env_var("ZALO_APP_SECRET", ""),
        }

        response = requests.post(final_url, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            ser = ZaloAccessTokenSerializer(data=response.json())
            ser.is_valid(raise_exception=False)
            if ser.errors:
                validated_data = ser.validated_data
                obj_token, _created = ZaloToken.objects.get_or_create(
                    company_id=company_id,
                    defaults={
                        'tenant_id': tenant_id,
                        'company_id': company_id,
                        'employee_created_id': employee_id,
                    }
                )
                obj_token.access_token = validated_data['access_token']
                obj_token.refresh_token = validated_data['refresh_token']
                obj_token.expires = timezone.now() + datetime.timedelta(seconds=int(validated_data['expire_in']))
                obj_token.employee_modified_id = employee_id
                obj_token.save()
                return obj_token
        return None


class ZaloAPI(ZaloAbstract):
    token_obj: ZaloToken

    def __init__(self, token_obj: ZaloToken, **kwargs):
        self.token_obj = token_obj
        super().__init__(**kwargs)


# "app_id": "989770863593126172",
#   "user_id_by_app": "6666690530530794071",
#   "event_name": "user_send_gif",
#   "timestamp": "1736995879452",
#   "sender": {
#     "id": "2661892529877279381"
#   },
#   "recipient": {
#     "id": "579745863508352884"
#   },
class ZaloMessageWebHooks:
    data: dict

    def __init__(self, data):
        self.data = data

    def validate(self):
        ser = ZaloEventSerializer(data=self.data)
        ser.is_valid(raise_exception=True)
        return ser.validated_data
