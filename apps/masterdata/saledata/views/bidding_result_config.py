from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models.bidding_result_config import BiddingResultConfig
from apps.masterdata.saledata.serializers.bidding_result_config import (BiddingResultConfigListSerializer,
                                                                        BiddingResultConfigCreateSerializer,
                                                                        BiddingResultConfigDetailSerializer)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin

# Create your views here.
class BiddingResultConfigList(BaseListMixin, BaseCreateMixin):
    queryset = BiddingResultConfig.objects
    serializer_list = BiddingResultConfigListSerializer
    serializer_create = BiddingResultConfigCreateSerializer
    serializer_detail = BiddingResultConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Bidding Result Config list",
        operation_description="Bidding Result Config list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Bidding Result Config",
        operation_description="Create new Bidding Result Config",
        request_body=BiddingResultConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
