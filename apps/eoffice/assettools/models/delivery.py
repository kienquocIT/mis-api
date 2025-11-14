__all__ = ['AssetToolsDelivery', 'AssetToolsDeliveryAttachmentFile', 'ProductDeliveredMapProvide']

import json

from django.db import models, transaction
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel, update_files_is_approved
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, AssetToolsMsg, DisperseModel


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
    prod_in_tools = models.ManyToManyField(
        'asset.InstrumentTool',
        through='ProductDeliveredMapProvide',
        symmetrical=False,
        related_name='prod_asset_tools_delivery',
    )
    attachments = models.ManyToManyField(
        'attachments.Files',
        through='AssetToolsDeliveryAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_asset_delivery',
    )

    def update_product_used(self):
        provide_prod_models = DisperseModel(app_model='assettools.AssetToolsProvideProduct').get_model()

        def handle_provide_completed(provide):
            # loop trong danh sách prod_map_provide nếu tất cả product đều cấp hết check complete_delivered
            # cho provide đó
            model_provide_lst = provide_prod_models.objects.filter(asset_tools_provide=provide)
            is_completed = True
            for prov_item in model_provide_lst:
                if prov_item.quantity != prov_item.delivered:
                    is_completed = False
                    break
            if is_completed:
                provide.complete_delivered = True
                provide.save(update_fields=['complete_delivered'])

        def update_provide(prod_map_queryset, number_delivered):
            if prod_map_queryset.exists():
                for prod_item in prod_map_queryset:
                    # nếu số đã giao còn nhỏ hơn số lượng cần giao
                    if prod_item.delivered < prod_item.quantity:
                        remaining = prod_item.delivered + number_delivered
                        if remaining <= prod_item.quantity:
                            prod_item.delivered += number_delivered
                    prod_item.save(update_fields=['delivered'])

        try:
            with transaction.atomic():
                if self.system_status == 3:
                    # lấy danh sách prod_map_deliver
                    prod_map_deliver_lst = ProductDeliveredMapProvide.objects.filter_on_company(
                        delivery_id=str(self.id),
                    ).select_related('prod_in_tools', 'prod_in_fixed')
                    for item in prod_map_deliver_lst:
                        delivered = item.done
                        product_is_tool = item.prod_in_tools
                        product_is_fixed = item.prod_in_fixed

                        if product_is_tool:
                            prod_available = product_is_tool.quantity - product_is_tool.allocated_quantity
                            if prod_available < delivered:
                                raise ValueError(AssetToolsMsg.ERROR_UPDATE_DELIVERED)

                            item.delivered_number += delivered
                            product_is_tool.allocated_quantity += delivered
                            if product_is_tool.allocated_quantity == product_is_tool.quantity:
                                product_is_tool.status = 2
                            product_is_tool.save(update_fields=["allocated_quantity", "status"])

                            prod_map_provide = self.provide.asset_provide_map_product.all().filter(
                                prod_in_tools_id=product_is_tool.id
                            )
                        elif product_is_fixed:
                            if delivered > 1:
                                raise ValueError(AssetToolsMsg.ERROR_UPDATE_DELIVERED)
                            item.delivered_number += delivered
                            product_is_fixed.status = 2
                            product_is_fixed.save(update_fields=["status"])
                            prod_map_provide = self.provide.asset_provide_map_product.all().filter(
                                prod_in_fixed_id=product_is_fixed.id
                            )
                        else:
                            item.delivered_number += delivered
                            prod_map_provide = self.provide.asset_provide_map_product.all().filter(
                                product_remark=item.prod_buy_new
                            )

                        update_provide(prod_map_provide, delivered)
                        item.save(update_fields=["delivered_number"])
                    handle_provide_completed(self.provide)
        except ValueError:
            raise ValueError(AssetToolsMsg.ERROR_UPDATE_DELIVERED)
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
                    "title": self.employee_inherit.group.title,
                    "code": self.employee_inherit.group.code,
                } if hasattr(self.employee_inherit.group, 'id') else {}
            }
        return True

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        if self.system_status >= 2:
            self.update_product_used()
            update_files_is_approved(
                AssetToolsDeliveryAttachmentFile.objects.filter(
                    asset_tools_delivery=self, attachment__is_approved=False
                ),
                self
            )
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
            if 'date_approved' in kwargs['update_fields']:
                CompanyFunctionNumber.auto_gen_code_based_on_config('assettoolsdelivery', True, self, kwargs)
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
    prod_buy_new = models.CharField(
        verbose_name='Title of Product buy new',
        max_length=500,
        null=True,
        blank=True
    )
    prod_in_tools = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name='Product provide map with request delivery',
        related_name='product_map_asset_tools_delivery',
        null=True
    )
    prod_in_fixed = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        verbose_name='Product fixed map with request delivery',
        related_name='product_asset_map_delivery',
        null=True
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
    uom = models.CharField(
        verbose_name='Unit of Measure',
        max_length=500,
        null=True,
        blank=True
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

    def create_backup_data(self):
        if self.prod_in_tools:
            self.product_data = {
                "id": str(self.prod_in_tools.id),
                "title": self.prod_in_tools.title,
                "code": self.prod_in_tools.code,
                "uom": self.prod_in_tools.measure_unit if hasattr(self.prod_in_tools, 'measure_unit') else '',
            }
        if self.prod_in_fixed:
            self.product_data = {
                "id": str(self.prod_in_fixed.id),
                "title": self.prod_in_fixed.title,
                "code": self.prod_in_fixed.code,
            }
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code,
                "group": {
                    "id": str(self.employee_inherit.group.id),
                    "title": self.employee_inherit.group.title,
                    "code": self.employee_inherit.group.code
                } if hasattr(self.employee_inherit.group, 'id') else {}

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
