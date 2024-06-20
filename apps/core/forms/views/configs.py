from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.core.forms.models import (
    Form, FormPublished, SANITIZE_HTML_CONFIG_TAGS, SANITIZE_HTML_CONFIG_ATTRS,
    SANITIZE_HTML_CONFIG_ATTRS_PREFIX,
)
from apps.core.forms.serializers.serializers import (
    FormListSerializer, FormCreateSerializer, FormDetailSerializer,
    FormUpdateSerializer, FormPublishedDetailSerializer, FormPublishedUpdateSerializer,
    FormPublishedRuntimeDetailSerializer, FormUpdateTurnOffSerializer, FormUpdateThemeSerializer,
    FormUpdateDuplicateSerializer,
)
from apps.core.mailer.handle_html import HTMLController
from apps.shared import (
    BaseListMixin, BaseCreateMixin, BaseUpdateMixin, BaseRetrieveMixin, BaseDestroyMixin, mask_view,
    ResponseController,
)


class FormList(BaseListMixin, BaseCreateMixin):
    queryset = Form.objects.prefetch_related('form_published')
    serializer_list = FormListSerializer
    serializer_create = FormCreateSerializer
    serializer_detail = FormDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=FormCreateSerializer)
    @mask_view(login_require=True, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FormDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = Form.objects
    serializer_detail = FormDetailSerializer
    serializer_update = FormUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class FormDetailTheme(BaseUpdateMixin):
    queryset = Form.objects
    serializer_update = FormUpdateThemeSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class FormDetailTurnOnOff(BaseUpdateMixin):
    queryset = Form.objects
    serializer_update = FormUpdateTurnOffSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class FormDetailDuplicate(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Form.objects
    serializer_update = FormUpdateDuplicateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def post(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class FormPublishedDetailForm(BaseRetrieveMixin):
    queryset = FormPublished.objects
    serializer_detail = FormPublishedDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_form_obj(self):
        pk_form = self.kwargs.get('pk_form', None)
        if pk_form:
            del self.kwargs['pk_form']
            try:
                return Form.objects.get_current(fill__company=True, pk=pk_form)
            except Form.DoesNotExist:
                ...
        return None

    def get_object(self):
        return FormPublished.objects.get_current(fill__company=True, form=self.kwargs['form'])

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk_form, **kwargs):
        form_obj = self.get_form_obj()
        if form_obj:
            self.kwargs['form'] = form_obj
            return self.retrieve(request, *args, pk_form, **kwargs)
        return ResponseController.notfound_404()


class FormPublishedDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = FormPublished.objects
    serializer_update = FormPublishedUpdateSerializer
    serializer_detail = FormPublishedRuntimeDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=FormPublishedUpdateSerializer)
    @mask_view(login_require=True, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class FormSanitizeHTML(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        sanitize_html = ''
        data = request.data
        if isinstance(data, dict) and 'html' in data:
            sanitize_html = HTMLController(html_str=data['html']).clean(
                append_tags=SANITIZE_HTML_CONFIG_TAGS,
                append_attrs=SANITIZE_HTML_CONFIG_ATTRS,
                is_minify=True,
                generic_attribute_prefixes=SANITIZE_HTML_CONFIG_ATTRS_PREFIX,
            )
        return ResponseController.success_200(
            data={
                'sanitize_html': HTMLController.unescape(sanitize_html),
            }
        )
