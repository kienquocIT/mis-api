__all__ = ['AssetToolsDelivery', 'AssetToolsDeliveryAttachmentFile', 'ProductDeliveredMapProvide']

import json

from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import ProductWareHouse
from apps.shared import DataAbstractModel, AssetToolsMsg
from .provide import AssetToolsProvideProduct


class AssetToolsDelivery(DataAbstractModel):
    provide = models.ForeignKey(
        'assettools.AssetToolsProvide',
        on_delete=models.CASCADE,
        verbose_name='request provide of employee',
        related_name='provide_asset_tools_delivery',
    )
    provide_data = models.JSONField(
        default=dict,
        verbose_name='Request provide of employee backup data',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': ''}
            ]
        )
    )
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Request provide of employee backup data',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': '', 'group': {'id': '', 'title': '', 'code': ''}}
            ]
        )
    )
    provide_inheritor = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='Provide inheritor',
        related_name='%(app_label)s_%(class)s_employee_inheritor',
    )
    remark = models.CharField(
        verbose_name='Descriptions',
        max_length=500,
        null=True,
        blank=True
    )
    products = models.ManyToManyField(
        'saledata.Product',
        through='ProductDeliveredMapProvide',
        symmetrical=False,
        related_name='products_asset_tools_delivery',
    )
    attachments = models.ManyToManyField(
        'attachments.Files',
        through='AssetToolsDeliveryAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_asset_delivery',
    )

    def code_generator(self):
        if not self.code:
            ast_p = AssetToolsDelivery.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_delete=False,
                system_status__gte=2
            ).count()
            char = "ATD"
            num_quotient, num_remainder = divmod(ast_p, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def update_product_used(self):
        if not self.code:
            prod_list = ProductDeliveredMapProvide.objects.filter(
                delivery_id=str(self.id),
            )
            product_asset_list = []
            product_warehouse_list = []
            for item in prod_list:
                count = item.done
                row_item = item.product.product_map_asset_provide.filter(
                    asset_tools_provide=self.provide,
                ).first()  # bảng AssetToolsProvideProduct
                if row_item:
                    # update delivered cho provide product
                    row_item.delivered += count
                    if row_item.delivered > row_item.quantity:
                        raise ValueError(AssetToolsMsg.ERROR_UPDATE_DELIVERED)
                    product_asset_list.append(row_item)

                    # update used_amount cho prod trong warehouse bảng ProductWareHouse
                    if 1 in item.product.product_choice:
                        prod_warehouse = item.product.product_warehouse_product.first()
                        if (prod_warehouse.stock_amount - prod_warehouse.used_amount) < count:
                            raise ValueError(AssetToolsMsg.ERROR_UPDATE_DELIVERED)
                        prod_warehouse.used_amount += count
                        product_warehouse_list.append(prod_warehouse)
            if product_asset_list:
                AssetToolsProvideProduct.objects.bulk_update(product_asset_list, fields=['delivered'])
            if product_warehouse_list:
                ProductWareHouse.objects.bulk_update(product_warehouse_list, fields=['used_amount'])

            check_lst = AssetToolsProvideProduct.objects.filter(asset_tools_provide=self.provide)
            is_completed = True
            for item in check_lst:
                if item.quantity != item.delivered:
                    is_completed = False
                    break
            if is_completed:
                self.provide.complete_delivered = True
                self.provide.save(update_fields=['complete_delivered'])
        return True

    def create_backup_data(self):
        if self.provide:
            self.provide_data = {
                "id": str(self.provide_id),
                "title": self.provide.title,
                "code": self.provide.code
            }
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code,
                "group": {
                    "id": str(self.employee_inherit.group_id),
                    "title": str(self.employee_inherit.group.title),
                    "code": str(self.employee_inherit.group.code),
                },
            }
        return True

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        if self.system_status >= 2:
            self.update_product_used()
            self.code_generator()
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset, Tools Delivery'
        verbose_name_plural = 'Asset, Tools Delivery'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductDeliveredMapProvide(DataAbstractModel):
    delivery = models.ForeignKey(
        'assettools.AssetToolsDelivery',
        on_delete=models.CASCADE,
        verbose_name='Product map delivery',
        related_name='provide_map_delivery',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product provide map with request delivery',
        related_name='product_map_asset_tools_delivery',
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
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name='Product had provided at warehouse',
        related_name='product_provided_at_warehouse',
    )
    warehouse_data = models.JSONField(
        default=dict,
        verbose_name='Warehouse info backup',
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
                {'id': '', 'full_name': '', 'code': '', 'group': {'id': '', 'title': ''}}
            ]
        )
    )
    request_number = models.IntegerField(
        default=0, verbose_name='Request number',
    )
    delivered_number = models.IntegerField(
        default=0, verbose_name='Delivered number',
    )
    done = models.IntegerField(
        default=0, verbose_name='Done',
    )
    date_delivered = models.DateTimeField(
        default=timezone.now,
        help_text='Date delivered asset, tools',
    )
    order = models.IntegerField(
        default=1, verbose_name='Order',
    )
    is_inventory = models.BooleanField(
        default=False, verbose_name='Has Inventory',
    )

    def create_backup_data(self):
        if self.product:
            self.product_data = {
                "id": str(self.product_id),
                "title": self.product.title,
                "code": self.product.code,
                "uom": {
                    "id": str(self.product.inventory_uom.id),
                    "title": self.product.inventory_uom.title,
                    "code": self.product.inventory_uom.code
                }
            }
        if self.warehouse:
            self.warehouse_data = {
                "id": str(self.warehouse_id),
                "title": self.warehouse.title,
                "code": self.warehouse.code,
            }
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code,
                "group": {
                    "id": str(self.employee_inherit.group_id),
                    "title": self.employee_inherit.group.title,
                    "code": self.employee_inherit.group.code
                }

            }

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset, Tools Delivery Map product'
        verbose_name_plural = 'Asset, Tools Delivery Map product'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AssetToolsDeliveryAttachmentFile(M2MFilesAbstractModel):
    asset_tools_delivery = models.ForeignKey(
        'assettools.AssetToolsDelivery',
        on_delete=models.CASCADE,
        verbose_name='Attachment file of Asset, Tools delivery'
    )

    @classmethod
    def get_doc_field_name(cls):
        # field name là foreignkey của request trên bảng này
        return 'asset_tools_delivery'

    class Meta:
        verbose_name = 'Asset, Tools delivery attachments'
        verbose_name_plural = 'Asset, Tools delivery attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
