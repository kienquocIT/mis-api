__all__ = ['ProjectWorkExpenseList']

from drf_yasg.utils import swagger_auto_schema

from apps.sales.project.models import WorkMapExpense, ProjectMapMember
from apps.sales.project.serializers import WorkExpenseListSerializers
from apps.shared import BaseListMixin, mask_view, ResponseController


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

    def valid_permit_add_gaw(self):
        return ProjectMapMember.objects.filter_current(
            fill__tenant=True, fill__company=True,
            member_id=self.cls_check.employee_attr.employee_current_id,
            permit_add_gaw=True,
        ).exists()

    @swagger_auto_schema(
        operation_summary="Work expense list",
        operation_description="get work expense list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='view',
        skip_filter_employee=True
    )
    def get(self, request, *args, **kwargs):
        if self.valid_permit_add_gaw():
            return self.list(request, *args, **kwargs)
        return ResponseController.forbidden_403()
