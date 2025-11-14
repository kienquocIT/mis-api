__all__ = ['AssetToolsReturn', 'AssetToolsReturnMapProduct', 'AssetToolsReturnAttachmentFile']

import json

from django.db import models, transaction
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel, update_files_is_approved
from apps.core.company.models import CompanyFunctionNumber
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

    def _prod_type_new(self, prod, employee_asset_list, return_number, provide_update_list, return_info_list):
        item = employee_asset_list.filter(
            prod_in_tools__isnull=True,
            prod_in_fixed__isnull=True,
            product_remark=prod.product_remark
        ).first()

        if item and item.quantity - item.is_returned > 0 and item.is_returned + return_number <= item.quantity:
            item.is_returned += return_number
            return_info_list.append(
                {
                    'product': {},
                    'product_remark': item.product_remark,
                    'return_number': return_number,
                    'reason': self.remark
                }
            )
            provide_update_list.append(item)

    def _prod_type_fixed(
            self,
            prod,
            models_fixed,
            employee_asset_list,
            return_number,
            provide_update_list,
            return_info_list,
            product_fixed_list
    ):
        prod_fixed = prod.prod_in_fixed
        prod_fixed_obj = models_fixed.objects.filter_on_company(id=prod_fixed['id'])
        if return_number != 1 or not prod_fixed_obj.exists():
            raise ValueError(AssetToolsMsg.RETURN_PRODUCT_ERROR01)

        prod_fixed_obj.status = 0
        item = employee_asset_list.filter(
            prod_in_tools__isnull=True,
            prod_in_fixed_id=prod_fixed['id'],
        ).first()
        if item and item.quantity - item.is_returned > 0 \
                and item.is_returned + return_number <= item.quantity:
            item.is_returned += return_number
            provide_update_list.append(item)
            # nếu số lượng trả về khới thì mới add vào danh sách update provide_update_list
            product_fixed_list.append(prod_fixed_obj)
            return_info_list.append(
                {
                    'product': prod_fixed,
                    'product_remark': prod.product_remark,
                    'return_number': return_number,
                    'reason': self.remark
                }
            )

    def _prod_type_tool(
            self,
            prod,
            employee_asset_list,
            return_number,
            provide_update_list,
            return_info_list,
            product_instrument_list
    ):
        tool_obj = prod.prod_in_tools
        item = employee_asset_list.filter(
            prod_in_tools_id=tool_obj.id,
            prod_in_fixed__isnull=True
        ).first()
        # số trả cộng số đã trả phải nhỏ hơn or = tổng số cấp
        # số ccdc đã cấp phải lớn hơn or = số return
        if item and item.is_returned + return_number <= item.quantity \
                and tool_obj.allocated_quantity >= return_number:
            item.is_returned += return_number
            provide_update_list.append(item)

            tool_obj.allocated_quantity -= return_number
            if tool_obj.allocated_quantity == 0:
                tool_obj.status = 0
            product_instrument_list.append(tool_obj)
            return_info_list.append(
                {
                    'product': {
                        'id': str(tool_obj.id),
                        'title': tool_obj.title,
                        'code': tool_obj.code
                    },
                    'product_remark': prod.product_remark,
                    'return_number': return_number,
                    'reason': self.remark
                }
            )
        else:
            raise ValueError(AssetToolsMsg.RETURN_PRODUCT_ERROR01)

    def update_prod_provide(self, prod_list, return_info_list):
        product_instrument_list = []
        product_fixed_list = []
        provide_update_list = []
        models_provide_map = DisperseModel(app_model='assettools.AssetToolsProvideProduct').get_model()
        employee_asset_list = models_provide_map.objects.filter_on_company(employee_inherit_id=self.employee_inherit_id)
        models_instrument = DisperseModel(app_model='asset.InstrumentTool').get_model()
        models_fixed = DisperseModel(app_model='asset.FixedAsset').get_model()

        for prod in prod_list:
            return_number = prod.return_number
            prod_type = 'tool' if prod.prod_in_tools else 'fixed' if prod.prod_in_fixed else 'new'

            if prod_type == 'new':
                self._prod_type_new(prod, employee_asset_list, return_number, provide_update_list, return_info_list)

            elif prod_type == 'fixed':
                self._prod_type_fixed(
                    prod, models_fixed, employee_asset_list, return_number, provide_update_list,
                    return_info_list, product_fixed_list
                )
            else:
                self._prod_type_tool(
                    prod, employee_asset_list, return_number, provide_update_list,
                    return_info_list, product_instrument_list
                )

        if product_instrument_list:
            models_instrument.objects.bulk_update(product_instrument_list, fields=['allocated_quantity', 'status'])
        if product_fixed_list:
            models_fixed.objects.bulk_update(product_fixed_list, fields=['status'])
        models_provide_map.objects.bulk_update(provide_update_list, fields=['is_returned'])

    def return_product_used(self):
        return_info_list = []
        try:
            with transaction.atomic():
                if self.system_status != 3:
                    return True, return_info_list

                all_prod_list = self.asset_return_map_product.all().select_related('prod_in_tools')

                self.update_prod_provide(all_prod_list, return_info_list)

                # Ghi nhận danh sách trả và cập nhật lại số lượng công cụ
                if return_info_list:
                    self.return_info_list = return_info_list

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
            done_update, log_list = self.return_product_used()
            update_files_is_approved(
                AssetToolsReturnAttachmentFile.objects.filter(
                    asset_tools_return=self, attachment__is_approved=False
                ),
                self
            )
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
                    if 'date_approved' in kwargs['update_fields']:
                        CompanyFunctionNumber.auto_gen_code_based_on_config('assettoolsreturn', True, self, kwargs)
                if done_update and log_list:
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
    prod_in_fixed = models.JSONField(
        default=dict,
        verbose_name='Fixed asset map with return request',
        null=True,
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': ''}
            ]
        )
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
