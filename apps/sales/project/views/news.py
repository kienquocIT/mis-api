from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions

from apps.sales.project.filters import ProjectNewsCommentListFilter
from apps.sales.project.serializers import (
    ProjectNewsListSerializer, ProjectNewsCommentListSerializer,
    ProjectNewsCommentCreateSerializer, ProjectNewsCommentUpdateSerializer, ProjectNewsCommentDetailSerializer,
    ProjectNewsCommentDetailFlowSerializer,
)
from apps.shared import (
    BaseListMixin, BaseCreateMixin,
    BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
    mask_view, TypeCheck, ResponseController,
)

from apps.sales.project.models import ProjectNews, ProjectNewsComment


class ProjectNewsList(BaseListMixin):
    queryset = ProjectNews.objects.select_related('employee_inherit', 'application')
    serializer_list = ProjectNewsListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'project_id': ['exact', 'in'],
        'application': ['exact', 'in'],
        'document_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
    }

    @swagger_auto_schema(operation_summary='Project News List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProjectNewsCommentList(BaseListMixin, BaseCreateMixin):
    queryset = ProjectNewsComment.objects
    serializer_list = ProjectNewsCommentListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    serializer_create = ProjectNewsCommentCreateSerializer
    serializer_detail = ProjectNewsCommentDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_inherit_id']
    # filterset_fields = {
    #     'news_id': ['exact', 'in'],
    #     'employee_inherit_id': ['exact', 'in'],
    #     'reply_from_id': ['exact', 'in', 'isnull'],
    #     'mentions': ['contains'],
    # }
    filterset_class = ProjectNewsCommentListFilter
    search_fields = ['msg']

    @swagger_auto_schema(operation_summary='Project News Comments')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, news_id, **kwargs):
        if news_id and TypeCheck.check_uuid(news_id):
            return self.list(request, *args, news_id, **kwargs)
        return ResponseController.success_200(data=[])

    @swagger_auto_schema(
        operation_summary='Project News Comments Create', request_body=ProjectNewsCommentCreateSerializer
    )
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, news_id, **kwargs):
        if news_id and TypeCheck.check_uuid(news_id):
            return self.create(request, *args, news_id, **kwargs)
        raise exceptions.NotFound


class ProjectNewsCommentDetail(BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectNewsComment.objects.select_related('employee_inherit')
    serializer_update = ProjectNewsCommentUpdateSerializer
    update_hidden_field = ['employee_modified_id']
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_inherit_id']

    def get_object(self):
        obj = super().get_object()
        if obj and self.request.user.employee_current_id in (obj.employee_inherit_id, obj.news.employee_inherit):
            return obj
        raise exceptions.NotFound

    @swagger_auto_schema(
        operation_summary='Project News Comment Update', request_body=ProjectNewsCommentUpdateSerializer
    )
    @mask_view(login_require=True, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        raise exceptions.NotFound

    @swagger_auto_schema(operation_summary='Project News Comment Delete')
    @mask_view(login_require=True, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.destroy(request, *args, pk, **kwargs)
        raise exceptions.NotFound


class ProjectNewsCommentDetailFlows(BaseRetrieveMixin):
    queryset = ProjectNewsComment.objects.select_related('employee_inherit')
    serializer_detail = ProjectNewsCommentDetailFlowSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_inherit_id']

    def get_object(self):
        obj = super().get_object()
        if obj and self.request.user.employee_current_id in (obj.employee_inherit_id, obj.news.employee_inherit):
            return obj
        raise exceptions.NotFound

    @swagger_auto_schema(operation_summary='Get comment flows include by id')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
