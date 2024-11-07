import logging

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from apps.core.process.filters import ProcessRuntimeListFilter
from apps.core.process.models.runtime import ProcessStageApplication
from apps.core.process.msg import ProcessMsg
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
    TypeCheck, ResponseController,
)
from apps.core.process.models import ProcessConfiguration, Process
from apps.core.process.serializers import (
    ProcessConfigListSerializer, ProcessConfigDetailSerializer, ProcessConfigCreateSerializer,
    ProcessConfigUpdateSerializer, ProcessRuntimeCreateSerializer, ProcessRuntimeListSerializer,
    ProcessRuntimeDetailSerializer, ProcessStageApplicationUpdateSerializer, ProcessStageApplicationDetailSerializer,
)

logger = logging.getLogger(__name__)


class ProcessConfigList(BaseListMixin, BaseCreateMixin):
    queryset = ProcessConfiguration.objects.select_related('employee_created')
    serializer_list = ProcessConfigListSerializer
    serializer_detail = ProcessConfigListSerializer
    serializer_create = ProcessConfigCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']
    filterset_fields = {
        'for_opp': ['exact'],
        'employee_created': ['exact', 'in'],
        'is_active': ['exact'],
    }

    @swagger_auto_schema(operation_summary='Process Configurate List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Process Configurate Create')
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProcessConfigDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProcessConfiguration.objects
    serializer_detail = ProcessConfigDetailSerializer
    serializer_update = ProcessConfigUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Process Configuration Detail')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Process Configuration Update')
    @mask_view(login_require=True, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Process Configuration Destroy')
    @mask_view(login_require=True, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class ProcessRuntimeOfMeList(BaseListMixin):
    queryset = Process.objects.select_related('config', 'employee_created', 'stage_current')
    serializer_list = ProcessRuntimeListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'opp_id': ['exact'],
    }
    search_fields = ['title', 'remark']

    @property
    def filter_kwargs_q(self):
        data = super().filter_kwargs_q
        return data

    def get_queryset_and_filter_queryset(self, *args, **kwargs):
        data = super().get_queryset_and_filter_queryset(*args, **kwargs)
        return data.filter(
            Q(employee_created_id=self.request.user.employee_current_id)
            |
            Q(members__contains=[str(self.request.user.employee_current_id)])
        )

    @swagger_auto_schema(operation_summary='Process Runtime List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProcessRuntimeList(BaseListMixin, BaseCreateMixin):
    queryset = Process.objects.select_related('config', 'employee_created', 'stage_current')
    serializer_list = ProcessRuntimeListSerializer
    serializer_detail = ProcessRuntimeListSerializer
    serializer_create = ProcessRuntimeCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    filterset_class = ProcessRuntimeListFilter
    search_fields = ['title', 'remark']

    @swagger_auto_schema(operation_summary='Process Runtime List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Process Runtime Create')
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProcessRuntimeDetail(BaseRetrieveMixin):
    queryset = Process.objects.select_related('config', 'opp')
    serializer_detail = ProcessRuntimeDetailSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Process Runtime Detail')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.retrieve(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()


class ProcessRuntimeStagesAppControl(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProcessStageApplication.objects
    serializer_detail = ProcessStageApplicationDetailSerializer
    serializer_update = ProcessStageApplicationUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    def manual_check_obj_retrieve(self, instance, **kwargs):
        return True

    @swagger_auto_schema(operation_summary='Process Runtime Stages : All Documents of Stages App')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.retrieve(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        if instance and isinstance(instance, ProcessStageApplication):
            amount = instance.amount
            try:
                min_num = int(instance.min)
            except Exception as err:
                logger.error('[ProcessRuntimeStagesAppDetail] Exception of get_object: %s', str(err))
                raise serializers.ValidationError(
                    {
                        'detail': ProcessMsg.STAGES_APP_NOT_ANALYSE
                    }
                )
            if amount >= min_num:
                return True
            raise serializers.ValidationError(
                {
                    'detail': ProcessMsg.STAGES_APP_NEED_AMOUNT.format(amount=amount)
                }
            )
        return False

    @swagger_auto_schema(operation_summary='Process Runtime Stages App Detail')
    @mask_view(login_require=True, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()
