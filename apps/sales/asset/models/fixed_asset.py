from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.company.models import CompanyFunctionNumber
from apps.sales.apinvoice.models import APInvoice, APInvoiceItems
from apps.sales.financialcashflow.models import CashOutflow
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct
from apps.sales.report.utils import IRForGoodsIssueHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel

__all__ = [
    'FixedAsset',
    'FixedAssetUseDepartment',
    'FixedAssetInventoryItem',
    'FixedAssetApInvoicePurchaseItem',
    'FixedAssetApInvoicePurchaseItemDetailProduct',
    'FixedAssetCashOutPurchaseItem',
    'FixedAssetDepreciation'
]

FIXED_ASSET_STATUS = [
    (0, _('Using')),
    (1, _('Leased')),
    (2, _('Delivered')),
    (3, _('Under Maintenance')),
    (4, _('Fully Depreciated')),
]

SOURCE_TYPE_CHOICES = [
    (0, _('Transfer from Inventory')),
    (1, _('Purchase Fixed Assets')),
    (2, _('Self-Manufactured Fixed Assets')),
    (3, _('Capital Construction Investment')),
    (4, _('Donation / Sponsorship')),
    (5, _('Receive Capital Contribution')),
]

DEPRECIATION_TYPE_CHOICES = [
    (0, _('Straight line depreciation')),
    (1, _('Adjusted reducing balance')),
]

TRACEABILITY_METHOD_SELECTION = [
    (0, _('None')),
    (1, _('Batch/Lot number')),
    (2, _('Serial number'))
]

class FixedAsset(DataAbstractModel):
    asset_code = models.CharField(max_length=100, blank=True)
    manage_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.SET_NULL,
        related_name="department_fixed_assets",
        null=True
    )
    use_customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        related_name="account_fixed_assets",
        null=True
    )
    status = models.PositiveSmallIntegerField(
        default=0,
        choices=FIXED_ASSET_STATUS,
    )
    source_type = models.PositiveSmallIntegerField(
        default=0,
        choices=SOURCE_TYPE_CHOICES,
    )
    asset_category = models.ForeignKey(
        'accountingsettings.AssetCategory',
        on_delete=models.CASCADE,
        null=True,
        related_name="asset_category_fixed_assets",
    )

    # depreciation + value:
    original_cost = models.FloatField(default=0)
    accumulative_depreciation = models.FloatField(default=0)
    net_book_value = models.FloatField(default=0)
    depreciation_method = models.PositiveSmallIntegerField(
        default=0,
        choices=DEPRECIATION_TYPE_CHOICES,
    )
    depreciation_time = models.PositiveIntegerField(default=0)
    depreciation_time_unit = models.PositiveSmallIntegerField(
        default=0,
        choices=[
            (0, _('Month')),
            (1, _('Year')),
        ],
    )
    adjustment_factor = models.FloatField(null=True)
    depreciation_start_date = models.DateTimeField()
    depreciation_end_date = models.DateTimeField()
    depreciation_value = models.FloatField(null=True)

    fixed_asset_write_off = models.ForeignKey(
        'asset.FixedAssetWriteOff',
        on_delete=models.SET_NULL,
        null=True,
        related_name="write_off_fixed_assets",
    )

    depreciation_data = models.JSONField(default=list, help_text='data for depreciation')
    last_posted_date = models.DateField(null=True, help_text='latest date which asset run depreciation')

    # GL accounts
    asset_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_account_assets',
    )
    accumulated_depreciation_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='accumulated_depreciation_assets',
    )
    depreciation_expense_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='depreciation_expense_assets',
    )

    class Meta:
        verbose_name = 'Fixed Asset'
        verbose_name_plural = 'Fixed Assets'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'fc552ebb-eb98-4d7b-81cd-e4b5813b7815'  # fixed asset's application id

    @classmethod
    def get_inventory_item_data(cls, fa_obj):
        inventory_item_data = []
        for item in fa_obj.inventory_items.all():
            try:
                uom = item.product.general_uom_group.uom_reference
            except AttributeError:
                uom = None

            if item.tracking_method == 0:
                inventory_item_data.append({
                    'fixed_asset_item': item,
                    'product': item.product,
                    'product_data': {
                        "id": str(item.product_id),
                        "code": item.product.code,
                        "title": item.product.title,
                        "description": item.product.description,
                        "general_traceability_method": item.product.general_traceability_method
                    } if item.product else {},
                    'warehouse': item.warehouse,
                    'warehouse_data': {
                        'id': str(item.warehouse_id), 'code': item.warehouse.code, 'title': item.warehouse.title,
                    } if item.warehouse else {},
                    'uom': uom,
                    'uom_data': {
                        'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                    } if uom else {},
                    'before_quantity': 1,
                    'remain_quantity': 1,
                    'issued_quantity': 1,
                    'lot_data': [],
                    'sn_data': []
                })
            if item.tracking_method == 1:
                inventory_item_data.append({
                    'fixed_asset_item': item,
                    'product': item.product,
                    'product_data': {
                        "id": str(item.product_id),
                        "code": item.product.code,
                        "title": item.product.title,
                        "description": item.product.description,
                        "general_traceability_method": item.product.general_traceability_method
                    } if item.product else {},
                    'warehouse': item.warehouse,
                    'warehouse_data': {
                        'id': str(item.warehouse_id), 'code': item.warehouse.code, 'title': item.warehouse.title,
                    } if item.warehouse else {},
                    'uom': uom,
                    'uom_data': {
                        'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                    } if uom else {},
                    'before_quantity': 1,
                    'remain_quantity': 1,
                    'issued_quantity': 1,
                    'lot_data': [{
                        'lot_id': str(item.product_warehouse_lot_id),
                        'old_quantity': item.product_warehouse_lot.quantity_import,
                        'quantity': 1
                    }],
                    'sn_data': []
                })
            if item.tracking_method == 2:
                inventory_item_data.append({
                    'fixed_asset_item': item,
                    'product': item.product,
                    'product_data': {
                        "id": str(item.product_id),
                        "code": item.product.code,
                        "title": item.product.title,
                        "description": item.product.description,
                        "general_traceability_method": item.product.general_traceability_method
                    } if item.product else {},
                    'warehouse': item.warehouse,
                    'warehouse_data': {
                        'id': str(item.warehouse_id), 'code': item.warehouse.code, 'title': item.warehouse.title,
                    } if item.warehouse else {},
                    'uom': uom,
                    'uom_data': {
                        'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                    } if uom else {},
                    'before_quantity': 1,
                    'remain_quantity': 1,
                    'issued_quantity': 1,
                    'lot_data': [],
                    'sn_data': [str(item.product_warehouse_serial_id)]
                })
        return inventory_item_data

    @classmethod
    def auto_create_goods_issue(cls, fa_obj):
        """ Phiếu Xuất kho được tạo từ chức năng này sẽ tự động duyệt mà không quan tâm quy trình như thế nào """
        gis_data = {
            'title': f'Goods issue for {fa_obj.code}',
            'goods_issue_type': 4,
            'fixed_asset': fa_obj,
            'system_auto_create': True,
            'tenant': fa_obj.tenant,
            'company': fa_obj.company,
            'employee_created': fa_obj.employee_created,
            'employee_inherit': fa_obj.employee_inherit,
            'date_created': timezone.now(),
            'date_approved': timezone.now(),
        }
        gis_obj = GoodsIssue.objects.create(**gis_data)
        bulk_info = []
        detail_data = cls.get_inventory_item_data(fa_obj)
        for item in detail_data:
            bulk_info.append(GoodsIssueProduct(goods_issue=gis_obj, **item))
        GoodsIssueProduct.objects.filter(goods_issue=gis_obj).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_info)

        # duyệt tự động
        CompanyFunctionNumber.auto_gen_code_based_on_config(
            app_code=None, instance=gis_obj, in_workflow=True, kwargs=None
        )
        gis_obj.system_status = 3
        gis_obj.save(update_fields=['code', 'system_status'])
        # action sau khi duyệt
        gis_obj.update_related_app_after_issue(gis_obj)
        new_logs = IRForGoodsIssueHandler.push_to_inventory_report(gis_obj)

        return {'gis_obj': gis_obj, 'new_logs': new_logs}

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    # B1: xuất hàng
                    self.auto_create_goods_issue(self)
        # hit DB
        super().save(*args, **kwargs)


class FixedAssetDepreciation(MasterDataAbstractModel):
    fixed_asset = models.ForeignKey(
        FixedAsset,
        related_name='depreciations',
        on_delete=models.CASCADE,
    )
    start_date = models.DateField()
    end_date = models.DateField()

    # Number of months
    period_months = models.FloatField()  # This period: 0.5, 1, 1, ...
    accumulated_months = models.FloatField()  # Running total: 0.5, 1.5, 2.5, ...

    # Money values
    period_depreciation = models.FloatField()  # Depreciation amount this period
    accumulated_depreciation = models.FloatField()  # Running total depreciation

    is_posted = models.BooleanField()


class FixedAssetUseDepartment(MasterDataAbstractModel):
    fixed_asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        related_name="use_departments",
        null=True
    )
    use_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="fixed_assets",
        null=True
    )


