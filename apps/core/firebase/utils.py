from django.conf import settings
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError

from apps.core.firebase.models import DeviceToken


class FCMNotify:
    @classmethod
    def destroy_token_of_user(cls, user_obj):
        if user_obj:
            token_objs = DeviceToken.objects.filter(user=user_obj)
            if token_objs:
                token_objs.delete()
        return True

    @classmethod
    def send_fcm_notification(cls, user, title: str, body: str, data: dict = None):
        if settings.FIREBASE_ENABLE is True:
            token_obj = DeviceToken.objects.filter(user=user, is_active=True).first()
            if not token_obj:
                return {"success": False, "message": "No device tokens found for user"}

            device_tokens = token_obj.token
            if device_tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data,
                    token=device_tokens,
                )

                try:
                    messaging.send(message)
                except UnregisteredError as err:
                    print('err:', err)
                    # print('send_fcm_notification.err:', err, ',', 'token:', device_tokens)
                    token_obj.delete()
                    return False
                return True
        return False
