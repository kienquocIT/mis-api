from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions

from apps.shared import (
    mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
    TypeCheck, ResponseController,
)

from apps.core.mailer.models import MailTemplate, MailTemplateSystem
from apps.core.mailer.serializers import (
    MailTemplateListSerializer, MailTemplateDetailSerializer,
    MailTemplateCreateSerializer, MailTemplateUpdateSerializer, MailTemplateSystemDetailSerializer,
    MailTemplateSystemUpdateSerializer,
)


class MailerConfigList(BaseListMixin, BaseCreateMixin):
    queryset = MailTemplate.objects
    serializer_list = MailTemplateListSerializer
    serializer_create = MailTemplateCreateSerializer
    serializer_detail = MailTemplateDetailSerializer

    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=MailTemplateCreateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MailerConfigDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = MailTemplate.objects
    serializer_detail = MailTemplateDetailSerializer
    serializer_update = MailTemplateUpdateSerializer

    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=MailTemplateUpdateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class MailerSystemGetByCode(BaseRetrieveMixin):
    queryset = MailTemplateSystem.objects
    serializer_detail = MailTemplateSystemDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_object(self):
        user_obj = self.request.user
        if user_obj and hasattr(user_obj, 'tenant_current_id') and hasattr(user_obj, 'company_current_id'):
            return MailTemplateSystem.template_get_or_create(
                tenant_id=user_obj.tenant_current_id,
                company_id=user_obj.company_current_id,
                system_code=self.kwargs['system_code'],
            )
        raise exceptions.NotFound

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, system_code, **kwargs):
        return self.retrieve(request, *args, system_code, **kwargs)


class MailerSystemDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = MailTemplateSystem.objects
    serializer_detail = MailTemplateSystemDetailSerializer
    serializer_update = MailTemplateSystemUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.retrieve(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(request_body=MailTemplateSystemUpdateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()
