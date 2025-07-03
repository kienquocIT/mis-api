from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import WareHouse
from apps.sales.inventory.models import GoodsTransfer, GoodsTransferProduct
from apps.sales.report.utils import IRForGoodsTransferHandler
from apps.shared import SimpleAbstractModel, DataAbstractModel


class EquipmentLoan(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)
    loan_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)

    @classmethod
    def auto_create_goods_transfer_doc(cls, el_obj):
        """
        Phiếu Điều chuyển được tạo từ chức năng này sẽ tự động duyệt mà không quan tâm quy trình như thế nào
        """
        gtf_data = {
            'title': f'Goods transfer for {el_obj.code}',
            'goods_transfer_type': 2,
            'equipment_loan': el_obj,
            'system_auto_create': True,
            'tenant': el_obj.tenant,
            'company': el_obj.company,
            'employee_created': el_obj.employee_created,
            'employee_inherit': el_obj.employee_inherit,
            'date_transfer': el_obj.date_created,
            'date_created': el_obj.date_created,
            'date_approved': el_obj.date_approved,
        }
        gtf_obj = GoodsTransfer.objects.create(**gtf_data)
        end_warehouse = WareHouse.objects.filter_on_company(use_for=1).first()
        bulk_info = []
        for item in el_obj.equipment_loan_items.all():
            for child in item.equipment_loan_item_detail.all():
                if child.loan_product_pw:  # none
                    product_warehouse = child.loan_product_pw
                    warehouse = product_warehouse.warehouse
                    product = product_warehouse.product
                    quantity = child.loan_product_pw_quantity
                    uom = product.general_uom_group.uom_reference if product.general_uom_group else None
                    unit_cost = product.get_cost_info_by_warehouse(
                        warehouse_id=warehouse.id if warehouse else None,
                        get_type=1,
                    )
                    bulk_info.append(GoodsTransferProduct(
                        goods_transfer=gtf_obj,
                        product_warehouse=product_warehouse,
                        warehouse=warehouse,
                        product=product,
                        sale_order=None,
                        end_warehouse=end_warehouse,
                        uom=uom,
                        lot_data=[],
                        sn_data=[],
                        quantity=quantity,
                        unit_cost=unit_cost,
                        subtotal=quantity * unit_cost,
                    ))
                elif child.loan_product_pw_lot:  # lot
                    product_warehouse = child.loan_product_pw_lot.product_warehouse
                    warehouse = product_warehouse.warehouse
                    product = product_warehouse.product
                    quantity = child.loan_product_pw_lot_quantity
                    uom = product.general_uom_group.uom_reference if product.general_uom_group else None
                    unit_cost = product.get_cost_info_by_warehouse(
                        warehouse_id=warehouse.id if warehouse else None,
                        get_type=1,
                    )
                    bulk_info.append(GoodsTransferProduct(
                        goods_transfer=gtf_obj,
                        product_warehouse=product_warehouse,
                        warehouse=warehouse,
                        product=product,
                        sale_order=None,
                        end_warehouse=end_warehouse,
                        uom=uom,
                        lot_data=[{
                            'lot_id': str(child.loan_product_pw_lot_id),
                            'quantity': child.loan_product_pw_lot_quantity
                        }],
                        sn_data=[],
                        quantity=quantity,
                        unit_cost=unit_cost,
                        subtotal=quantity * unit_cost,
                    ))
                elif child.loan_product_pw_serial:  # sn
                    product_warehouse = child.loan_product_pw_serial.product_warehouse
                    warehouse = product_warehouse.warehouse
                    product = product_warehouse.product
                    quantity = 1
                    uom = product.general_uom_group.uom_reference if product.general_uom_group else None
                    unit_cost = product.get_cost_info_by_warehouse(
                        warehouse_id=warehouse.id if warehouse else None,
                        get_type=1,
                    )
                    bulk_info.append(GoodsTransferProduct(
                        goods_transfer=gtf_obj,
                        product_warehouse=product_warehouse,
                        warehouse=warehouse,
                        product=product,
                        sale_order=None,
                        end_warehouse=end_warehouse,
                        uom=uom,
                        lot_data=[],
                        sn_data=[str(child.loan_product_pw_serial_id)],
                        quantity=quantity,
                        unit_cost=unit_cost,
                        subtotal=quantity * unit_cost,
                    ))
        GoodsTransferProduct.objects.filter(goods_transfer=gtf_obj).delete()
        GoodsTransferProduct.objects.bulk_create(bulk_info)

        # duyệt tự động
        gtf_obj.add_auto_generate_code_to_instance(gtf_obj, 'GT[n4]', True)
        gtf_obj.system_status = 3
        gtf_obj.save(update_fields=['code', 'system_status'])
        # action sau khi duyệt
        gtf_obj.update_data_warehouse(gtf_obj)
        IRForGoodsTransferHandler.push_to_inventory_report(gtf_obj)

        return gtf_obj

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'EL-[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

            if self.system_status == 3:
                self.auto_create_goods_transfer_doc(self)
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
