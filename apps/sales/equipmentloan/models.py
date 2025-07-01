from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import SimpleAbstractModel, DataAbstractModel


class EquipmentLoan(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)
    loan_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'EL-[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Equipment Loan'
        verbose_name_plural = 'Equipments Loan'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class EquipmentLoanItem(SimpleAbstractModel):
    equipment_loan = models.ForeignKey(
        EquipmentLoan, on_delete=models.CASCADE, related_name='equipment_loan_items'
    )
    order = models.IntegerField(default=1)
    loan_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    loan_product_data = models.JSONField(default=dict)
    loan_quantity = models.FloatField()

    class Meta:
        verbose_name = 'Equipment Loan Item'
        verbose_name_plural = 'Equipment Loan Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class EquipmentLoanItemDetail(SimpleAbstractModel):
    equipment_loan_item = models.ForeignKey(
        EquipmentLoanItem, on_delete=models.CASCADE, related_name='equipment_loan_item_detail', null=True
    )

    loan_product_pw = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    loan_product_pw_quantity = models.FloatField(default=0)

    loan_product_pw_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    loan_product_pw_lot_data = models.JSONField(default=dict)
    loan_product_pw_lot_quantity = models.FloatField(default=0)

    loan_product_pw_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    loan_product_pw_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Equipment Loan Item Detail'
        verbose_name_plural = 'Equipment Loan Items Detail'
        default_permissions = ()
        permissions = ()


class EquipmentLoanAttachmentFile(M2MFilesAbstractModel):
    equipment_loan = models.ForeignKey(
        EquipmentLoan, on_delete=models.CASCADE, related_name='equipment_loan_attachments'
    )

    class Meta:
        verbose_name = 'Equipment Loan attachment'
        verbose_name_plural = 'Equipment Loan attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
