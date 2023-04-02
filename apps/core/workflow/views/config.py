from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.workflow.models import Workflow, Node  # pylint: disable-msg=E0611
from apps.core.workflow.serializers.config import WorkflowListSerializer, WorkflowCreateSerializer, \
    WorkflowDetailSerializer, WorkflowUpdateSerializer
from apps.core.workflow.serializers.config_sub import NodeListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class WorkflowList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Workflow.objects
    filterset_fields = ['application']
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
        self.serializer_class = WorkflowDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update workflow",
        operation_description="Update workflow by ID",
        request_body=WorkflowUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = WorkflowUpdateSerializer
        return self.update(request, *args, **kwargs)


class NodeSystemList(
    BaseListMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Node.objects
    serializer_list = NodeListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(
            is_system=True,
            tenant_id=None,
            company_id=None
        ).order_by('order')

    @swagger_auto_schema(
        operation_summary="Node System List",
        operation_description="Get Node System List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
