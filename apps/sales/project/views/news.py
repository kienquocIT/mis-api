from typing import Union

from drf_yasg.utils import swagger_auto_schema
import rest_framework.exceptions

from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response

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

from apps.sales.project.models import ProjectNews, ProjectNewsComment, ProjectMapMember


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

    @classmethod
    def get_prj_allowed(cls, item_data):
        if item_data and isinstance(item_data, dict) and 'prj' in item_data and isinstance(item_data['prj'], dict):
            ids = list(item_data['prj'].keys())
            if TypeCheck.check_uuid_list(data=ids):
                return item_data['prj'].keys()
        return []

    def get_prj_has_view_this(self):
        return [
            str(item) for item in ProjectMapMember.objects.filter_current(
                fill__tenant=True, fill__company=True,
                member_id=self.cls_check.employee_attr.employee_current_id,
                permit_view_this_project=True,
            ).values_list('project_id', flat=True)
        ]

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        # check permit config exists if from_app not calling...
        prj_has_view_ids = self.get_prj_has_view_this()
        if self.cls_check.permit_cls.config_data__exist or prj_has_view_ids:
            return self.filter_kwargs_q__from_config() | Q(project_id__in=prj_has_view_ids)
        return self.list_empty()

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:
        # permit_data = {"employee": [], "roles": []}
        prj_ids = []
        if arr_from_app and isinstance(arr_from_app, list) and len(arr_from_app) == 3:
            permit_data = self.cls_check.permit_cls.config_data__by_code(
                label_code=arr_from_app[0],
                model_code=arr_from_app[1],
                perm_code=arr_from_app[2],
                has_roles=False,
            )
            if 'employee' in permit_data:
                prj_ids += self.get_prj_allowed(item_data=permit_data['employee'])
            if 'roles' in permit_data and isinstance(permit_data['roles'], list):
                for item_data in permit_data['roles']:
                    prj_ids += self.get_prj_allowed(item_data=item_data)
            if settings.DEBUG_PERMIT:
                print('=> prj_ids:                :', '[HAS FROM APP]', prj_ids)
        return Q(project_id__in=list(set(prj_ids)))

    @swagger_auto_schema(operation_summary='Project news list')
    @mask_view(
        login_require=True, employee_require=True,
        label_code='project', model_code='project', perm_code='view')
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
        raise rest_framework.exceptions.NotFound


class ProjectNewsCommentDetail(BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectNewsComment.objects.select_related('employee_inherit')
    serializer_update = ProjectNewsCommentUpdateSerializer
    update_hidden_field = ['employee_modified_id']
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_inherit_id']

    def get_object(self):
        obj = super().get_object()
        if obj and self.request.user.employee_current_id in (obj.employee_inherit_id, obj.news.employee_inherit):
            return obj
        raise rest_framework.exceptions.NotFound

    @swagger_auto_schema(
        operation_summary='Project News Comment Update', request_body=ProjectNewsCommentUpdateSerializer
    )
    @mask_view(login_require=True, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        raise rest_framework.exceptions.NotFound

    @swagger_auto_schema(operation_summary='Project News Comment Delete')
    @mask_view(login_require=True, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.destroy(request, *args, pk, **kwargs)
        raise rest_framework.exceptions.NotFound


class ProjectNewsCommentDetailFlows(BaseRetrieveMixin):
    queryset = ProjectNewsComment.objects.select_related('employee_inherit')
    serializer_detail = ProjectNewsCommentDetailFlowSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_inherit_id']

    def get_object(self):
        obj = super().get_object()
        if obj and self.request.user.employee_current_id in (obj.employee_inherit_id, obj.news.employee_inherit):
            return obj
        raise rest_framework.exceptions.NotFound

    @swagger_auto_schema(operation_summary='Get comment flows include by id')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
