from django.urls import path
from apps.masterdata.saledata.views.contacts import (
    SalutationList, SalutationDetail, InterestsList, InterestsDetail, ContactList, ContactDetail,
    ContactListNotMapAccount,
)
from apps.masterdata.saledata.views.accounts import (
    AccountTypeList, AccountTypeDetail, IndustryList, IndustryDetail,
    AccountList, AccountDetail, AccountGroupList, AccountGroupDetail, AccountsMapEmployeesList, AccountForSaleList,
)
from apps.masterdata.saledata.views.config import ConfigPaymentTermList, ConfigPaymentTermDetail
from apps.masterdata.saledata.views.expense import ExpenseList, ExpenseDetail
from apps.masterdata.saledata.views.good_receipt import GoodReceiptDetail
from apps.masterdata.saledata.views.product import (
    ProductTypeList, ProductTypeDetail, ProductCategoryList, ProductCategoryDetail,
    ExpenseTypeList, ExpenseTypeDetail, UnitOfMeasureGroupList, UnitOfMeasureGroupDetail,
    UnitOfMeasureList, UnitOfMeasureDetail, ProductList, ProductDetail,
)
from apps.masterdata.saledata.views.price import (
    TaxCategoryList, TaxCategoryDetail, TaxList, TaxDetail, CurrencyList, CurrencyDetail, SyncWithVCB,
    PriceList, PriceDetail, PriceDelete, UpdateItemsForPriceList, DeleteItemForPriceList, ItemAddFromPriceList,
)
from apps.masterdata.saledata.views import (
    ShippingList, ShippingDetail,
    WareHouseList, WareHouseDetail, GoodReceiptList, ShippingCheckList, WarehouseStockList,
)

urlpatterns = [
    path('salutations', SalutationList.as_view(), name='SalutationList'),
    path('salutation/<str:pk>', SalutationDetail.as_view(), name='SalutationDetail'),
    path('interests', InterestsList.as_view(), name='InterestsList'),
    path('interest/<str:pk>', InterestsDetail.as_view(), name='InterestDetail'),
    path('accounttypes', AccountTypeList.as_view(), name='AccountTypeList'),
    path('accounttype/<str:pk>', AccountTypeDetail.as_view(), name='AccountTypeDetail'),
    path('accountgroups', AccountGroupList.as_view(), name='AccountGroupList'),
    path('accountgroup/<str:pk>', AccountGroupDetail.as_view(), name='AccountGroupDetail'),
    path('industries', IndustryList.as_view(), name='IndustryList'),
    path('industry/<str:pk>', IndustryDetail.as_view(), name='IndustryDetail'),

    # contact
    path('contacts', ContactList.as_view(), name='ContactList'),
    path('contact/<str:pk>', ContactDetail.as_view(), name='ContactDetail'),
    path('contacts-not-map-account', ContactListNotMapAccount.as_view(), name='ContactListNotMapAccount'),

    # account
    path('accounts', AccountList.as_view(), name='AccountList'),
    path('account/<str:pk>', AccountDetail.as_view(), name='AccountDetail'),
    path('accounts-map-employees', AccountsMapEmployeesList.as_view(), name='AccountsMapEmployeesList'),
    path('accounts-sale', AccountForSaleList.as_view(), name='AccountForSaleList'),
]

urlpatterns += [
    path('product-types', ProductTypeList.as_view(), name='ProductTypeList'),
    path('product-type/<str:pk>', ProductTypeDetail.as_view(), name='ProductTypeDetail'),
    path('product-categories', ProductCategoryList.as_view(), name='ProductCategoryList'),
    path('product-category/<str:pk>', ProductCategoryDetail.as_view(), name='ProductCategoryDetail'),

    path('expense-types', ExpenseTypeList.as_view(), name='ExpenseTypeList'),
    path('expense-type/<str:pk>', ExpenseTypeDetail.as_view(), name='ExpenseTypeDetail'),

    path('units-of-measure-group', UnitOfMeasureGroupList.as_view(), name='UnitOfMeasureGroupList'),
    path('unit-of-measure-group/<str:pk>', UnitOfMeasureGroupDetail.as_view(), name='UnitOfMeasureGroupDetail'),
    path('units-of-measure', UnitOfMeasureList.as_view(), name='UnitOfMeasureList'),
    path('unit-of-measure/<str:pk>', UnitOfMeasureDetail.as_view(), name='UnitOfMeasureDetail'),
]

urlpatterns += [
    path('products', ProductList.as_view(), name='ProductList'),
    path('create-product-from-price-list/<str:pk>', ItemAddFromPriceList.as_view(), name='ItemAddFromPriceList'),
    path('product/<str:pk>', ProductDetail.as_view(), name='ProductDetail'),
]

urlpatterns += [
    path('tax-categories', TaxCategoryList.as_view(), name='TaxCategoryList'),
    path('tax-category/<str:pk>', TaxCategoryDetail.as_view(), name='TaxCategoryDetail'),
    path('taxes', TaxList.as_view(), name='TaxList'),
    path('tax/<str:pk>', TaxDetail.as_view(), name='TaxDetail'),
    path('currencies', CurrencyList.as_view(), name='CurrencyList'),
    path('currency/<str:pk>', CurrencyDetail.as_view(), name='CurrencyDetail'),
    path('sync-selling-rate-with-VCB/<str:pk>', SyncWithVCB.as_view(), name='SyncWithVCB'),
]

urlpatterns += [
    path('prices', PriceList.as_view(), name='PriceList'),
    path('price/<str:pk>', PriceDetail.as_view(), name='PriceDetail'),
    path('delete-price/<str:pk>', PriceDelete.as_view(), name='PriceDelete'),
    path(
        'update-products-for-price-list/<str:pk>', UpdateItemsForPriceList.as_view(),
        name='UpdateProductsForPriceList'
    ),
    path(
        'delete-products-for-price-list/<str:pk>', DeleteItemForPriceList.as_view(),
        name='DeleteItemForPriceList'
    ),
]

urlpatterns += [
    path('masterdata/config/payment-term', ConfigPaymentTermList.as_view(), name='ConfigPaymentTermList'),
    path(
        'masterdata/config/payment-term/<str:pk>',
        ConfigPaymentTermDetail.as_view(),
        name='ConfigPaymentTermDetail'
    ),
]

urlpatterns += [
    path('expenses', ExpenseList.as_view(), name='ExpenseList'),
    path('expense/<str:pk>', ExpenseDetail.as_view(), name='ExpenseDetail')
]

urlpatterns += [
    path('shippings', ShippingList.as_view(), name='ShippingList'),
    path('shipping/<str:pk>', ShippingDetail.as_view(), name='ShippingDetail'),
    path('shippings-check', ShippingCheckList.as_view(), name='ShippingCheckList'),
]

# warehouse
urlpatterns += [
    path('warehouses', WareHouseList.as_view(), name='WareHouseList'),
    path('warehouse/<str:pk>', WareHouseDetail.as_view(), name='WareHouseDetail'),
    path('warehouse-stock', WarehouseStockList.as_view(), name='WarehouseStockList'),
]
# // warehouse


# good receipt
urlpatterns += [
    path('good-receipt', GoodReceiptList.as_view(), name='GoodReceiptList'),
    path('good-receipt/<str:pk>', GoodReceiptDetail.as_view(), name='GoodReceiptDetail'),
]
# // end good receipt
