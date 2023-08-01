from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared import (
    BaseListMixin, mask_view, BaseUpdateMixin,
    ResponseController,
    Caching, BaseCreateMixin, BaseRetrieveMixin, BaseDestroyMixin,
)

from apps.core.log.models import (
    ActivityLog,
    Notifications,
    BookMark, DocPined,
)
from apps.core.log.serializers import (
    ActivityListSerializer,
    NotifyListSerializer, NotifyUpdateDoneSerializer,
    BookMarkListSerializer, BookMarkCreateSerializer, BookMarkUpdateSerializer,
    DocPinedListSerializer, DocPinedCreateSerializer,
)

__all__ = [
    'ActivityLogList',
    'MyNotifyNoDoneCount',
    'MyNotifyList',
    'MyNotifyDetail',
    'MyNotifySeenAll',
    'MyNotifyCleanAll',
    'BookMarkList',
    'BookMarkDetail',
    'DocPinedList',
    'DocPinedDetail',
]


class ActivityLogList(BaseListMixin):
    queryset = ActivityLog.objects
    list_hidden_field = ['tenant_id', 'company_id']
    serializer_list = ActivityListSerializer
    filterset_fields = {
        'doc_id': ['exact'],
        'doc_app': ['exact'],
        'user_id': ['exact'],
        'employee_id': ['exact'],
    }

    @swagger_auto_schema(operation_summary='Activity Log')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyNotifyNoDoneCount(APIView):
    queryset = Notifications.objects

    @swagger_auto_schema(operation_summary='My Notify No Done Count')
    @mask_view(
        login_require=True,
        employee_require=False,
        auth_require=False
    )
    def get(self, request, *args, **kwargs):
        count = 0
        if request.user.employee_current_id:
            cache_key = Caching.key_cache_table(
                table_name=Notifications.__name__,
                string_key=Notifications.cache_base_key(user_obj=request.user),
                hash_key=True,
            )
            cache_data = Caching().get(key=cache_key)
            if cache_data:
                count = cache_data
            else:
                user_obj = request.user
                count = self.queryset.filter(
                    tenant_id=user_obj.tenant_current_id,
                    company_id=user_obj.company_current_id,
                    employee_id=user_obj.employee_current_id,
                    is_done=False,
                ).count()
                Caching().set(
                    key=cache_key,
                    value=count,
                    timeout=60 * 60,
                )
        return ResponseController.success_200(data={'count': count}, key_data='result')


class MyNotifySeenAll(APIView):
    queryset = Notifications.objects

    @swagger_auto_schema(operation_summary='My Notify Seen All')
    @mask_view(login_require=True, employee_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        if request.user.employee_current_id:
            Notifications.call_seen_all(
                tenant_id=request.user.tenant_current_id,
                company_id=request.user.company_current_id,
                employee_id=request.user.employee_current_id,
            )
        return ResponseController.success_200(data={'detail': 'Done'}, key_data='result')


class MyNotifyCleanAll(APIView):
    queryset = Notifications.objects

    @swagger_auto_schema(operation_summary='My Notify Clean All')
    @mask_view(login_require=True, employee_require=True, auth_require=False)
    def delete(self, request, *args, **kwargs):
        if request.user.employee_current_id:
            Notifications.call_clean_all_seen(
                tenant_id=request.user.tenant_current_id,
                company_id=request.user.company_current_id,
                employee_id=request.user.employee_current_id,
            )
        return ResponseController.no_content_204()


class MyNotifyList(BaseListMixin):
    queryset = Notifications.objects
    list_hidden_field = ['tenant_id', 'company_id']
    serializer_list = NotifyListSerializer
    filterset_fields = {
        'doc_id': ['exact'],
        'doc_app': ['exact'],
        'is_done': ['exact'],
    }

    @swagger_auto_schema(operation_summary='My Notify List')
    @mask_view(login_require=True, employee_require=False, auth_require=False, )
    def get(self, request, *args, **kwargs):
        if request.user.employee_current_id:
            kwargs['employee_id'] = request.user.employee_current_id
            return self.list(request, *args, **kwargs)
        return self.list_empty()


class MyNotifyDetail(BaseUpdateMixin):
    queryset = Notifications.objects
    query_extend_base_model = False
    serializer_update = NotifyUpdateDoneSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_id', ]

    @swagger_auto_schema(operation_summary='Update done my notify', request_body=NotifyUpdateDoneSerializer)
    @mask_view(login_require=True, employee_require=True, auth_require=False, )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


# BookMark
class BookMarkList(BaseListMixin, BaseCreateMixin):
    query_extend_base_model = False
    queryset = BookMark.objects
    list_hidden_field = ['employee_id']
    create_hidden_field = ['employee_id']
    serializer_list = BookMarkListSerializer
    serializer_detail = BookMarkListSerializer
    serializer_create = BookMarkCreateSerializer

    def error_employee_require(self):
        return self.list_empty()

    @swagger_auto_schema(operation_summary='BookMark List')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='BookMark Create')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BookMarkDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    query_extend_base_model = False
    queryset = BookMark.objects
    retrieve_hidden_field = ['employee_id']
    serializer_detail = BookMarkListSerializer
    serializer_update = BookMarkUpdateSerializer

    @swagger_auto_schema(operation_summary='BookMark Update')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='BookMark Destroy')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


# -- BookMark

# Pined
class DocPinedList(BaseListMixin, BaseCreateMixin):
    query_extend_base_model = False
    queryset = DocPined.objects
    serializer_list = DocPinedListSerializer
    serializer_detail = DocPinedListSerializer
    serializer_create = DocPinedCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id', 'employee_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_id']

    def get_queryset(self):
        return super().get_queryset().select_related('runtime', 'runtime__stage_currents').prefetch_related(
            'runtime__stage_currents__assignee_of_runtime_stage'
        )

    @swagger_auto_schema(operation_summary='Doc Pined List')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Doc Pined Create', request_body=DocPinedCreateSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DocPinedDetail(BaseDestroyMixin):
    query_extend_base_model = False
    queryset = DocPined.objects
    serializer_detail = DocPinedListSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id', 'employee_id']

    @swagger_auto_schema(operation_summary='Doc Pined Destroy')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)

# -- Pined
