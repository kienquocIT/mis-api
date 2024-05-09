from drf_yasg.utils import swagger_auto_schema

from apps.core.diagram.models import DiagramDocument
from apps.core.diagram.serializers import DiagramListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


# Create your views here.
class DiagramList(BaseListMixin, BaseCreateMixin):
    queryset = DiagramDocument.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'app_code': ['exact'],
        'doc_id': ['exact'],
    }
    serializer_list = DiagramListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Diagram List",
        operation_description="Get Diagram List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
