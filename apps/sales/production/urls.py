from django.urls import path

from apps.sales.production.views import ProductionOrderList, ProductionOrderDetail, ProductionOrderDDList
from apps.sales.production.views.bom import (
    LaborListForBOM, ProductMaterialListForBOM, ProductToolsListForBOM,
    BOMList, BOMDetail, BOMOrderList, FinishProductListForBOM
)

urlpatterns = [
    path('finish-product-list-for-BOM', FinishProductListForBOM.as_view(), name='FinishProductListForBOM'),
    path('labor-list-for-BOM', LaborListForBOM.as_view(), name='LaborListForBOM'),
    path('product-material-list-for-BOM', ProductMaterialListForBOM.as_view(), name='ProductMaterialListForBOM'),
    path('product-tool-list-for-BOM', ProductToolsListForBOM.as_view(), name='ProductToolsListForBOM'),
    # BEGIN
    path('bom/list', BOMList.as_view(), name='BOMList'),
    path('bom/<str:pk>', BOMDetail.as_view(), name='BOMDetail'),

    path('bom-order/list', BOMOrderList.as_view(), name='BOMOrderList'),

    # Production order
    path('production-order/list', ProductionOrderList.as_view(), name='ProductionOrderList'),
    path('production-order/<str:pk>', ProductionOrderDetail.as_view(), name='ProductionOrderDetail'),
    path('production-order-dd/list', ProductionOrderDDList.as_view(), name='ProductionOrderDDList'),
]
