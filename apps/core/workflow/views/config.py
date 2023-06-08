from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.workflow.models import (
    WorkflowConfigOfApp, Workflow,
    Runtime,
)
from apps.core.workflow.serializers.config import (
    WorkflowListSerializer, WorkflowCreateSerializer,
    WorkflowDetailSerializer, WorkflowUpdateSerializer, WorkflowOfAppListSerializer, WorkflowOfAppUpdateSerializer,
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin,
    ResponseController, HttpMsg, WorkflowMsg,
)

__all__ = [
    'WorkflowOfAppList', 'WorkflowOfAppDetail',
    'WorkflowList',
    'WorkflowDetail',
]


class WorkflowOfAppList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = WorkflowConfigOfApp.objects
    serializer_class = WorkflowOfAppListSerializer
    serializer_list = WorkflowOfAppListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Workflow of Feature List",
        operation_description="Get Workflow of feature List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WorkflowOfAppDetail(BaseUpdateMixin):
    queryset = WorkflowConfigOfApp.objects
    serializer_update = WorkflowOfAppUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(request_body=WorkflowOfAppUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class WorkflowList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Workflow.objects
    filterset_fields = ['application', 'is_active']
    serializer_list = WorkflowListSerializer
    serializer_create = WorkflowCreateSerializer
    serializer_detail = WorkflowListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "application"
        )

    @swagger_auto_schema(
        operation_summary="Workflow List",
        operation_description="Get Workflow List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Workflow",
        operation_description="Create new Workflow",
        request_body=WorkflowCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkflowDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Workflow.objects
    serializer_detail = WorkflowDetailSerializer
    serializer_update = WorkflowUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "application"
        )

    @swagger_auto_schema(
        operation_summary="Workflow detail",
        operation_description="Get workflow detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update workflow",
        operation_description="Update workflow by ID",
        request_body=WorkflowUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # check in-progress workflows. If exists, don't allow change.
        count = Runtime.check_document_in_progress(workflow_id=instance.id, state_or_count='count')
        if count > 0:
            raise serializers.ValidationError({'detail': WorkflowMsg.WORKFLOW_NOT_ALLOW_CHANGE.format(str(count))})

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}  # pylint: disable=W0212

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
