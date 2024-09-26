from django.urls import path

from apps.sales.production.views import ProductionOrderList, ProductionOrderDetail, ProductionOrderDDList
from apps.sales.production.views.bom import (
    LaborListForBOM, ProductMaterialListForBOM, ProductToolsListForBOM,
    BOMList, BOMDetail, BOMOrderList, ProductListForBOM
)
from apps.sales.production.views.production_report import ProductionReportList, ProductionReportDetail, \
    ProductionReportDDList, ProductionReportGRList
from apps.sales.production.views.work_order import WorkOrderList, WorkOrderDetail, WorkOrderDDList

urlpatterns = [
    path('product-list-for-BOM', ProductListForBOM.as_view(), name='ProductListForBOM'),
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

    # Production report
    path('production-report/list', ProductionReportList.as_view(), name='ProductionReportList'),
    path('production-report/<str:pk>', ProductionReportDetail.as_view(), name='ProductionReportDetail'),
    path('production-report-dd/list', ProductionReportDDList.as_view(), name='ProductionReportDDList'),
    path('production-report-gr/list', ProductionReportGRList.as_view(), name='ProductionReportGRList'),

    # Work order
    path('work-order/list', WorkOrderList.as_view(), name='WorkOrderList'),
    path('work-order/<str:pk>', WorkOrderDetail.as_view(), name='WorkOrderDetail'),
    path('work-order-dd/list', WorkOrderDDList.as_view(), name='WorkOrderDDList'),
]
