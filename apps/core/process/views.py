import logging

from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, exceptions

from apps.core.process.filters import ProcessRuntimeListFilter, ProcessRuntimeDataMatchFilter
from apps.core.process.models.runtime import ProcessStageApplication, ProcessMembers
from apps.core.process.msg import ProcessMsg
from apps.core.process.utils import ProcessRuntimeControl
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
    TypeCheck, ResponseController,
)
from apps.core.process.models import ProcessConfiguration, Process
from apps.core.process.serializers import (
    ProcessConfigListSerializer, ProcessConfigDetailSerializer, ProcessConfigCreateSerializer,
    ProcessConfigUpdateSerializer, ProcessRuntimeCreateSerializer, ProcessRuntimeListSerializer,
    ProcessRuntimeDetailSerializer, ProcessStageApplicationUpdateSerializer, ProcessStageApplicationDetailSerializer,
    ProcessConfigReadySerializer, ProcessStageApplicationListSerializer, ProcessRuntimeDataMatchFromStageSerializer,
    ProcessRuntimeDataMatchFromProcessSerializer, ProcessRuntimeMembersSerializer,
    ProcessRuntimeMembersCreateSerializer,
)

logger = logging.getLogger(__name__)


class ProcessConfigReadyList(BaseListMixin):
    queryset = ProcessConfiguration.objects
    serializer_list = ProcessConfigReadySerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'for_opp': ['exact'],
    }
    search_fields = ['title', 'remark']

    def get_queryset_and_filter_queryset(self, *args, **kwargs):
        date_now = timezone.now()
        data = super().get_queryset_and_filter_queryset(*args, **kwargs)
        return data.filter(is_active=True).filter(
            Q(apply_start__isnull=False, apply_start__lt=date_now)
            |
            Q(apply_start__isnull=True)
        ).filter(
            Q(apply_finish__isnull=False, apply_finish__gt=date_now)
            |
            Q(apply_finish__isnull=True)
        )

    @swagger_auto_schema(operation_summary='Process Configurate List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
        'id': ['in'],
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


class ProcessRuntimeDataMatch(BaseRetrieveMixin):
    filterset_class = ProcessRuntimeDataMatchFilter
    serializer_detail = ProcessRuntimeDataMatchFromStageSerializer

    @swagger_auto_schema(
        operation_summary='Get Process Runtime Match With Filter',
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        result = {}
        query_params = request.query_params.dict()

        app_id = query_params.get('app_id', None)
        stage_id = query_params.get('process_stage_id', None)

        if stage_id and TypeCheck.check_uuid(stage_id):
            select_related = ['process', 'process__opp', 'application']
            obj_app = ProcessStageApplication.objects.select_related(*select_related).filter(id=stage_id).first()
            ProcessRuntimeControl.check_permit_process(
                process_obj=obj_app.process, employee_id=request.user.employee_current_id
            )
            if obj_app:
                result = ProcessRuntimeDataMatchFromStageSerializer(instance=obj_app).data
        elif app_id and TypeCheck.check_uuid(app_id):
            opp_id = query_params.get('opp_id', None)
            process_id = query_params.get('process_id', None)

            if opp_id and process_id:
                obj_process = Process.objects.select_related('opp').filter(opp_id=opp_id, id=process_id).first()
            elif opp_id:
                obj_process = Process.objects.select_related('opp').filter(opp_id=opp_id).first()
            elif process_id:
                obj_process = Process.objects.select_related('opp').filter(id=process_id).first()
            else:
                obj_process = None

            ProcessRuntimeControl.check_permit_process(
                process_obj=obj_process, employee_id=request.user.employee_current_id
            )

            if obj_process:
                result = ProcessRuntimeDataMatchFromProcessSerializer(
                    instance=obj_process, context={'app_id': app_id}
                ).data

        return ResponseController.success_200(data=result)


class ProcessRuntimeOfMeList(BaseListMixin):
    queryset = Process.objects.select_related('config', 'employee_created', 'stage_current')
    serializer_list = ProcessRuntimeListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'opp_id': ['exact'],
    }
    search_fields = ['title', 'remark']

    def get_queryset_and_filter_queryset(self, *args, **kwargs):
        if self.request.user.employee_current_id:
            data = super().get_queryset_and_filter_queryset(*args, **kwargs)
            return data.filter(was_done=False).filter(
                Q(employee_created_id=self.request.user.employee_current_id)
                |
                Q(members__contains=[str(self.request.user.employee_current_id)])
            )
        return super().get_queryset().none()

    @swagger_auto_schema(operation_summary='Process Runtime List')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProcessStagesAppsOfMeList(BaseListMixin):
    queryset = ProcessStageApplication.objects
    serializer_list = ProcessStageApplicationListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'process_id': ['exact'],
        'application_id': ['exact'],
        'was_done': ['exact'],
    }
    search_fields = ['title', 'remark']

    def get_queryset(self):
        return super().get_queryset().select_related('application', 'process', 'process__opp').order_by(
            'process__title'
        )

    def get_queryset_and_filter_queryset(self, *args, **kwargs):
        data = super().get_queryset_and_filter_queryset(*args, **kwargs)
        return data.filter(was_done=False).filter(
            Q(process__employee_created_id=self.request.user.employee_current_id)
            |
            Q(process__members__contains=[str(self.request.user.employee_current_id)])
        )

    @swagger_auto_schema(operation_summary='Process Stages Apps Of Me')
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

    def get_queryset(self):
        if self.request.user.employee_current_id:
            return super().get_queryset().filter(members__contains=str(self.request.user.employee_current_id))
        return super().get_queryset().none()

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

    def get_object(self):
        instance = super().get_object()
        ProcessRuntimeControl.check_permit_process(
            process_obj=instance, employee_id=self.request.user.employee_current_id
        )
        return instance

    @swagger_auto_schema(operation_summary='Process Runtime Detail')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.retrieve(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()


class ProcessRuntimeMembers(BaseListMixin, BaseCreateMixin):
    queryset = ProcessMembers.objects.select_related('employee', 'employee_created')
    serializer_list = ProcessRuntimeMembersSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def view_check_process(self, process_id):
        try:
            process_obj = Process.objects.get_current(fill__tenant=True, fill__company=True, pk=process_id)
            ProcessRuntimeControl.check_permit_process(
                process_obj=process_obj, employee_id=self.request.user.employee_current_id
            )
            return True
        except Process.DoesNotExist:
            pass
        raise exceptions.PermissionDenied

    @swagger_auto_schema(operation_summary='Process Runtime Members')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, process_id, **kwargs):
        if process_id and TypeCheck.check_uuid(process_id):
            self.view_check_process(process_id=process_id)
            return self.list(request, *args, process_id, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Process Runtime Add Members', request_body=ProcessRuntimeMembersCreateSerializer
    )
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, process_id, **kwargs):
        if process_id and TypeCheck.check_uuid(process_id):
            self.view_check_process(process_id=process_id)
            ser = ProcessRuntimeMembersCreateSerializer(
                data={
                    **request.data,
                    'process': process_id,
                }
            )
            ser.is_valid(raise_exception=True)
            instance = ser.save(
                tenant_id=request.user.tenant_current_id,
                company_id=request.user.company_current_id,
                employee_created_id=request.user.employee_current_id,
            )
            return ResponseController.created_201(data=ProcessRuntimeMembersSerializer(instance=instance).data)
        return ResponseController.notfound_404()


