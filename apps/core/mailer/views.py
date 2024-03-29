from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.parsers import MultiPartParser

from django.utils.translation import gettext_lazy as _

from apps.core.mailer.mail_control import SendMailController
from apps.shared import (
    mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
    TypeCheck, ResponseController, MailMsg, DisperseModel,
)

from apps.core.mailer.models import MailTemplate, MailTemplateSystem, MailConfig
from apps.core.mailer.serializers import (
    MailTemplateListSerializer, MailTemplateDetailSerializer,
    MailTemplateCreateSerializer, MailTemplateUpdateSerializer, MailTemplateSystemDetailSerializer,
    MailTemplateSystemUpdateSerializer, MailConfigDetailSerializer, MailConfigUpdateSerializer,
    MailTestConnectDataSerializer,
)


class MailerFeatureAppList(BaseListMixin):
    queryset = MailTemplate.objects
    serializer_list = MailTemplateListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        result = []
        app_ids = list(
            MailTemplate.objects.filter_current(fill__tenant=True, fill__company=True).values_list(
                'application', flat=True
            ).distinct()
        )
        app_cls = DisperseModel(app_model='base.application').get_model()
        if app_ids and app_cls:
            result = [
                {
                    'id': str(obj.id),
                    'title': _(str(obj.title)),
                    'code': str(obj.code)
                } for obj in app_cls.objects.filter(id__in=app_ids).order_by('title')
            ]
        return ResponseController.success_200(data=result)


class MailerFeatureList(BaseListMixin, BaseCreateMixin):
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


class MailTemplateByApplication(BaseListMixin):
    queryset = MailTemplate.objects
    serializer_list = MailTemplateListSerializer
    serializer_create = MailTemplateCreateSerializer
    serializer_detail = MailTemplateDetailSerializer

    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, application_id, **kwargs):
        return self.list(request, *args, application_id, **kwargs)


class MailerFeatureDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
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
            return MailTemplateSystem.get_config(
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


class MailerServerConfigGet(BaseRetrieveMixin):
    queryset = MailConfig.objects
    serializer_detail = MailConfigDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_object(self):
        user_obj = self.request.user
        if user_obj and hasattr(user_obj, 'tenant_current_id') and hasattr(user_obj, 'company_current_id'):
            return MailConfig.get_config(tenant_id=user_obj.tenant_current_id, company_id=user_obj.company_current_id)
        raise exceptions.NotFound

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MailerServerConfigDetail(BaseUpdateMixin):
    parser_classes = [MultiPartParser]
    queryset = MailConfig.objects
    serializer_detail = MailConfigDetailSerializer
    serializer_update = MailConfigUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['tenant_id', 'company_id']

    def write_log(self, *args, **kwargs):
        body_data = self.request.data
        if 'ssl_key' in body_data:
            body_data['ssl_key'] = "{EXIST_FILE}"
        if 'ssl_cert' in body_data:
            body_data['ssl_cert'] = "{EXIST_FILE}"
        kwargs['request_data'] = body_data
        return super().write_log(*args, **kwargs)

    def resolve_partial(self, *args, **kwargs):
        return True

    @swagger_auto_schema(request_body=MailConfigUpdateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class MailServerTestConnectAPI(BaseRetrieveMixin):
    queryset = MailConfig.objects
    serializer_detail = MailConfigDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @classmethod
    def call_test_connect(
            cls, host, port, username, password, use_tls=False, use_ssl=False, ssl_keyfile=None, ssl_cert_file=None
    ):
        if host and port and username and password:
            mail_cls = SendMailController(
                is_active=True,
                host=host, port=port,
                username=username, password=password,
                use_tls=use_tls, use_ssl=use_ssl,
                ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_cert_file,
            )
            try:
                if mail_cls.connection.open():
                    return ResponseController.success_200(
                        data={
                            'detail': 'successfully',
                        }
                    )
                return ResponseController.bad_request_400(
                    msg={
                        'connect_errors': MailMsg.CONNECT_FAILURE,
                        'connect_state': 503,
                    }
                )
            except Exception as err:
                print('[MailServerTestConnectAPI][GET]', str(err))
                return ResponseController.bad_request_400(
                    msg={
                        'connect_errors': str(err),
                        'connect_state': 503,
                    }
                )
        return ResponseController.bad_request_400(
            msg={
                'connect_errors': MailMsg.CONNECT_DATA_NOT_ENOUGH,
                'connect_state': 400,
            }
        )

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            # from django.core.mail import get_connection
            # from django.core.mail.backends.smtp import EmailBackend
            instance = self.get_object()

            if instance.use_our_server is True:
                return ResponseController.success_200(
                    data={
                        'detail': MailMsg.USE_OUR_SERVER,
                    }
                )

            real_data = instance.get_real_data()
            host = real_data['host']
            port = real_data['port']
            username = real_data['username']
            password = real_data['password']
            return self.call_test_connect(
                host=host, port=port, username=username, password=password, use_tls=instance.use_tls,
                use_ssl=instance.use_ssl,
                ssl_keyfile=instance.ssl_key.path if instance.use_ssl and instance.ssl_key else None,
                ssl_cert_file=instance.ssl_cert.path if instance.use_ssl and instance.ssl_cert else None,
            )
        return ResponseController.notfound_404()


class MailServerTestConnectDataAPI(MailServerTestConnectAPI):
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(request_body=MailTestConnectDataSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def post(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            instance = self.get_object()
            ser = MailTestConnectDataSerializer(instance=instance, data=request.data)
            ser.is_valid(raise_exception=True)
            validated_data = ser.validated_data
            return self.call_test_connect(
                host=validated_data['host'],
                port=validated_data['port'],
                username=validated_data['username'],
                password=validated_data['password'],
                use_tls=validated_data['use_tls'],
            )
        return ResponseController.notfound_404()