class FixedAssetInventoryItem(MasterDataAbstractModel):
    fixed_asset = models.ForeignKey(
        'FixedAsset',
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.SET_NULL,
        related_name="product_inventory_items",
        null=True
    )
    product_warehouse_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial',
        on_delete=models.SET_NULL,
        related_name="product_warehouse_serial_inventory_items",
        null=True
    )
    product_warehouse_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name="product_warehouse_lot_inventory_items",
        null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.SET_NULL,
        related_name="warehouse_inventory_items",
        null=True
    )
    tracking_number = models.TextField()
    tracking_method = models.PositiveSmallIntegerField(
        default=0,
        choices=TRACEABILITY_METHOD_SELECTION
    )
    total_register_value = models.FloatField(default=0)


class FixedAssetApInvoicePurchaseItem(MasterDataAbstractModel):
    fixed_asset = models.ForeignKey(
        'FixedAsset',
        on_delete=models.CASCADE,
        related_name="ap_purchase_items",
    )
    ap_invoice = models.ForeignKey(
        APInvoice,
        on_delete=models.SET_NULL,
        related_name="asset_purchase_items",
        null=True
    )
    total_register_value = models.FloatField(default=0)


class FixedAssetApInvoicePurchaseItemDetailProduct(MasterDataAbstractModel):
    ap_invoice_item = models.ForeignKey(
        APInvoiceItems,
        on_delete=models.SET_NULL,
        related_name="ap_invoice_item_detail_products",
        null=True
    )
    ap_invoice_purchase_item = models.ForeignKey(
        'FixedAssetApInvoicePurchaseItem',
        on_delete=models.CASCADE,
        related_name='detail_products'
    )
    quantity = models.IntegerField(default=0)
    unit_price = models.FloatField(default=0)
    amount = models.FloatField(default=0)


class FixedAssetCashOutPurchaseItem(MasterDataAbstractModel):
    fixed_asset = models.ForeignKey(
        'FixedAsset',
        on_delete=models.CASCADE,
        related_name="cash_out_purchase_items",
    )
    cash_out = models.ForeignKey(
        CashOutflow,
        on_delete=models.SET_NULL,
        related_name="asset_purchase_items",
        null=True
    )
    total_register_value = models.FloatField(default=0)
