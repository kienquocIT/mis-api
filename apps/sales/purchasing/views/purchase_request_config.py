from drf_yasg.utils import swagger_auto_schema  # noqa

from apps.sales.purchasing.serializers import PurchaseRequestConfigDetailSerializer, \
    PurchaseRequestConfigUpdateSerializer
from apps.sales.purchasing.models import PurchaseRequestConfig
from apps.shared import BaseRetrieveMixin, BaseUpdateMixin, mask_view


class PurchaseRequestConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PurchaseRequestConfig.objects  # noqa
    serializer_detail = PurchaseRequestConfigDetailSerializer
    serializer_update = PurchaseRequestConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Purchase Request Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Purchase Request Config Update",
        request_body=PurchaseRequestConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
