__all__ = ['AssetToolsReturn', 'AssetToolsReturnMapProduct', 'AssetToolsReturnAttachmentFile']

import json

from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import ProductWareHouse
from apps.shared import DataAbstractModel, AssetToolsMsg


class AssetToolsReturn(DataAbstractModel):
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Employee inherit backup data',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': '', 'group': {'id': '', 'title': '', 'code': ''}}
            ]
        )
    )
    remark = models.CharField(
        verbose_name='Descriptions',
        max_length=500,
        null=True,
        blank=True
    )
    products = models.ManyToManyField(
        'saledata.Product',
        through='AssetToolsReturnMapProduct',
        symmetrical=False,
        related_name='products_asset_return',
    )
    return_info_list = models.JSONField(
        default=dict,
        verbose_name='Log info when return asset',
        help_text=json.dumps(
            [
                {
                    'product': {'id': '', 'title': '', 'code': ''},
                    'return_number': 0,
                    'reason': 'error message'
                }
            ]
        )
    )
    attachments = models.ManyToManyField(
        'attachments.Files',
        through='AssetToolsReturnAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_asset_return',
    )
    date_return = models.DateTimeField(
        default=timezone.now,
        help_text='Date Return asset, tools',
    )

    def code_generator(self):
        if not self.code:
            asset_return = AssetToolsReturn.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_delete=False,
                system_status__gte=2
            ).count()
            char = "ATR"
            num_quotient, num_remainder = divmod(asset_return, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def return_product_used(self):
        return_info_list = []
        if not self.code:
            prod_list = AssetToolsReturnMapProduct.objects.filter(
                asset_return_id=str(self.id),
            ).select_related('product')
            product_warehouse_list = []
            for item in prod_list:
                count = item.return_number
                item_prod = item.product
                if item_prod and 1 in item_prod.product_choice:
                    prod_warehouse = item.product.product_warehouse_product.first()
                    if prod_warehouse.used_amount < count:
                        return_info_list.append(
                            {
                                'product': item_prod.product_data if item_prod.product_data else {},
                                'return_number': count,
                                'reason': AssetToolsMsg.RETURN_PRODUCT_ERROR01
                            }
                        )
                        raise ValueError(AssetToolsMsg.RETURN_PRODUCT_ERROR01)
                    # minus used_amount in ProductWareHouse if product has control inventory
                    prod_warehouse.used_amount -= count
                    product_warehouse_list.append(prod_warehouse)
            if return_info_list:
                self.return_info_list = return_info_list
            if product_warehouse_list:
                ProductWareHouse.objects.bulk_update(product_warehouse_list, fields=['used_amount'])

        return True, return_info_list

    def create_backup_data(self):
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        return True

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        if self.system_status >= 2:
            done_update, err_list = self.return_product_used()
            self.code_generator()
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
                if done_update and err_list:
                    kwargs['update_fields'].append('return_info_list')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset return'
        verbose_name_plural = 'Assets return'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AssetToolsReturnMapProduct(DataAbstractModel):
    asset_return = models.ForeignKey(
        'assettools.AssetToolsReturn',
        on_delete=models.CASCADE,
        verbose_name='Asset return map product',
        related_name='asset_return_map_product',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product map asset return',
        related_name='product_map_asset_return',
    )
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product data backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': '', 'uom': {'id': '', 'code': ''}}
            ]
        )
    )
    warehouse_stored_product = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name='Warehouse stored product',
        related_name='warehouse_stored_product',
    )
    warehouse_sp_data = models.JSONField(
        default=dict,
        verbose_name='warehouse info backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': ''}
            ]
        )
    )
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Employee info backup',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': ''}
            ]
        )
    )
    return_number = models.IntegerField(
        default=0, verbose_name='Return number',
    )
    order = models.IntegerField(
        default=1, verbose_name='Order',
    )

    def create_backup_data(self):
        if self.product:
            self.product_data = {
                "id": str(self.product_id),
                "title": self.product.title,
                "code": self.product.code,
                "uom_data": {
                    "id": str(self.product.inventory_uom_id),
                    "title": self.product.inventory_uom.title,
                }
            }
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        if self.warehouse_stored_product:
            self.warehouse_sp_data = {
                "id": str(self.warehouse_stored_product_id),
                "title": self.warehouse_stored_product.title,
                "code": self.warehouse_stored_product.code
            }

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset, Tools Return Map product'
        verbose_name_plural = 'Asset, Tools Return Map product'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AssetToolsReturnAttachmentFile(M2MFilesAbstractModel):
    asset_tools_return = models.ForeignKey(
        'assettools.AssetToolsReturn',
        on_delete=models.CASCADE,
        verbose_name='Attachment file of Asset, Tools return'
    )

    @classmethod
    def get_doc_field_name(cls):
        # field name là foreignkey của request trên bảng này
        return 'asset_tools_return'

    class Meta:
        verbose_name = 'Asset, Tools return attachments'
        verbose_name_plural = 'Asset, Tools return attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
