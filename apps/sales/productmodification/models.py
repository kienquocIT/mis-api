from django.db import models, transaction
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import Product, ProductProductType, ProductSpecificIdentificationSerialNumber, \
    ProductWareHouse, ProductWareHouseSerial
from apps.masterdata.saledata.models.product_warehouse import PWModified, PWModifiedComponent, \
    PWModifiedComponentDetail, ProductWareHouseLot
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct
from apps.sales.inventory.utils import GRFromPMHandler
from apps.sales.report.utils import IRForGoodsIssueHandler
from apps.shared import SimpleAbstractModel, DataAbstractModel, DisperseModel


class ProductModification(DataAbstractModel):
    product_modified = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, related_name='product_modified')
    new_description = models.TextField(null=True, blank=True)

    prd_wh = models.ForeignKey('saledata.ProductWareHouse', on_delete=models.CASCADE, null=True)
    prd_wh_data = models.JSONField(default=dict)

    prd_wh_lot = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True)
    prd_wh_lot_data = models.JSONField(default=dict)

    prd_wh_serial = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True)
    prd_wh_serial_data = models.JSONField(default=dict)

    created_goods_receipt = models.BooleanField(default=False)
    created_goods_issue_for_root = models.BooleanField(default=False)

    representative_product_modified = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_representative_product_modified',
        null=True
    )

    @classmethod
    def get_product_modified_data(cls, pm_obj):
        product_modified_data = []
        try:
            uom = pm_obj.product_modified.general_uom_group.uom_reference
        except AttributeError:
            uom = None
        if pm_obj.product_modified.general_traceability_method == 0:
            product_modified_data.append({
                'product_modification_item': None,
                'product': pm_obj.prd_wh.product if pm_obj.prd_wh else None,
                'product_data': pm_obj.prd_wh_data.get('product', {}) if pm_obj.prd_wh_data else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [],
                'sn_data': []
            })
        if pm_obj.product_modified.general_traceability_method == 1:
            product_modified_data.append({
                'product_modification_item': None,
                'product': pm_obj.prd_wh.product if pm_obj.prd_wh else None,
                'product_data': pm_obj.prd_wh_data.get('product', {}) if pm_obj.prd_wh_data else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [{
                    'lot_id': str(pm_obj.prd_wh_lot_id),
                    'old_quantity': pm_obj.prd_wh_lot.quantity_import,
                    'quantity': 1
                }],
                'sn_data': []
            })
        if pm_obj.product_modified.general_traceability_method == 2:
            product_modified_data.append({
                'product_modification_item': None,
                'product': pm_obj.prd_wh.product if pm_obj.prd_wh else None,
                'product_data': pm_obj.prd_wh_data.get('product', {}) if pm_obj.prd_wh_data else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [],
                'sn_data': [str(pm_obj.prd_wh_serial_id)]
            })
        return product_modified_data

    @classmethod
    def get_representative_product_data(cls, pm_obj, re_prd_wh_obj, re_prd_wh_serial_obj, re_prd_wh_lot_obj):
        representative_product_modified_data = []
        try:
            uom = pm_obj.representative_product_modified.general_uom_group.uom_reference
        except AttributeError:
            uom = None
        if pm_obj.representative_product_modified.general_traceability_method == 0:
            representative_product_modified_data.append({
                'product_modification_item': None,
                'product': re_prd_wh_obj.product if re_prd_wh_obj else None,
                'product_data': {
                    'id': str(re_prd_wh_obj.product_id),
                    'code': re_prd_wh_obj.product.code,
                    'title': re_prd_wh_obj.product.title,
                    'description': re_prd_wh_obj.product.description,
                    'general_traceability_method': re_prd_wh_obj.product.general_traceability_method,
                    'valuation_method': re_prd_wh_obj.product.valuation_method,
                } if re_prd_wh_obj.product else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [],
                'sn_data': []
            })
        if pm_obj.representative_product_modified.general_traceability_method == 1:
            representative_product_modified_data.append({
                'product_modification_item': None,
                'product': re_prd_wh_obj.product if re_prd_wh_obj else None,
                'product_data': {
                    'id': str(re_prd_wh_obj.product_id),
                    'code': re_prd_wh_obj.product.code,
                    'title': re_prd_wh_obj.product.title,
                    'description': re_prd_wh_obj.product.description,
                    'general_traceability_method': re_prd_wh_obj.product.general_traceability_method,
                    'valuation_method': re_prd_wh_obj.product.valuation_method,
                } if re_prd_wh_obj.product else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [{
                    'lot_id': str(re_prd_wh_lot_obj.id),
                    'old_quantity': re_prd_wh_lot_obj.quantity_import,
                    'quantity': 1
                }],
                'sn_data': []
            })
        if pm_obj.representative_product_modified.general_traceability_method == 2:
            representative_product_modified_data.append({
                'product_modification_item': None,
                'product': re_prd_wh_obj.product if re_prd_wh_obj else None,
                'product_data': {
                    'id': str(re_prd_wh_obj.product_id),
                    'code': re_prd_wh_obj.product.code,
                    'title': re_prd_wh_obj.product.title,
                    'description': re_prd_wh_obj.product.description,
                    'general_traceability_method': re_prd_wh_obj.product.general_traceability_method,
                    'valuation_method': re_prd_wh_obj.product.valuation_method,
                } if re_prd_wh_obj.product else {},
                'warehouse': pm_obj.prd_wh.warehouse if pm_obj.prd_wh else None,
                'warehouse_data': pm_obj.prd_wh_data.get('warehouse', {}) if pm_obj.prd_wh_data else {},
                'uom': uom,
                'uom_data': {
                    'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                } if uom else {},
                'before_quantity': 1,
                'remain_quantity': 1,
                'issued_quantity': 1,
                'lot_data': [],
                'sn_data': [str(re_prd_wh_serial_obj.id)]
            })
        return representative_product_modified_data

    @classmethod
    def get_component_data(cls, pm_obj):
        component_data = []
        for item in pm_obj.current_components.all():
            try:
                uom = item.component_product.general_uom_group.uom_reference
            except AttributeError:
                uom = None
            for child in item.current_components_detail.all():
                if child.component_prd_wh:
                    try:
                        warehouse = child.component_prd_wh.warehouse
                    except AttributeError:
                        warehouse = None
                    component_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': child.component_prd_wh_quantity,
                        'remain_quantity': child.component_prd_wh_quantity,
                        'issued_quantity': child.component_prd_wh_quantity,
                        'lot_data': [],
                        'sn_data': []
                    })
                if child.component_prd_wh_lot:
                    try:
                        warehouse = child.component_prd_wh_lot.product_warehouse.warehouse
                    except AttributeError:
                        warehouse = None
                    component_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': child.component_prd_wh_lot_quantity,
                        'remain_quantity': child.component_prd_wh_lot_quantity,
                        'issued_quantity': child.component_prd_wh_lot_quantity,
                        'lot_data': [{
                            'lot_id': str(child.component_prd_wh_lot_id),
                            'old_quantity': child.component_prd_wh_lot.quantity_import,
                            'quantity': child.component_prd_wh_lot_quantity
                        }],
                        'sn_data': []
                    })
                if child.component_prd_wh_serial:
                    try:
                        warehouse = child.component_prd_wh_serial.product_warehouse.warehouse
                    except AttributeError:
                        warehouse = None
                    component_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': 1,
                        'remain_quantity': 1,
                        'issued_quantity': 1,
                        'lot_data': [],
                        'sn_data': [str(child.component_prd_wh_serial_id)]
                    })
        return component_data

    @classmethod
    def auto_create_goods_issue(cls, pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_serial_obj, re_prd_prd_wh_lot_obj):
        """
        Phiếu Xuất kho được tạo từ chức năng này sẽ tự động duyệt mà không quan tâm quy trình như thế nào
        """
        gis_data = {
            'title': f'Goods issue for {pm_obj.code}',
            'goods_issue_type': 3,
            'product_modification': pm_obj,
            'system_auto_create': True,
            'tenant': pm_obj.tenant,
            'company': pm_obj.company,
            'employee_created': pm_obj.employee_created,
            'employee_inherit': pm_obj.employee_inherit,
            'date_created': pm_obj.date_created,
            'date_approved': pm_obj.date_approved,
        }
        gis_obj = GoodsIssue.objects.create(**gis_data)
        bulk_info = []
        detail_data = (
            cls.get_product_modified_data(pm_obj) +
            cls.get_representative_product_data(
                pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj,
            ) +
            cls.get_component_data(pm_obj)
        )
        for item in detail_data:
            bulk_info.append(GoodsIssueProduct(goods_issue=gis_obj, **item))
        GoodsIssueProduct.objects.filter(goods_issue=gis_obj).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_info)

        # duyệt tự động
        CompanyFunctionNumber.auto_gen_code_based_on_config('goodsissue', True, gis_obj)
        gis_obj.system_status = 3
        gis_obj.save(update_fields=['code', 'system_status'])
        # action sau khi duyệt
        gis_obj.update_related_app_after_issue(gis_obj)
        new_logs = IRForGoodsIssueHandler.push_to_inventory_report(gis_obj)

        return {'gis_obj': gis_obj, 'new_logs': new_logs}

    @classmethod
    def create_remove_component_product_mapped(cls, pm_obj):
        for item in pm_obj.removed_components.all():
            mapped_type = item.product_mapped_data.pop('type')
            if mapped_type == 'new':
                if not item.product_mapped_data.get('code'):
                    item.product_mapped_data['code'] = CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code='product'
                    )
                product_type = item.product_mapped_data.pop('product_type')
                general_product_category = item.product_mapped_data.get('general_product_category')
                general_uom_group = item.product_mapped_data.get('general_uom_group')
                general_traceability_method = item.product_mapped_data.get('general_traceability_method')
                inventory_uom = item.product_mapped_data.get('inventory_uom')
                valuation_method = item.product_mapped_data.get('valuation_method')
                prd_created_obj = Product.objects.create(
                    code=item.product_mapped_data.get('code'),
                    title=item.product_mapped_data.get('title'),
                    description=item.product_mapped_data.get('description'),
                    product_choice=[1],
                    general_product_category_id=general_product_category,
                    general_uom_group_id=general_uom_group,
                    general_traceability_method=general_traceability_method,
                    inventory_uom_id=inventory_uom,
                    valuation_method=valuation_method,
                    tenant=pm_obj.tenant,
                    company=pm_obj.company,
                    employee_created=pm_obj.employee_created,
                    employee_inherit=pm_obj.employee_created,  # người thụ hưởng là người tạo phiếu luôn
                )
                CompanyFunctionNumber.auto_code_update_latest_number(app_code='product')
                item.component_product_id = str(prd_created_obj.id)
                item.fair_value = item.product_mapped_data.get('fair_value', 0)
                item.is_mapped = True
                ProductProductType.objects.create(product=prd_created_obj, product_type_id=product_type)
                prd_obj = Product.objects.filter_on_company(id=item.product_mapped_data.get('product_mapped')).first()
                item.component_product_data = {
                    'id': str(prd_obj.id),
                    'code': prd_obj.code,
                    'title': prd_obj.title,
                    'description': prd_obj.description,
                    'general_traceability_method': prd_obj.general_traceability_method,
                } if prd_obj else {}
            if mapped_type == 'map':
                item.component_product_id = item.product_mapped_data.get('product_mapped')
                item.fair_value = item.product_mapped_data.get('fair_value', 0)
                item.is_mapped = True
                prd_obj = Product.objects.filter_on_company(id=item.product_mapped_data.get('product_mapped')).first()
                item.component_product_data = {
                    'id': str(prd_obj.id),
                    'code': prd_obj.code,
                    'title': prd_obj.title,
                    'description': prd_obj.description,
                    'general_traceability_method': prd_obj.general_traceability_method,
                } if prd_obj else {}
            item.save(update_fields=['component_product_id', 'component_product_data', 'fair_value', 'is_mapped'])
        return True

    @classmethod
    def update_current_product_component(
            cls, pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
    ):
        """
        Hàm này để cập nhập các component hiện tại cho SP đã đem đi Ráp - Rã.
        """
        if pm_obj.representative_product_modified:
            prd_wh = re_prd_prd_wh_obj
            prd_wh_lot = re_prd_prd_wh_lot_obj
            prd_wh_serial = re_prd_prd_wh_serial_obj
        else:
            prd_wh = pm_obj.prd_wh
            prd_wh_lot = pm_obj.prd_wh_lot
            prd_wh_serial = pm_obj.prd_wh_serial
        PWModified.objects.filter_on_company(
            product_warehouse=prd_wh,
            product_warehouse_lot=prd_wh_lot,
            product_warehouse_serial=prd_wh_serial,
        ).delete()
        pw_modified_obj = PWModified.objects.create(
            product_warehouse=prd_wh,
            product_warehouse_lot=prd_wh_lot,
            product_warehouse_serial=prd_wh_serial,
            modified_number=pm_obj.code,
            new_description=pm_obj.new_description,
            employee_created=pm_obj.employee_created,
            date_created=pm_obj.date_created,
            tenant=pm_obj.tenant,
            company=pm_obj.company,
        )
        bulk_info = []
        bulk_info_detail = []
        for order, item in enumerate(pm_obj.current_components.all()):
            pw_modified_component = PWModifiedComponent(
                pw_modified=pw_modified_obj,
                order=order,
                component_text_data=item.component_text_data,
                component_product=item.component_product,
                component_product_data=item.component_product_data,
                component_quantity=item.component_quantity
            )
            bulk_info.append(pw_modified_component)
            for detail_item in item.current_components_detail.all():
                bulk_info_detail.append(
                    PWModifiedComponentDetail(
                        pw_modified_component=pw_modified_component,
                        component_prd_wh=detail_item.component_prd_wh,
                        component_prd_wh_quantity=detail_item.component_prd_wh_quantity,
                        component_prd_wh_lot=detail_item.component_prd_wh_lot,
                        component_prd_wh_lot_data=detail_item.component_prd_wh_lot_data,
                        component_prd_wh_lot_quantity=detail_item.component_prd_wh_lot_quantity,
                        component_prd_wh_serial=detail_item.component_prd_wh_serial,
                        component_prd_wh_serial_data=detail_item.component_prd_wh_serial_data,
                    )
                )
        PWModifiedComponent.objects.filter(pw_modified=pw_modified_obj).delete()
        PWModifiedComponent.objects.bulk_create(bulk_info)
        PWModifiedComponentDetail.objects.bulk_create(bulk_info_detail)
        return True

    @classmethod
    def auto_clone_for_representative_product(cls, pm_obj):
        re_prd_prd_wh_obj = None
        re_prd_prd_wh_lot_obj = None
        re_prd_prd_wh_serial_obj = None
        if pm_obj.representative_product_modified:
            re_prd_prd_wh_obj = ProductWareHouse.objects.filter(
                product=pm_obj.representative_product_modified,
                warehouse=pm_obj.prd_wh.warehouse
            ).first()
            if re_prd_prd_wh_obj:
                re_prd_prd_wh_obj.receipt_amount += 1
                re_prd_prd_wh_obj.stock_amount += 1
                re_prd_prd_wh_obj.save(update_fields=['receipt_amount', 'stock_amount'])
            else:
                re_prd_prd_wh_obj = ProductWareHouse.objects.create(
                    tenant=pm_obj.prd_wh.tenant,
                    company=pm_obj.prd_wh.company,
                    product=pm_obj.representative_product_modified,
                    uom=pm_obj.prd_wh.uom,
                    warehouse=pm_obj.prd_wh.warehouse,
                    tax=pm_obj.prd_wh.tax,
                    unit_price=pm_obj.prd_wh.unit_price,
                    stock_amount=1,
                    receipt_amount=1,
                    sold_amount=0,
                    picked_ready=0,
                    product_data=pm_obj.prd_wh.product_data,
                    warehouse_data=pm_obj.prd_wh.warehouse_data,
                    uom_data=pm_obj.prd_wh.uom_data,
                    tax_data=pm_obj.prd_wh.tax_data
                )
        if all([
            re_prd_prd_wh_obj,
            pm_obj.representative_product_modified.general_traceability_method == 1,
            pm_obj.prd_wh_lot
        ]):
            re_prd_prd_wh_lot_obj = ProductWareHouseLot.objects.create(
                tenant=pm_obj.prd_wh.tenant,
                company=pm_obj.prd_wh.company,
                product_warehouse=re_prd_prd_wh_obj,
                lot_number=pm_obj.prd_wh_lot.lot_number,
                quantity_import=1,
                expire_date=pm_obj.prd_wh_lot.expire_date,
                manufacture_date=pm_obj.prd_wh_lot.manufacture_date
            )
        if all([
            re_prd_prd_wh_obj,
            pm_obj.representative_product_modified.general_traceability_method == 2,
            pm_obj.prd_wh_serial
        ]):
            re_prd_prd_wh_serial_obj = ProductWareHouseSerial.objects.create(
                tenant=pm_obj.prd_wh.tenant,
                company=pm_obj.prd_wh.company,
                product_warehouse=re_prd_prd_wh_obj,
                vendor_serial_number=pm_obj.prd_wh_serial.vendor_serial_number,
                serial_number=pm_obj.prd_wh_serial.serial_number,
                expire_date=pm_obj.prd_wh_serial.expire_date,
                manufacture_date=pm_obj.prd_wh_serial.manufacture_date,
                warranty_start=pm_obj.prd_wh_serial.warranty_start,
                warranty_end=pm_obj.prd_wh_serial.warranty_end
            )
        return re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj

    @classmethod
    def setup_representative_product(cls, pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj):
        gr_products_data = []
        representative_product_obj = pm_obj.representative_product_modified
        if representative_product_obj:
            uom_obj = representative_product_obj.inventory_uom
            gr_products_data.append({
                'order': 1,
                'product_modification_product_id': None,
                'product_id': str(representative_product_obj.id),
                'product_data': {
                    'id': str(representative_product_obj.id),
                    'title': representative_product_obj.title,
                    'code': representative_product_obj.code,
                    'general_traceability_method': representative_product_obj.general_traceability_method,
                    'description': representative_product_obj.description,
                    'product_choice': representative_product_obj.product_choice,
                },
                'uom_id': str(uom_obj.id) if uom_obj else None,
                'uom_data': {
                    'id': str(uom_obj.id),
                    'title': uom_obj.title,
                    'code': uom_obj.code,
                    'uom_group': {
                        'id': str(uom_obj.group_id),
                        'title': uom_obj.group.title,
                        'code': uom_obj.group.code,
                        'uom_reference': {
                            'id': str(uom_obj.group.uom_reference_id),
                            'title': uom_obj.group.uom_reference.title,
                            'code': uom_obj.group.uom_reference.code,
                            'ratio': uom_obj.group.uom_reference.ratio,
                            'rounding': uom_obj.group.uom_reference.rounding,
                        } if uom_obj.group.uom_reference else {},
                    } if uom_obj.group else {},
                    'ratio': uom_obj.ratio,
                    'rounding': uom_obj.rounding,
                    'is_referenced_unit': uom_obj.is_referenced_unit,
                } if uom_obj else {},
                'product_unit_price': pm_obj.product_modified.get_current_cost_info(
                    get_type=1,
                    **{
                        'warehouse_id': pm_obj.prd_wh.warehouse_id,
                        'sale_order_id': None,  # ráp rã không gắn với SO
                    }
                ),
                'product_quantity_order_actual': 1,
                'quantity_import': 1,
                'gr_warehouse_data': cls.setup_representative_product_product_wh(
                    pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                ),
            })
        return gr_products_data

    @classmethod
    def setup_representative_product_product_wh(
            cls, pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
    ):
        if pm_obj:
            if re_prd_prd_wh_obj:
                return [{
                    'warehouse_id': str(re_prd_prd_wh_obj.warehouse_id),
                    'warehouse_data': {
                        'id': str(re_prd_prd_wh_obj.warehouse_id),
                        'title': re_prd_prd_wh_obj.warehouse.title,
                        'code': re_prd_prd_wh_obj.warehouse.code,
                    } if re_prd_prd_wh_obj.warehouse else {},
                    'quantity_import': 1,
                    'serial_data': [{
                        'expire_date': str(re_prd_prd_wh_serial_obj.expire_date)
                        if re_prd_prd_wh_serial_obj.expire_date is not None else None,
                        'manufacture_date': str(re_prd_prd_wh_serial_obj.manufacture_date)
                        if re_prd_prd_wh_serial_obj.manufacture_date is not None else None,
                        'serial_number': re_prd_prd_wh_serial_obj.serial_number,
                        'vendor_serial_number': re_prd_prd_wh_serial_obj.vendor_serial_number,
                        'warranty_start': str(re_prd_prd_wh_serial_obj.warranty_start)
                        if re_prd_prd_wh_serial_obj.warranty_start is not None else None,
                        'warranty_end': str(re_prd_prd_wh_serial_obj.warranty_end)
                        if re_prd_prd_wh_serial_obj.warranty_end is not None else None,
                    }] if re_prd_prd_wh_serial_obj else [],
                    'lot_data': [{
                        'lot_number': re_prd_prd_wh_lot_obj.lot_number,
                        'expire_date': str(re_prd_prd_wh_lot_obj.expire_date)
                        if re_prd_prd_wh_lot_obj.expire_date is not None else None,
                        'manufacture_date': str(re_prd_prd_wh_lot_obj.manufacture_date)
                        if re_prd_prd_wh_lot_obj.manufacture_date is not None else None,
                        'quantity_import': 1,
                    }] if re_prd_prd_wh_lot_obj else [],
                }]
        return []

    @classmethod
    def auto_import_representative_product(
        cls, pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
    ):
        model_cls = DisperseModel(app_model='inventory.goodsreceipt').get_model()
        if pm_obj and model_cls and hasattr(model_cls, 'objects'):
            gr_products_data = cls.setup_representative_product(
                pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
            )
            if gr_products_data:
                goods_receipt_obj = GRFromPMHandler.run_create(
                    pm_obj=pm_obj,
                    gr_products_data=gr_products_data,
                    model_cls=model_cls,
                    system_status=3,
                )
                return goods_receipt_obj
        return None

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('productmodification', True, self, kwargs)
                    try:
                        with transaction.atomic():
                            self.create_remove_component_product_mapped(self)
                            # B1: clone serial/lot cho sp đại diện
                            [
                                re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                            ] = self.auto_clone_for_representative_product(self)
                            # B2: cập nhập hoặc tạo giá đich danh khi nhập
                            if re_prd_prd_wh_serial_obj:
                                ProductSpecificIdentificationSerialNumber.create_or_update_si_product_serial(
                                    product=self.representative_product_modified,
                                    serial_obj=re_prd_prd_wh_serial_obj,
                                    specific_value=0,
                                    from_pm=True,
                                    product_modification=self
                                )
                            else:
                                if self.prd_wh_serial:
                                    ProductSpecificIdentificationSerialNumber.create_or_update_si_product_serial(
                                        product=self.product_modified,
                                        serial_obj=self.prd_wh_serial,
                                        specific_value=0,
                                        from_pm=True,
                                        product_modification=self
                                    )
                            # B3: nhập hàng vô sp đại diện
                            self.auto_import_representative_product(
                                self, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                            )
                            # B4: xuất hàng như thường (xuất cả sp gốc và sp đại diện)
                            issue_data = self.auto_create_goods_issue(
                                self, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                            )
                            # B5: tạo phiếu nhập tự động (nếu có SP đại diện thì không cần nhập lại sp gốc)
                            GRFromPMHandler.create_new(
                                self, issue_data, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                            )

                            # đánh dấu serial dùng cho ráp rã rồi
                            if self.prd_wh_serial:
                                self.prd_wh_serial.use_for_modification = True
                                self.prd_wh_serial.save(update_fields=['use_for_modification'])
                            if re_prd_prd_wh_serial_obj:
                                re_prd_prd_wh_serial_obj.use_for_modification = True
                                re_prd_prd_wh_serial_obj.save(update_fields=['use_for_modification'])

                            self.update_current_product_component(
                                self, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                            )
                    except Exception as err:
                        print(err)

        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product Modification'
        verbose_name_plural = 'Product Modification'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CurrentComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='current_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict) # {'title': ...; 'description':...}
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.FloatField()
    is_added_component = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Current Component'
        verbose_name_plural = 'Current Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class CurrentComponentDetail(SimpleAbstractModel):
    current_component = models.ForeignKey(
        CurrentComponent, on_delete=models.CASCADE, related_name='current_components_detail', null=True
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Current Component Detail'
        verbose_name_plural = 'Current Components Detail'
        default_permissions = ()
        permissions = ()


class RemovedComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='removed_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict)
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.FloatField(default=0)
    gr_remain_quantity = models.FloatField(default=0)
    is_mapped = models.BooleanField(default=False)
    product_mapped_data = models.JSONField(default=dict)
    fair_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Removed Component'
        verbose_name_plural = 'Removed Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class RemovedComponentDetail(SimpleAbstractModel):
    removed_component = models.ForeignKey(
        RemovedComponent, on_delete=models.CASCADE, related_name='removed_components_detail', null=True
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Removed Component Detail'
        verbose_name_plural = 'Removed Components Detail'
        default_permissions = ()
        permissions = ()
