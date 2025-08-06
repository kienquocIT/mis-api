from drf_yasg.utils import swagger_auto_schema

from apps.hrm.absenceexplanation.models import AbsenceExplanation
from apps.hrm.absenceexplanation.serializers import AbsenceExplanationListSerializer, \
    AbsenceExplanationDetailSerializer, AbsenceExplanationCreateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


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

