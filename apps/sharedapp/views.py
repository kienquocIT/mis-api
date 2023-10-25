from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared.extends.signals import SaleDefaultData
from apps.shared import ResponseController


class DefaultDataStorageView(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        data = {
            "sale": {
                "Product Type": SaleDefaultData.ProductType_data,
                "Tax Category": SaleDefaultData.TaxCategory_data,
                "Currency": SaleDefaultData.Currency_data,
            }
        }
        return ResponseController.success_200(
            data=data,
            key_data='result',
        )


class ApplicationConfigData(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        data = {
            "sale": {
                "Product Type": SaleDefaultData.ProductType_data,
                "Tax Category": SaleDefaultData.TaxCategory_data,
                "Currency": SaleDefaultData.Currency_data,
            }
        }
        return ResponseController.success_200(
            data=data,
            key_data='result',
        )
