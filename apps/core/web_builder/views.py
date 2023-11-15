import re

from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.core.company.models import Company
from apps.core.web_builder.authen import authenticated_for_ui
from apps.core.web_builder.serializers import (
    PageBuilderListSerializer, PageBuilderDetailSerializer,
    PageBuilderUpdateSerializer, PageBuilderCreateSerializer, PageBuilderDetailViewerSerializer,
)
from apps.shared import (
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin, mask_view,
    TypeCheck, ResponseController,
)
from apps.core.web_builder.models import PageBuilder


class PageBuilderList(BaseListMixin, BaseCreateMixin):
    queryset = PageBuilder.objects
    serializer_list = PageBuilderListSerializer
    serializer_detail = PageBuilderDetailSerializer
    serializer_create = PageBuilderCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=PageBuilderCreateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current_id': self.request.user.company_current_id
        }
        return self.create(request, *args, **kwargs)


class PageBuilderDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = PageBuilder.objects
    serializer_detail = PageBuilderDetailSerializer
    serializer_update = PageBuilderUpdateSerializer

    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    def resolve_partial(self, partial_parsed: bool):
        if self.request.method == 'PUT':
            return True
        return partial_parsed

    @swagger_auto_schema(request_body=PageBuilderUpdateSerializer)
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'company_current_id': self.request.user.company_current_id
        }
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class PageBuilderViewPathSub(APIView):
    @swagger_auto_schema()
    @mask_view(auth_require=False, login_require=False)
    def get(self, request, *args, pk_company, path_sub, **kwargs):
        if pk_company and TypeCheck.check_uuid(pk_company):
            if path_sub == '-':
                path_sub = '/'

            if not path_sub.startswith('/'):
                path_sub = '/' + path_sub

            for obj in PageBuilder.objects.filter(company_id=pk_company, is_publish=True).cache():
                regex_str = obj.page_path
                if '{id}' in obj.page_path:
                    regex_str = str(obj.page_path).replace(
                        '{id}', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                    )
                regex_str = f'^{regex_str}$'
                pattern = re.compile(regex_str)
                if pattern.match(path_sub):
                    ser = PageBuilderDetailViewerSerializer(obj)
                    return ResponseController.success_200(data=ser.data)
        return ResponseController.notfound_404()


class CompanyGetter(APIView):
    @swagger_auto_schema()
    @mask_view(auth_require=False, login_require=False)
    def get(self, request, *args, company_sub_domain, **kwargs):
        if authenticated_for_ui(request):
            try:
                obj = Company.objects.get(sub_domain=company_sub_domain)
            except Company.DoesNotExist:
                return ResponseController.notfound_404()

            return ResponseController.success_200(data={
                'id':  obj.id,
                'title': obj.title,
                'code': obj.code,
                'sub_domain': obj.sub_domain,
                'tenant': {
                    'id': obj.tenant.id,
                    'title': obj.tenant.title,
                    'code': obj.tenant.code,
                }
            }, key_data='result')

        return ResponseController.notfound_404()
