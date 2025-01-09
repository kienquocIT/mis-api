import hmac
import json
import hashlib
from django.http import HttpResponse
from rest_framework.views import APIView

from apps.core.chat3rd.utils import MessengerControl
from apps.shared.extends.env import get_env_var


class MessengerWebHooks(APIView):
    def get_header_signature(self):
        signature_data = self.request.headers.get("x-hub-signature-256", "")
        if signature_data and '=' in signature_data:
            return signature_data.split('=')[-1]
        return ""

    def valid_signature(self) -> bool:
        messenger_key = get_env_var('MESSENGER_APP_SECRET', default=None)

        if messenger_key:
            header_signature = self.get_header_signature()

            if header_signature:
                key_encode = messenger_key.encode('utf-8')
                body = self.request.body
                expected_hash = hmac.new(key_encode, body, hashlib.sha256).hexdigest()

                if header_signature == expected_hash:
                    return True
        return False

    def get(self, request, *args, **kwargs):
        verify_token = get_env_var('MESSENGER_VERIFY_TOKEN', default=None)
        if verify_token:
            mode = request.GET.get('hub.mode', None)
            token = request.GET.get('hub.verify_token', None)
            challenge = request.GET.get('hub.challenge', None)
            if mode and token and challenge and mode == 'subscribe' and token == verify_token:
                return HttpResponse(challenge, status=200)
        return HttpResponse('Verification token mismatch', status=403)

    def post(self, request, *args, **kwargs):
        if self.valid_signature():
            payload = json.loads(request.body)
            print('payload:', json.dumps(payload))
            data = json.loads(request.body.decode('utf-8'))
            MessengerControl(data=data).active()
            return HttpResponse('EVENT_RECEIVED', status=200)
        return HttpResponse('Verification token mismatch', status=403)
