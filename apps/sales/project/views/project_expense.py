__all__ = ['ProjectWorkExpenseList']

from drf_yasg.utils import swagger_auto_schema

from apps.sales.project.models import WorkMapExpense
from apps.sales.project.serializers import WorkExpenseListSerializers
from apps.shared import BaseListMixin, mask_view


class ProjectWorkExpenseList(BaseListMixin):
    queryset = WorkMapExpense.objects
    serializer_list = WorkExpenseListSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = ['title', 'code']
    filterset_fields = {
        'work_id': ['exact']
    }

    def get_queryset(self):
        return super().get_queryset().select_related('expense_name', 'expense_item', 'uom', 'tax')

    @swagger_auto_schema(
        operation_summary="Work expense list",
        operation_description="get work expense list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
