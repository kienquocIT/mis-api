from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared import mask_view, ResponseController

from .models import DeviceToken


class FirebaseOfUser(APIView):
    @swagger_auto_schema(operation_summary='Register Device Token')
    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        user = request.user
        if user and hasattr(user, 'id'):
            token_obj = None

            old_id = request.data.get("old_id", None)
            if old_id:
                try:
                    token_obj = DeviceToken.objects.get_current(user=user, pk=old_id)
                except DeviceToken.DoesNotExist:
                    pass

            token = request.data.get("token", None)
            if token:
                try:
                    if token_obj:
                        token_obj.token = token
                        token_obj.is_active = True
                        token_obj.save()
                    else:
                        device_info = request.data.get("device_info", None)
                        token_obj, create = DeviceToken.objects.get_or_create(
                            tenant=user.tenant_current,
                            company=user.company_current,
                            user=user, token=token, defaults={'device_info': device_info, 'is_active': True},
                        )
                        if create is False:
                            token_obj.date_modified = timezone.now()
                            token_obj.is_active = True
                            token_obj.save()
                except Exception as err:
                    print('[FirebaseOfUser][post] err:', str(err))

            if token_obj:
                return ResponseController.created_201(
                    data={
                        'id': str(token_obj.id),
                    }
                )
        return ResponseController.bad_request_400()
