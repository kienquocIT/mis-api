from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import WareHouse
from apps.sales.inventory.models import GoodsTransfer, GoodsTransferProduct
from apps.sales.report.utils import IRForGoodsTransferHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel


class EquipmentReturn(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'f5954e02-6ad1-4ebf-a4f2-0b598820f5f0'

    @staticmethod
    def update_none_item_list(data_bulk_info, item, gtf_obj, product_warehouse, end_warehouse):
        """
        Hàm kiểm tra none này đã thêm vào danh sách trước đó hay chưa.
        Nếu có thì update item cũ, chưa thì thêm mới
        """
        source_warehouse = product_warehouse.warehouse
        product = product_warehouse.product
        quantity = item.return_quantity
        uom = product.general_uom_group.uom_reference if product.general_uom_group else None
        unit_cost = product.get_cost_info_by_warehouse(
            warehouse_id=source_warehouse.id if source_warehouse else None,
            get_type=1,
        )
        for sub in data_bulk_info:
            if all([
                sub.get('product_warehouse') is not None,
                sub.get('warehouse') is not None,
                sub.get('product') is not None,
                product_warehouse is not None,
                source_warehouse is not None,
                product is not None
            ]):
                if all([
                    str(sub['product_warehouse'].id) == str(product_warehouse.id),
                    str(sub['warehouse'].id) == str(source_warehouse.id),
                    str(sub['product'].id) == str(product.id)
                ]):
                    sub['quantity'] += quantity
                    sub['subtotal'] += quantity * unit_cost
                    return data_bulk_info
        data_bulk_info.append({
            'goods_transfer': gtf_obj,
            'product_warehouse': product_warehouse,
            'warehouse': source_warehouse,
            'product': product,
            'end_warehouse': end_warehouse,
            'uom': uom,
            'lot_data': [],
            'sn_data': [],
            'quantity': quantity,
            'unit_cost': unit_cost,
            'subtotal': quantity * unit_cost,
        })
        return data_bulk_info

    @staticmethod
    def update_lot_item_list(data_bulk_info, child, gtf_obj, product_warehouse, end_warehouse):
        """
        Hàm kiểm tra lot này đã thêm vào danh sách trước đó hay chưa.
        Nếu có thì update item cũ, chưa thì thêm mới
        """
        warehouse = product_warehouse.warehouse
        product = product_warehouse.product
        quantity = child.return_product_pw_lot_quantity
        uom = product.general_uom_group.uom_reference if product.general_uom_group else None
        unit_cost = product.get_cost_info_by_warehouse(
            warehouse_id=warehouse.id if warehouse else None,
            get_type=1,
        )
        for sub in data_bulk_info:
            if all([
                sub.get('product_warehouse') is not None,
                sub.get('warehouse') is not None,
                sub.get('product') is not None,
                product_warehouse is not None,
                warehouse is not None,
                product is not None
            ]):
                if all([
                    str(sub['product_warehouse'].id) == str(product_warehouse.id),
                    str(sub['warehouse'].id) == str(warehouse.id),
                    str(sub['product'].id) == str(product.id)
                ]):
                    sub['lot_data'] += [{
                        'lot_id': str(child.return_product_pw_lot_id),
                        'quantity': quantity
                    }]
                    sub['quantity'] += quantity
                    sub['subtotal'] += quantity * unit_cost
                    return data_bulk_info
        data_bulk_info.append({
            'goods_transfer': gtf_obj,
            'product_warehouse': product_warehouse,
            'warehouse': warehouse,
            'product': product,
            'end_warehouse': end_warehouse,
            'uom': uom,
            'lot_data': [{
                'lot_id': str(child.return_product_pw_lot_id),
                'quantity': quantity
            }],
            'sn_data': [],
            'quantity': quantity,
            'unit_cost': unit_cost,
            'subtotal': quantity * unit_cost,
        })
        return data_bulk_info

    @staticmethod
    def update_serial_item_list(data_bulk_info, child, gtf_obj, product_warehouse, end_warehouse):
        """
        Hàm kiểm tra serial này đã thêm vào danh sách trước đó hay chưa.
        Nếu có thì update item cũ, chưa thì thêm mới
        """
        warehouse = product_warehouse.warehouse
        product = product_warehouse.product
        quantity = 1
        uom = product.general_uom_group.uom_reference if product.general_uom_group else None
        unit_cost = product.get_cost_info_by_warehouse(
            warehouse_id=warehouse.id if warehouse else None,
            get_type=1,
        )
        for sub in data_bulk_info:
            if all([
                sub.get('product_warehouse') is not None,
                sub.get('warehouse') is not None,
                sub.get('product') is not None,
                product_warehouse is not None,
                warehouse is not None,
                product is not None
            ]):
                if all([
                    str(sub['product_warehouse'].id) == str(product_warehouse.id),
                    str(sub['warehouse'].id) == str(warehouse.id),
                    str(sub['product'].id) == str(product.id)
                ]):
                    sub['sn_data'] += [str(child.return_product_pw_serial_id)]
                    sub['quantity'] += 1
                    sub['subtotal'] += quantity * unit_cost
                    return data_bulk_info
        data_bulk_info.append({
            'goods_transfer': gtf_obj,
            'product_warehouse': product_warehouse,
            'warehouse': warehouse,
            'product': product,
            'end_warehouse': end_warehouse,
            'uom': uom,
            'lot_data': [],
            'sn_data': [str(child.return_product_pw_serial_id)],
            'quantity': quantity,
            'unit_cost': unit_cost,
            'subtotal': quantity * unit_cost,
        })
        return data_bulk_info

    @classmethod
    def auto_create_goods_transfer_doc(cls, er_obj):
        """
        Phiếu Điều chuyển được tạo từ chức năng này sẽ tự động duyệt mà không quan tâm quy trình như thế nào
        """
        gtf_data = {
            'title': f'Goods transfer for {er_obj.code}',
            'goods_transfer_type': 3,
            'equipment_return': er_obj,
            'system_auto_create': True,
            'tenant': er_obj.tenant,
            'company': er_obj.company,
            'employee_created': er_obj.employee_created,
            'employee_inherit': er_obj.employee_inherit,
            'date_transfer': er_obj.date_created,
            'date_created': er_obj.date_created,
            'date_approved': er_obj.date_approved,
        }
        gtf_obj = GoodsTransfer.objects.create(**gtf_data)
        source_warehouse = WareHouse.objects.filter_on_company(use_for=1).first()
        data_bulk_info = []
        for item in er_obj.equipment_return_items.all():
            end_warehouse = item.return_to_warehouse
            product_warehouse = item.return_product.product_warehouse_product.filter(warehouse=source_warehouse).first()
            if item.return_product.general_traceability_method == 0:
                data_bulk_info = cls.update_none_item_list(
                    data_bulk_info,
                    item,
                    gtf_obj,
                    product_warehouse,
                    end_warehouse
                )
            for child in item.equipment_return_item_detail.all():
                if child.return_product_pw_lot:  # lot
                    data_bulk_info = cls.update_lot_item_list(
                        data_bulk_info,
                        child,
                        gtf_obj,
                        product_warehouse,
                        end_warehouse
                    )
                elif child.return_product_pw_serial:  # sn
                    data_bulk_info = cls.update_serial_item_list(
                        data_bulk_info,
                        child,
                        gtf_obj,
                        product_warehouse,
                        end_warehouse
                    )
        bulk_info = []
        for item in data_bulk_info:
            bulk_info.append(GoodsTransferProduct(**item))
        GoodsTransferProduct.objects.filter(goods_transfer=gtf_obj).delete()
        GoodsTransferProduct.objects.bulk_create(bulk_info)

        # duyệt tự động
        CompanyFunctionNumber.auto_gen_code_based_on_config('goodstransfer', True, gtf_obj)
        gtf_obj.system_status = 3
        gtf_obj.save(update_fields=['code', 'system_status'])
        # action sau khi duyệt
        gtf_obj.update_data_warehouse(gtf_obj)
        IRForGoodsTransferHandler.push_to_inventory_report(gtf_obj)

        return gtf_obj

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('equipmentreturn', True, self, kwargs)
                    self.auto_create_goods_transfer_doc(self)
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
