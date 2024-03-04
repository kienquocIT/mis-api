from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView

from apps.core.printer.serializers import (
    PrintTemplateListSerializer, PrintTemplateCreateSerializer,
    PrintTemplateUpdateSerializer, PrintTemplateDetailSerializer,
)
from apps.shared import (
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin, mask_view,
    ResponseController, TypeCheck,
)

from apps.core.printer.models import PrintTemplates
from apps.shared import DisperseModel


class PrintTemplateApplicationList(BaseListMixin):
    queryset = PrintTemplates.objects
    serializer_list = PrintTemplateListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        result = []
        app_ids = list(
            PrintTemplates.objects.filter_current(fill__tenant=True, fill__company=True).values_list(
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


class PrintTemplateList(BaseListMixin, BaseCreateMixin):
    queryset = PrintTemplates.objects

    serializer_list = PrintTemplateListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    serializer_create = PrintTemplateCreateSerializer
    serializer_detail = PrintTemplateDetailSerializer
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    filterset_fields = {
        'application_id': ['exact', 'in'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related('application')

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=PrintTemplateCreateSerializer)
    @mask_view(login_require=True, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PrintTemplateDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = PrintTemplates.objects

    serializer_detail = PrintTemplateDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    serializer_update = PrintTemplateUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=PrintTemplateUpdateSerializer)
    @mask_view(login_require=True, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class PrintTemplateUsingDetail(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        if 'application_id' in self.kwargs and TypeCheck.check_uuid(self.kwargs['application_id']):
            template_objs = PrintTemplates.objects.filter_current(
                fill__tenant=True, fill__company=True,
                is_active=True,
                application=self.kwargs['application_id'],
            )
            if template_objs:
                default_data = {}
                result = []
                for obj in template_objs:
                    temp_data = {
                        'id': str(obj.id),
                        'title': str(obj.title),
                        'remarks': str(obj.remarks),
                    }
                    if obj.is_default is True:
                        default_data = {
                            **temp_data,
                            'contents': obj.contents,
                        }
                    result.append(temp_data)
                return ResponseController.success_200(
                    data={
                        'default': default_data,
                        'template_list': result,
                    },
                    key_data='result'
                )
        return ResponseController.notfound_404()


class PrintTemplateDetailUsing(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            obj = PrintTemplates.objects.filter_current(
                fill__tenant=True, fill__company=True,
                is_active=True, id=pk
            ).first()
            if obj:
                ctx = {
                    'id': str(obj.id),
                    'title': str(obj.title),
                    'remarks': str(obj.remarks),
                    'contents': obj.contents,
                }
                return ResponseController.success_200(data=ctx)
        return ResponseController.notfound_404()
