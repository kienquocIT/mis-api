from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.workflow.models import Workflow, Node
from apps.core.workflow.serializers.config import WorkflowListSerializer, WorkflowCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class WorkflowList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Workflow.object_global.select_related("company")
    serializer_list = WorkflowListSerializer
    serializer_create = WorkflowCreateSerializer
    serializer_detail = WorkflowListSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

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


class NodeSystemList(
    BaseListMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Node.objects
    serializer_list = WorkflowListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super(NodeSystemList, self).get_queryset().filter(is_system=True)

    @swagger_auto_schema(
        operation_summary="Node System List",
        operation_description="Get Node System List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
