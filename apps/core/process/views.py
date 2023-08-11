from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.process.models import SaleFunction, Process, SaleProcessStep
from apps.core.process.serializers import FunctionProcessListSerializer, ProcessUpdateSerializer, \
    ProcessDetailSerializer, ProcessStepDetailSerializer, SkipProcessStepSerializer, SetProcessStepCurrentSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class FunctionProcessList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = SaleFunction.objects

    serializer_list = FunctionProcessListSerializer
    list_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Function Process List",
        operation_description="Get Function Process List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProcessDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Process.objects  # noqa
    serializer_detail = ProcessDetailSerializer
    serializer_update = ProcessUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Process Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Process Update",
        request_body=ProcessUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class SkipProcessStep(BaseUpdateMixin):
    queryset = SaleProcessStep.objects  # noqa
    serializer_detail = ProcessStepDetailSerializer
    serializer_update = SkipProcessStepSerializer

    @swagger_auto_schema(
        operation_summary="Skip Process Step",
        request_body=SkipProcessStepSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SetCurrentProcessStep(BaseUpdateMixin):
    queryset = SaleProcessStep.objects  # noqa
    serializer_detail = ProcessStepDetailSerializer
    serializer_update = SetProcessStepCurrentSerializer

    @swagger_auto_schema(
        operation_summary="Set Current Process Step",
        request_body=SetProcessStepCurrentSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
