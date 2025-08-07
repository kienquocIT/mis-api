from drf_yasg.utils import swagger_auto_schema

from apps.hrm.absenceexplanation.models import AbsenceExplanation
from apps.hrm.absenceexplanation.serializers import AbsenceExplanationListSerializer, \
    AbsenceExplanationDetailSerializer, AbsenceExplanationCreateSerializer, AbsenceExplanationUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class AbsenceExplanationList(BaseListMixin, BaseCreateMixin):
    queryset = AbsenceExplanation.objects
    serializer_list = AbsenceExplanationListSerializer
    serializer_detail = AbsenceExplanationDetailSerializer
    serializer_create = AbsenceExplanationCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="HRM Absence Explanation request list",
        operation_description="get absence explanation request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create absence explanation",
        operation_description="Create new absence explanation",
        request_body=AbsenceExplanationCreateSerializer
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        return self.create(request, *args, **kwargs)


class AbsenceExplanationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AbsenceExplanation.objects
    serializer_detail = AbsenceExplanationDetailSerializer
    serializer_update = AbsenceExplanationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary="Absence explanation detail",
        operation_description="Get absence explanation detail",
        perm_code='view',
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mask_view(
        login_require=True,
        auth_require=False,
        perm_code='edit'
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
