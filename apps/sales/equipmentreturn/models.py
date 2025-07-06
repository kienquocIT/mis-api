from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import WareHouse
from apps.sales.inventory.models import GoodsTransfer, GoodsTransferProduct
from apps.sales.report.utils import IRForGoodsTransferHandler
from apps.shared import SimpleAbstractModel, DataAbstractModel


class EquipmentReturn(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'f5954e02-6ad1-4ebf-a4f2-0b598820f5f0'

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'ER-[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Equipment Return'
        verbose_name_plural = 'Equipments Return'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class EquipmentReturnItem(SimpleAbstractModel):
    equipment_return = models.ForeignKey(
        EquipmentReturn, on_delete=models.CASCADE, related_name='equipment_return_items'
    )
    order = models.IntegerField(default=1)
    return_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    return_product_data = models.JSONField(default=dict)
    return_quantity = models.FloatField()

    class Meta:
        verbose_name = 'Equipment Return Item'
        verbose_name_plural = 'Equipment Return Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class EquipmentReturnItemDetail(SimpleAbstractModel):
    equipment_return_item = models.ForeignKey(
        EquipmentReturnItem, on_delete=models.CASCADE, related_name='equipment_return_item_detail', null=True
    )

    return_product_pw = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    return_product_pw_quantity = models.FloatField(default=0)

    return_product_pw_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    return_product_pw_lot_data = models.JSONField(default=dict)
    return_product_pw_lot_quantity = models.FloatField(default=0)

    return_product_pw_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    return_product_pw_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Equipment Return Item Detail'
        verbose_name_plural = 'Equipment Return Items Detail'
        default_permissions = ()
        permissions = ()


class EquipmentReturnAttachmentFile(M2MFilesAbstractModel):
    equipment_return = models.ForeignKey(
        EquipmentReturn, on_delete=models.CASCADE, related_name='equipment_return_attachments'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'equipment_return'

    class Meta:
        verbose_name = 'Equipment Return attachment'
        verbose_name_plural = 'Equipment Return attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
