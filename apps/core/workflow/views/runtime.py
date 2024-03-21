from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.core.workflow.models import Runtime, RuntimeStage, RuntimeAssignee
from apps.core.workflow.serializers.runtime import (
    RuntimeListSerializer,
    RuntimeStageListSerializer, RuntimeDetailSerializer, RuntimeAssigneeUpdateSerializer, RuntimeAssigneeListSerializer,
    RuntimeMeListSerializer, RuntimeAfterFinishUpdateSerializer,
)
from apps.shared import ResponseController, mask_view, BaseListMixin, TypeCheck, HttpMsg

__all__ = [
    'RuntimeDiagramDetail',
    'RuntimeListView',
    'RuntimeMeListView',
    'RuntimeDetail',
    'RuntimeAssigneeList',
    'RuntimeAssigneeDetail',
    'RuntimeAfterFinishDetail',
]


class RuntimeListView(BaseListMixin):
    queryset = Runtime.objects
    serializer_list = RuntimeListSerializer
    filterset_fields = {
        'flow_id': ['exact', 'in'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related('stage_currents', 'doc_employee_created')

    @swagger_auto_schema()
    @mask_view(
        login_require=True, auth_require=True,
        label_code='workflow', model_code='workflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        params = request.query_params
        if 'flow_id' in params and TypeCheck.check_uuid(params['flow_id']):
            kwargs['flow_id'] = params['flow_id']
            return self.list(request, *args, **kwargs)
        return ResponseController.notfound_404()


class RuntimeMeListView(BaseListMixin):
    queryset = Runtime.objects
    serializer_list = RuntimeMeListSerializer
    filterset_fields = {
        'app_id': ['exact', 'in'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related('stage_currents').prefetch_related(
            'stage_currents__assignee_of_runtime_stage'
        )

    @property
    def filter_kwargs_q(self) -> Q():
        return Q(doc_employee_created_id=self.request.user.employee_current_id)

    @swagger_auto_schema(operation_summary='Runtime of me')
    @mask_view(login_require=True, auth_require=False, employee_require=True, use_custom_get_filter_auth=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RuntimeDiagramDetail(APIView):
    @swagger_auto_schema(operation_description='Runtime Detail Diagram')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, runtime_id, **kwargs):
        if TypeCheck.check_uuid(runtime_id):
            # import time
            # time.sleep(1)
            try:
                runtime_obj = Runtime.objects.select_related('app', 'stage_currents').get(
                    id=runtime_id
                )
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()

            stage_objs = RuntimeStage.objects.select_related('from_stage', 'to_stage').prefetch_related(
                'assignee_of_runtime_stage', 'log_of_stage_runtime',
            ).filter(runtime=runtime_obj)
            result = {
                'id': runtime_obj.id,
                'doc_title': runtime_obj.doc_title,
                'stages': RuntimeStageListSerializer(instance=stage_objs, many=True).data,
            }
            return ResponseController.success_200(data=result, key_data='result')
        return ResponseController.notfound_404()


class RuntimeDetail(APIView):
    @swagger_auto_schema(operation_description='Runtime Detail')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        if TypeCheck.check_uuid(pk):
            try:
                runtime_obj = Runtime.objects.select_related('stage_currents').get(
                    id=pk
                )
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()

            return ResponseController.success_200(
                data=RuntimeDetailSerializer(
                    instance=runtime_obj, context={'employee_current_id': request.user.employee_current_id}
                ).data, key_data='result'
            )
        return ResponseController.notfound_404()


class RuntimeAssigneeList(BaseListMixin):
    queryset = RuntimeAssignee.objects
    serializer_list = RuntimeAssigneeListSerializer
    list_hidden_field = ['company_id']
    filterset_fields = {
        'is_done': ['exact', 'in'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related('stage', 'stage__runtime', 'employee')

    @property
    def filter_kwargs_q(self) -> Q():
        return Q(employee_id=self.request.user.employee_current_id)

    def error_employee_require(self):
        return self.list_empty()

    @swagger_auto_schema(operation_summary='Runtime Task List')
    @mask_view(login_require=True, auth_require=False, employee_require=True, use_custom_get_filter_auth=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RuntimeAssigneeDetail(APIView):
    @swagger_auto_schema(operation_summary='Runtime Detail')
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        if TypeCheck.check_uuid(pk):
            try:
                runtime_assignee_obj = RuntimeAssignee.objects.select_related('stage').get(
                    id=pk
                )
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()

            ser = RuntimeAssigneeUpdateSerializer(instance=runtime_assignee_obj, data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
        return ResponseController.notfound_404()


class RuntimeAfterFinishDetail(APIView):
    @swagger_auto_schema(operation_summary='Runtime After Finish')
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        if TypeCheck.check_uuid(pk):
            try:
                runtime_obj = Runtime.objects.get(id=pk)
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()

            ser = RuntimeAfterFinishUpdateSerializer(instance=runtime_obj, data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
        return ResponseController.notfound_404()
