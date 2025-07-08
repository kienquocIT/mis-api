from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel


class EquipmentReturn(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'f5954e02-6ad1-4ebf-a4f2-0b598820f5f0'

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('equipmentreturn', True, self, kwargs)
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
    return_quantity = models.FloatField(default=0)

    return_to_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)
    return_to_warehouse_data = models.JSONField(default=dict)

    loan_item_mapped = models.ForeignKey('equipmentloan.EquipmentLoanItem', on_delete=models.SET_NULL, null=True)

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

    return_product_pw_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    return_product_pw_lot_data = models.JSONField(default=dict)
    return_product_pw_lot_quantity = models.FloatField(default=0)

    return_product_pw_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    return_product_pw_serial_data = models.JSONField(default=dict)

    loan_item_detail_mapped = models.ForeignKey(
        'equipmentloan.EquipmentLoanItemDetail', on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = 'Equipment Return Item Detail'
        verbose_name_plural = 'Equipment Return Items Detail'
        default_permissions = ()
        permissions = ()


class EquipmentLoanAttachmentFile(M2MFilesAbstractModel):
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
