__all__ = ['AssetToolsReturn', 'AssetToolsReturnMapProduct', 'AssetToolsReturnAttachmentFile']

import json

from django.db import models, transaction
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, AssetToolsMsg, DisperseModel


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
    prod_in_tools = models.ManyToManyField(
        'asset.InstrumentTool',
        through='AssetToolsReturnMapProduct',
        symmetrical=False,
        related_name='prod_in_tools_asset_return',
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

    def update_prod_provide(self, prod_list, return_info_list, product_instrument_list):
        models_provide_map = DisperseModel(app_model='assettools.AssetToolsProvideProduct').get_model()
        for item in prod_list:
            count = item.return_number
            item_prod = item.prod_in_tools

            # Khởi tạo thông tin log trả sản phẩm
            return_info_list.append(
                {
                    'product': item.product_data if item.product_data else {},
                    'product_remark': item.product_remark,
                    'return_number': count,
                    'reason': self.remark
                }
            )

            # Nếu sản phẩm đã được cấp phát
            if item_prod:
                if item_prod.allocated_quantity < count:
                    raise ValueError(AssetToolsMsg.RETURN_PRODUCT_ERROR01)

                item_prod.allocated_quantity -= count
                product_instrument_list.append(item_prod)

                prod_provide_lst = item_prod.product_map_asset_provide.filter(
                    asset_tools_provide__employee_inherit=self.employee_inherit
                )
            else:
                # Sản phẩm chưa có trong công cụ cấp phát (dạng ghi chú)
                prod_provide_lst = models_provide_map.objects.filter(
                    asset_tools_provide__employee_inherit=self.employee_inherit,
                    product_remark=item.product_remark,
                    prod_in_tools__isnull=True
                )

            # Cập nhật số lượng trả cho từng mục cung cấp
            for provide_item in prod_provide_lst:
                available_return = provide_item.delivered - provide_item.is_returned
                if available_return <= 0:
                    continue

                returned_now = min(available_return, count)
                provide_item.is_returned += returned_now
                count -= returned_now

                if count == 0:
                    break

            models_provide_map.objects.bulk_update(prod_provide_lst, fields=['is_returned'])

    def return_product_used(self):
        return_info_list = []
        product_instrument_list = []
        models_instrument = DisperseModel(app_model='asset.InstrumentTool').get_model()

        try:
            with transaction.atomic():
                if self.system_status != 3:
                    return True, return_info_list

                prod_list = AssetToolsReturnMapProduct.objects.filter(
                    asset_return_id=str(self.id),
                ).select_related('prod_in_tools')

                self.update_prod_provide(prod_list, return_info_list, product_instrument_list)

                # Ghi nhận danh sách trả và cập nhật lại số lượng công cụ
                if return_info_list:
                    self.return_info_list = return_info_list

                if product_instrument_list:
                    models_instrument.objects.bulk_update(product_instrument_list, fields=['allocated_quantity'])

        except ValueError:
            raise ValueError(AssetToolsMsg.ERROR_CREATE_ASSET_RETURN)

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
    prod_in_tools = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name='Product map asset return',
        related_name='product_map_asset_return',
        null=True,
    )
    product_remark = models.CharField(verbose_name='Product title buy new', null=True, blank=True, max_length=500)
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product data backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': '', 'uom': {'id': '', 'code': ''}}
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
        if self.prod_in_tools:
            self.product_data = {
                "id": str(self.prod_in_tools_id),
                "title": self.prod_in_tools.title,
                "code": self.prod_in_tools.code
            }
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
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