class ProcessRuntimeStagesAppControl(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProcessStageApplication.objects
    serializer_detail = ProcessStageApplicationDetailSerializer
    serializer_update = ProcessStageApplicationUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    def manual_check_obj_retrieve(self, instance, **kwargs):
        ProcessRuntimeControl.check_permit_process(
            process_obj=instance.process, employee_id=self.request.user.employee_current_id
        )
        return True

    @swagger_auto_schema(operation_summary='Process Runtime Stages : All Documents of Stages App')
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.retrieve(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        if instance and isinstance(instance, ProcessStageApplication):
            ProcessRuntimeControl.check_permit_process(
                process_obj=instance.process, employee_id=self.request.user.employee_current_id
            )

            state = ProcessRuntimeControl.check_application_can_state_done(stage_app_obj=instance)
            if state:
                return True
            raise serializers.ValidationError(
                {
                    'detail': ProcessMsg.STAGES_APP_NEED_AMOUNT.format(amount=instance.amount)
                }
            )
        return False

    @swagger_auto_schema(operation_summary='Process Runtime Stages App Detail')
    @mask_view(login_require=True, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()


class ProcessRuntimeMemberDetail(BaseDestroyMixin):
    queryset = ProcessMembers.objects
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def manual_check_obj_destroy(self, instance, **kwargs):
        ProcessRuntimeControl.check_permit_process(
            process_obj=instance.process, employee_id=self.request.user.employee_current_id
        )

        employee_current_id = str(self.request.user.employee_current_id)
        if (
                str(instance.employee_id) == employee_current_id
                and str(instance.process.employee_created_id) == employee_current_id
        ):
            raise exceptions.PermissionDenied
        return True

    @swagger_auto_schema(operation_summary='Process Runtime Stages : All Documents of Stages App')
    @mask_view(login_require=True, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)
