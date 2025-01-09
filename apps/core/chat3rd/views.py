from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView

from apps.core.chat3rd.models import MessengerToken, MessengerPageToken, MessengerMessage, MessengerPerson
from apps.core.chat3rd.serializers import (
    MessengerPersonListSerializer, MessengerMessageListSerializer,
    MessengerPersonLinkToContactSerializer, MessengerPersonLinkToLeadSerializer,
)
from apps.core.chat3rd.tasks import messenger_scan_account_token
from apps.core.chat3rd.utils import GraphFbMigrate, FB_MAX_CALL_PER_HOUR, get_called
from apps.shared import mask_view, ResponseController, call_task_background, TypeCheck, BaseListMixin, BaseUpdateMixin


class MessengerLimit(APIView):
    @swagger_auto_schema(operation_summary='Get limit of company for Facebook API')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and hasattr(request.user, 'company_current_id'):
            company_id = request.user.company_current_id
            if company_id:
                return ResponseController.success_200(data={
                    'max': FB_MAX_CALL_PER_HOUR,
                    'used': get_called(company_id=company_id),
                })
            return ResponseController.forbidden_403()
        return ResponseController.unauthorized_401()


class MessengerConnect(APIView):
    @swagger_auto_schema(operation_summary='Get status Connect to Messenger')
    @mask_view(
        login_require=True,
    )
    def get(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'company_current'):
            try:
                obj_token = MessengerToken.objects.get(
                    tenant_id=user_obj.tenant_current_id,
                    company_id=user_obj.company_current_id,
                )
            except MessengerToken.DoesNotExist:
                return ResponseController.notfound_404()
            if obj_token.expires is None or (obj_token.expires and obj_token.expires > timezone.now()):
                pages = [
                    {
                        'id': obj.id,
                        'name': obj.name,
                        'account_id': obj.account_id,
                        'picture': obj.picture,
                        'link': obj.link,
                    }
                    for obj in MessengerPageToken.objects.filter(
                        parent=obj_token,
                        tenant_id=user_obj.tenant_current_id,
                        company_id=user_obj.company_current_id,
                    )
                ]
                return ResponseController.success_200(
                    data={
                        'id': obj_token.id,
                        'is_syncing': obj_token.is_syncing,
                        'is_sync_accounts': obj_token.is_sync_accounts,
                        'pages': pages,
                        'expires': obj_token.expires.strftime('%Y-%m-%d %H:%M:%S') if obj_token.expires else None,
                    }
                )
            raise serializers.ValidationError(
                {
                    'token': 'Expired',
                }
            )
        return ResponseController.notfound_404()

    @swagger_auto_schema(operation_summary='Build connect to Messenger')
    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'company_current'):
            code = request.data.get('code', None)
            redirect_uri = request.data.get('redirect_uri', None)
            if code and redirect_uri:
                token_obj = GraphFbMigrate(code=code, redirect_uri=redirect_uri).get_token_long_lived(
                    tenant_id=user_obj.tenant_current_id,
                    company_id=user_obj.company_current_id,
                    employee_id=user_obj.employee_current_id,
                )
                if token_obj:
                    if token_obj.is_syncing is False:
                        token_obj.is_syncing = True
                        token_obj.save(update_fields=['is_syncing'])
                        call_task_background(
                            my_task=messenger_scan_account_token,
                            **{
                                'messenger_id': str(token_obj.id),
                            }
                        )
                        return ResponseController.success_200(
                            data={
                                'result': 'success',
                            }
                        )
                    raise serializers.ValidationError(
                        {
                            'is_syncing': 'The syncing process is running',
                        }
                    )
            return ResponseController.notfound_404()
        return ResponseController.forbidden_403()


class MessengerAccountSync(APIView):
    @swagger_auto_schema(operation_summary='Sync page from User Token')
    @mask_view(login_require=True)
    def post(self, request, *args, pk, **kwargs):
        print('pk:', pk)
        try:
            token_obj = MessengerToken.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
        except MessengerToken.DoesNotExist:
            return ResponseController.notfound_404()

        token_obj.is_syncing = True
        token_obj.save(update_fields=['is_syncing'])
        call_task_background(
            my_task=messenger_scan_account_token,
            **{
                'messenger_id': str(token_obj.id),
            }
        )
        return ResponseController.success_200(
            data={
                'result': 'ok',
            }
        )


class MessengerPersonView(BaseListMixin):
    @classmethod
    def get_page(cls, pk):
        try:
            return MessengerPageToken.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
        except MessengerPageToken.DoesNotExist:
            pass
        return None

    queryset = MessengerPerson.objects
    serializer_list = MessengerPersonListSerializer

    @swagger_auto_schema(operation_summary='Get person interaction with Page')
    @mask_view(login_require=True)
    def get(self, request, *args, page_id, **kwargs):
        if page_id and TypeCheck.check_uuid(page_id):
            page_obj = self.get_page(pk=page_id)
            if page_obj:
                return self.list(request, *args, page_id, **kwargs)
        return ResponseController.notfound_404()


class MessengerPersonChats(BaseListMixin):
    @classmethod
    def get_page(cls, pk):
        try:
            return MessengerPageToken.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
        except MessengerPageToken.DoesNotExist:
            pass
        return None

    @classmethod
    def get_person(cls, pk):
        try:
            return MessengerPerson.objects.filter_current(fill__tenant=True, fill__company=True, pk=pk)
        except MessengerPerson.DoesNotExist:
            pass
        return None

    queryset = MessengerMessage.objects.select_related('person')
    serializer_list = MessengerMessageListSerializer

    @swagger_auto_schema(operation_summary='Get person chat with Page')
    @mask_view(login_require=True)
    def get(self, request, *args, page_id, person_id, **kwargs):
        if page_id and person_id and TypeCheck.check_uuid(page_id) and TypeCheck.check_uuid(person_id):
            page_obj = self.get_page(pk=page_id)
            if page_obj:
                person_obj = self.get_person(pk=person_id)
                if person_obj:
                    return self.list(request, *args, page_id, person_id, **kwargs)
        return ResponseController.notfound_404()


class MessengerPersonDetailContact(BaseUpdateMixin):
    queryset = MessengerPerson.objects
    serializer_update = MessengerPersonLinkToContactSerializer
    update_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Update person with Contact')
    @mask_view(login_require=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class MessengerPersonDetailLead(BaseUpdateMixin):
    queryset = MessengerPerson.objects
    serializer_update = MessengerPersonLinkToLeadSerializer
    update_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Update person with Lead')
    @mask_view(login_require=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
