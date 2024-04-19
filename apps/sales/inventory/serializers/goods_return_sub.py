from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.acceptance.models import FinalAcceptanceIndicator
from apps.sales.delivery.models import OrderDeliveryProduct, OrderDeliverySub, OrderPickingSub, OrderPickingProduct
from apps.sales.delivery.serializers import OrderDeliverySubUpdateSerializer
from apps.sales.inventory.models import GoodsReturnProductDetail
from apps.sales.report.models import ReportInventorySub


class GoodsReturnSubSerializerForNonPicking:
    @classmethod
    def create_delivery_product_detail_mapped(cls, goods_return, product_detail_list):
        bulk_info = []
        for item in product_detail_list:
            bulk_info.append(
                GoodsReturnProductDetail.objects.create(
                    goods_return=goods_return,
                    **item
                )
            )
        GoodsReturnProductDetail.objects.filter(goods_return=goods_return).delete()
        GoodsReturnProductDetail.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def prepare_data_for_logging(cls, instance, return_quantity, product_detail_list):
        activities_data = []
        delivery_product = OrderDeliveryProduct.objects.filter(
            delivery_sub=instance.delivery,
            product=instance.product
        ).first()
        if delivery_product:
            lot_data = []
            for lot in product_detail_list:
                type_value = lot.get('type')
                if type_value == 1:  # is LOT
                    prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot['lot_no_id']).first()
                    if prd_wh_lot:
                        lot_data.append({
                            'lot_id': str(prd_wh_lot.id),
                            'lot_number': prd_wh_lot.lot_number,
                            'lot_quantity': return_quantity,
                            'lot_value': delivery_product.product_unit_price * return_quantity,
                            'lot_expire_date': str(prd_wh_lot.expire_date)
                        })
            activities_data.append({
                'product': instance.product,
                'warehouse': instance.return_to_warehouse,
                'system_date': instance.date_created,
                'posting_date': None,
                'document_date': None,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': return_quantity,
                'cost': delivery_product.product_unit_price,
                'value': delivery_product.product_unit_price * return_quantity,
                'lot_data': lot_data
            })
        else:
            raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_created,
            activities_data
        )
        return True

    @classmethod
    def create_prod(cls, new_sub, delivery_sub_obj, return_quantity, redelivery_quantity, gr_product):
        """
        (TH delivery đã DONE hết)
        Trả hàng 'gr_product':
        B1: Lọc hết sản phẩm của 'delivery_sub_obj'
        B2: Chạy vòng lặp for:
            + Nếu sản phẩm đó trùng với 'gr_product' thì TẠO MỚI với:
            > 'delivered_quantity_before' -= số lượng return
            > 'remaining_quantity' và 'ready_quantity' = số lượng redelivery
            + Else: giữ nguyên 'delivered_quantity_before', 'remaining_quantity' và 'ready_quantity' = 0
        B3: Bulk create
        """
        prod_arr = []
        for obj in OrderDeliveryProduct.objects.filter(delivery_sub=delivery_sub_obj):
            obj_return_quantity = return_quantity if obj.product == gr_product else 0
            obj_redelivery_quantity = redelivery_quantity if obj.product == gr_product else 0
            new_prod = OrderDeliveryProduct(
                delivery_sub=new_sub,
                product=obj.product,
                uom=obj.uom,
                delivery_quantity=obj.delivery_quantity - obj_return_quantity + obj_redelivery_quantity,
                delivered_quantity_before=obj.delivery_quantity - obj_return_quantity,
                remaining_quantity=obj_redelivery_quantity,
                ready_quantity=obj_redelivery_quantity,
                picked_quantity=0,
                order=obj.order,
                delivery_data=obj.delivery_data
            )
            new_prod.before_save()
            prod_arr.append(new_prod)
        OrderDeliveryProduct.objects.filter(delivery_sub=new_sub).delete()
        OrderDeliveryProduct.objects.bulk_create(prod_arr)
        return True

    @classmethod
    def update_prod(cls, ready_sub, return_quantity, redelivery_quantity, gr_product, for_picking):
        """
        (TH còn phiếu delivery chưa DONE)
        B0: 'ready_sub' là phiếu delivery hiện tại đang Ready
        Trả hàng 'gr_product':
        B1: Lọc hết sản phẩm của 'ready_sub'
        B2: Chạy vòng lặp for cập nhập:
            + Nếu sản phẩm đó trùng với 'gr_product' thì CẬP NHẬP với:
            > 'delivered_quantity_before' -= số lượng return
            > 'remaining_quantity' và 'ready_quantity' += số lượng redelivery
            + Else: giữ nguyên 'delivered_quantity_before', 'remaining_quantity' và 'ready_quantity' = 0
        B3: Done
        """
        for obj in OrderDeliveryProduct.objects.filter(delivery_sub=ready_sub):
            obj_return_quantity = return_quantity if obj.product == gr_product else 0
            obj_redelivery_quantity = redelivery_quantity if obj.product == gr_product else 0
            if obj_return_quantity > obj.delivery_quantity:
                raise serializers.ValidationError({
                    'Return quantity':
                        f'Return quantity ({obj_return_quantity}) > delivery quantity ({obj.delivery_quantity}).'
                })
            obj.delivery_quantity = obj.delivery_quantity - obj_return_quantity + obj_redelivery_quantity
            obj.delivered_quantity_before -= obj_return_quantity
            obj.remaining_quantity += obj_redelivery_quantity
            if not for_picking:
                obj.ready_quantity += obj_redelivery_quantity
            obj.save(
                update_fields=[
                    'delivery_quantity', 'delivered_quantity_before',
                    'remaining_quantity', 'ready_quantity'
                ],
                for_goods_return=True
            )
        return True

    @classmethod
    def create_product_warehouse_for_general(cls, gr_obj, return_quantity):
        # get delivery product
        delivery_product = OrderDeliveryProduct.objects.filter(
            delivery_sub=gr_obj.delivery,
            product=gr_obj.product
        ).first()
        if delivery_product:
            ProductWareHouse.push_from_receipt(
                tenant_id=gr_obj.tenant_id,
                company_id=gr_obj.company_id,
                product_id=gr_obj.product_id,
                warehouse_id=gr_obj.return_to_warehouse_id,
                uom_id=gr_obj.uom_id,
                tax_id=delivery_product.product.sale_tax_id,
                amount=return_quantity,
                unit_price=delivery_product.product_unit_price,
                lot_data=[],
                serial_data=[],
            )
            return True
        raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})

    @classmethod
    def create_product_warehouse_for_lot(cls, gr_obj, return_quantity, sample_lot):
        # get delivery product
        delivery_product = OrderDeliveryProduct.objects.filter(
            delivery_sub=gr_obj.delivery,
            product=gr_obj.product
        ).first()
        if delivery_product:
            new_prd_wh = ProductWareHouse.objects.filter(
                tenant_id=gr_obj.tenant_id,
                company_id=gr_obj.company_id,
                product=gr_obj.product,
                warehouse=gr_obj.return_to_warehouse
            ).first()
            if not new_prd_wh:
                new_prd_wh = ProductWareHouse.objects.create(
                    tenant_id=gr_obj.tenant_id,
                    company_id=gr_obj.company_id,
                    product=gr_obj.product,
                    uom=gr_obj.uom,
                    warehouse=gr_obj.return_to_warehouse,
                    tax=delivery_product.product.sale_tax,
                    unit_price=delivery_product.product_unit_price,
                    stock_amount=return_quantity,
                    receipt_amount=return_quantity,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': gr_obj.product_id,
                        'code': gr_obj.product.code,
                        'title': gr_obj.product.title
                    },
                    warehouse_data={
                        'id': gr_obj.return_to_warehouse_id,
                        'code': gr_obj.return_to_warehouse.code,
                        'title': gr_obj.return_to_warehouse.title
                    },
                    uom_data={
                        'id': gr_obj.uom_id,
                        'code': gr_obj.uom.code,
                        'title': gr_obj.uom.title
                    },
                    tax_data={
                        'id': delivery_product.product.sale_tax_id,
                        'code': delivery_product.product.sale_tax.code,
                        'title': delivery_product.product.sale_tax.title,
                        'rate': delivery_product.product.sale_tax.rate
                    }
                )
            else:
                new_prd_wh.stock_amount += return_quantity
                new_prd_wh.sold_amount += return_quantity
                new_prd_wh.save(update_fields=['stock_amount', 'sold_amount'])
            ProductWareHouseLot.objects.create(
                tenant_id=gr_obj.tenant_id,
                company_id=gr_obj.company_id,
                product_warehouse=new_prd_wh,
                lot_number=sample_lot.lot_number,
                quantity_import=return_quantity,
                expire_date=sample_lot.expire_date,
                manufacture_date=sample_lot.manufacture_date
            )
            return True
        raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})

    @classmethod
    def create_product_warehouse_for_sn(cls, gr_obj, return_quantity, sample_sn):
        # get delivery product
        delivery_product = OrderDeliveryProduct.objects.filter(
            delivery_sub=gr_obj.delivery,
            product=gr_obj.product
        ).first()
        if delivery_product:
            new_prd_wh = ProductWareHouse.objects.filter(
                tenant_id=gr_obj.tenant_id,
                company_id=gr_obj.company_id,
                product=gr_obj.product,
                warehouse=gr_obj.return_to_warehouse
            ).first()
            if not new_prd_wh:
                new_prd_wh = ProductWareHouse.objects.create(
                    tenant_id=gr_obj.tenant_id,
                    company_id=gr_obj.company_id,
                    product=gr_obj.product,
                    uom=gr_obj.uom,
                    warehouse=gr_obj.return_to_warehouse,
                    tax=delivery_product.product.sale_tax,
                    unit_price=delivery_product.product_unit_price,
                    stock_amount=return_quantity,
                    receipt_amount=return_quantity,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': gr_obj.product_id,
                        'code': gr_obj.product.code,
                        'title': gr_obj.product.title
                    },
                    warehouse_data={
                        'id': gr_obj.return_to_warehouse_id,
                        'code': gr_obj.return_to_warehouse.code,
                        'title': gr_obj.return_to_warehouse.title
                    },
                    uom_data={
                        'id': gr_obj.uom_id,
                        'code': gr_obj.uom.code,
                        'title': gr_obj.uom.title
                    },
                    tax_data={
                        'id': delivery_product.product.sale_tax_id,
                        'code': delivery_product.product.sale_tax.code,
                        'title': delivery_product.product.sale_tax.title,
                        'rate': delivery_product.product.sale_tax.rate
                    }
                )
            else:
                new_prd_wh.stock_amount += 1
                new_prd_wh.sold_amount += 1
                new_prd_wh.save(update_fields=['stock_amount', 'sold_amount'])
            ProductWareHouseSerial.objects.create(
                tenant_id=gr_obj.tenant_id,
                company_id=gr_obj.company_id,
                product_warehouse=new_prd_wh,
                vendor_serial_number=sample_sn.vendor_serial_number,
                serial_number=sample_sn.serial_number,
                expire_date=sample_sn.expire_date,
                manufacture_date=sample_sn.manufacture_date,
                warranty_start=sample_sn.warranty_start,
                warranty_end=sample_sn.warranty_end
            )
            return True
        raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})

    @classmethod
    def update_warehouse_prod_type_general(cls, product_wh, item, gr_obj, return_quantity):
        if product_wh:
            product_wh.stock_amount += item.get('default_return_number')
            product_wh.sold_amount -= item.get('default_return_number')
            product_wh.save(update_fields=['stock_amount', 'sold_amount'])
        else:
            cls.create_product_warehouse_for_general(gr_obj, return_quantity)

    @classmethod
    def update_warehouse_prod_type_lot(cls, product_wh, item, gr_obj, return_quantity):
        lot = ProductWareHouseLot.objects.filter(id=item.get('lot_no_id'))
        if product_wh:
            lot_wh = lot.filter(product_warehouse=product_wh).first()
            if lot_wh:
                lot_wh.product_warehouse.stock_amount += item.get('lot_return_number')
                lot_wh.product_warehouse.sold_amount -= item.get('lot_return_number')
                lot_wh.quantity_import += item.get('lot_return_number')
                lot_wh.save(update_fields=['quantity_import'])
                lot_wh.product_warehouse.save(update_fields=['stock_amount', 'sold_amount'])
            else:
                if lot.first():
                    ProductWareHouseLot.objects.create(
                        tenant_id=gr_obj.tenant_id,
                        company_id=gr_obj.company_id,
                        product_warehouse=product_wh,
                        lot_number=lot.first().lot_number,
                        quantity_import=item.get('lot_return_number'),
                        expire_date=lot.first().expire_date,
                        manufacture_date=lot.first().manufacture_date
                    )
                    product_wh.stock_amount += item.get('lot_return_number')
                    product_wh.sold_amount -= item.get('lot_return_number')
                    product_wh.save(update_fields=['stock_amount', 'sold_amount'])
                else:
                    raise serializers.ValidationError({'No LOT': 'This Lot is not found.'})
        else:
            if lot.first():
                cls.create_product_warehouse_for_lot(gr_obj, return_quantity, lot.first())
            else:
                raise serializers.ValidationError({'No LOT': 'This Lot is not found.'})

    @classmethod
    def update_warehouse_prod_type_sn(cls, product_wh, item, gr_obj, return_quantity):
        serial = ProductWareHouseSerial.objects.filter(id=item.get('serial_no_id'))
        if product_wh:
            serial_wh = serial.filter(product_warehouse=product_wh).first()
            if serial_wh:
                serial_wh.product_warehouse.stock_amount += 1
                serial_wh.product_warehouse.sold_amount -= 1
                serial_wh.is_delete = 0
                serial_wh.save(update_fields=['is_delete'])
                serial_wh.product_warehouse.save(update_fields=['stock_amount', 'sold_amount'])
            else:
                if serial.first():
                    ProductWareHouseSerial.objects.create(
                        tenant_id=gr_obj.tenant_id,
                        company_id=gr_obj.company_id,
                        product_warehouse=product_wh,
                        vendor_serial_number=serial.first().vendor_serial_number,
                        serial_number=serial.first().serial_number,
                        expire_date=serial.first().expire_date,
                        manufacture_date=serial.first().manufacture_date,
                        warranty_start=serial.first().warranty_start,
                        warranty_end=serial.first().warranty_end
                    )
                    product_wh.stock_amount += item.get('lot_return_number')
                    product_wh.sold_amount -= item.get('lot_return_number')
                    product_wh.save(update_fields=['stock_amount', 'sold_amount'])
                else:
                    raise serializers.ValidationError({'No SN': 'This Serial is not found.'})
        else:
            if serial.first():
                cls.create_product_warehouse_for_sn(gr_obj, return_quantity, serial.first())
            else:
                raise serializers.ValidationError({'No SN': 'This Serial is not found.'})

    @classmethod
    def update_warehouse_prod(cls, product_detail_list, gr_obj, return_quantity):
        """
        Có 3 TH:
        1) Nếu product không có phương thức quản lí tồn kho: cập nhập trong ProductWareHouse
        2) Nếu product quản lí ồn kho = LOT: cập nhập trong ProductWareHouse & ProductWareHouseLot
        3) Nếu product quản lí ồn kho = SN: cập nhập trong ProductWareHouse & ProductWareHouseSerial
        """
        gr_product = gr_obj.product
        product_wh = ProductWareHouse.objects.filter(
            tenant_id=gr_obj.tenant_id,
            company_id=gr_obj.company_id,
            product=gr_product,
            warehouse=gr_obj.return_to_warehouse
        ).first()
        for item in product_detail_list:
            type_value = item.get('type')
            if type_value == 0:  # General
                cls.update_warehouse_prod_type_general(product_wh, item, gr_obj, return_quantity)
            elif type_value == 1:  # LOT
                cls.update_warehouse_prod_type_lot(product_wh, item, gr_obj, return_quantity)
            elif type_value == 2:  # SN
                cls.update_warehouse_prod_type_sn(product_wh, item, gr_obj, return_quantity)
        cls.prepare_data_for_logging(gr_obj, return_quantity, product_detail_list)
        return True

    @classmethod
    def update_product_state(cls, returned_delivery, product_detail_list):
        returned_product_by_sn = []
        returned_product_by_lot = []
        lot_return_number = 0
        default_return_number = 0
        for item in product_detail_list:
            if item.get('type') == 0:
                default_return_number = item.get('default_return_number')
            elif item.get('type') == 1:
                returned_product_by_lot.append(item.get('lot_no_id'))
                lot_return_number = item.get('lot_return_number')
            elif item.get('type') == 2:
                returned_product_by_sn.append(item.get('serial_no_id'))
        if len(returned_product_by_lot) > 0:
            for item in returned_delivery.delivery_lot_delivery_sub.all():
                if str(item.product_warehouse_lot_id) in returned_product_by_lot:
                    item.returned_quantity += lot_return_number
                    item.save(update_fields=['returned_quantity'])
        elif len(returned_product_by_sn) > 0:
            for item in returned_delivery.delivery_serial_delivery_sub.all():
                if str(item.product_warehouse_serial_id) in returned_product_by_sn:
                    item.is_returned = True
                    item.save(update_fields=['is_returned'])
        else:
            for item in returned_delivery.delivery_product_delivery_sub.all():
                item.returned_quantity_default += default_return_number
                item.save(update_fields=['returned_quantity_default'])
        return True

    @classmethod
    def update_delivery(cls, goods_return, product_detail_list, for_picking=False):
        """
        B1: Lấy phiếu Delivery đã chọn từ phiếu trả hàng
        B2: Có 2 TH:
            1) Nếu còn phiếu Delivery chưa Done: UPDATE lại phiếu Delivery hiện có > UPDATE product warehouse
            2) Nếu Delivery đã Done:
               + Nếu có giao lại: CREATE phiếu Delivery mới > UPDATE product warehouse
               + Nếu không giao lại: UPDATE product warehouse
        """
        returned_delivery = goods_return.delivery
        return_quantity = 0
        redelivery_quantity = 0
        for item in product_detail_list:
            if item.get('type') == 0:
                return_quantity += item.get('default_return_number', 0)
                redelivery_quantity += item.get('default_redelivery_number', 0)
            elif item.get('type') == 1:
                return_quantity += item.get('lot_return_number', 0)
                redelivery_quantity += item.get('lot_redelivery_number', 0)
            elif item.get('type') == 2:
                return_quantity += item.get('is_return', 0)
                redelivery_quantity += item.get('is_redelivery', 0)
        if redelivery_quantity > return_quantity:
            raise serializers.ValidationError({
                'Redelivery quantity':
                    f'Redelivery quantity ({redelivery_quantity}) > return quantity ({return_quantity}).'
            })
        cls.update_product_state(returned_delivery, product_detail_list)
        if goods_return.sale_order.delivery_status in [1, 2]:  # Have not done delivery
            ready_sub = returned_delivery.order_delivery.sub
            ready_sub.delivery_quantity = ready_sub.delivery_quantity - return_quantity + redelivery_quantity
            ready_sub.delivered_quantity_before -= return_quantity
            ready_sub.remaining_quantity += redelivery_quantity
            if not for_picking:
                ready_sub.ready_quantity += redelivery_quantity
            ready_sub.save(update_fields=[
                'delivery_quantity', 'delivered_quantity_before',
                'remaining_quantity', 'ready_quantity'
            ])
            cls.update_prod(ready_sub, return_quantity, redelivery_quantity, goods_return.product, for_picking)
            cls.update_warehouse_prod(product_detail_list, goods_return, return_quantity)
        elif goods_return.sale_order.delivery_status == 3:  # Done delivery
            if redelivery_quantity != 0:
                delivery_sub_obj = returned_delivery.order_delivery.sub
                new_sub = OrderDeliverySub.objects.create(
                    company_id=delivery_sub_obj.company_id,
                    tenant_id=delivery_sub_obj.tenant_id,
                    order_delivery=delivery_sub_obj.order_delivery,
                    date_done=None,
                    code=OrderDeliverySubUpdateSerializer.create_new_code(),
                    previous_step=delivery_sub_obj,
                    times=delivery_sub_obj.times + 1,
                    delivery_quantity=delivery_sub_obj.delivery_quantity - return_quantity + redelivery_quantity,
                    delivered_quantity_before=delivery_sub_obj.delivery_quantity - return_quantity,
                    remaining_quantity=redelivery_quantity,
                    ready_quantity=redelivery_quantity,
                    delivery_data=None,
                    is_updated=False,
                    state=1,  # ready
                    sale_order_data=delivery_sub_obj.sale_order_data,
                    estimated_delivery_date=delivery_sub_obj.estimated_delivery_date,
                    actual_delivery_date=delivery_sub_obj.actual_delivery_date,
                    customer_data=delivery_sub_obj.customer_data,
                    contact_data=delivery_sub_obj.contact_data,
                    config_at_that_point=delivery_sub_obj.config_at_that_point,
                    employee_inherit=delivery_sub_obj.employee_inherit
                )
                cls.create_prod(new_sub, delivery_sub_obj, return_quantity, redelivery_quantity, goods_return.product)
                returned_delivery.order_delivery.sub = new_sub
                returned_delivery.order_delivery.save(update_fields=['sub'])
                goods_return.sale_order.delivery_status = 2
                goods_return.sale_order.save(update_fields=['delivery_status'])
            cls.update_warehouse_prod(product_detail_list, goods_return, return_quantity)
        return True


class GoodsReturnSubSerializerForPicking:
    @classmethod
    def create_new_picking(cls, picking_obj_sub, return_quantity, redelivery_quantity, gr_product):
        new_sub = OrderPickingSub.objects.create(
            tenant_id=picking_obj_sub.tenant_id,
            company_id=picking_obj_sub.company_id,
            order_picking=picking_obj_sub.order_picking,
            date_done=None,
            previous_step=picking_obj_sub,
            times=picking_obj_sub.times + 1,
            pickup_quantity=picking_obj_sub.pickup_quantity - return_quantity + redelivery_quantity,
            picked_quantity_before=picking_obj_sub.pickup_quantity - return_quantity,
            remaining_quantity=redelivery_quantity,
            picked_quantity=0,
            pickup_data=picking_obj_sub.pickup_data,
            sale_order_data=picking_obj_sub.sale_order_data,
            delivery_option=picking_obj_sub.delivery_option,
            config_at_that_point=picking_obj_sub.config_at_that_point,
            employee_inherit=picking_obj_sub.employee_inherit
        )
        bulk_info = []
        for obj in OrderPickingProduct.objects.filter(picking_sub=picking_obj_sub):
            obj_return_quantity = return_quantity if obj.product == gr_product else 0
            obj_redelivery_quantity = redelivery_quantity if obj.product == gr_product else 0
            new_item = OrderPickingProduct(
                product_data=obj.product_data,
                uom_data=obj.uom_data,
                uom_id=obj.uom_id,
                pickup_quantity=obj.pickup_quantity - obj_return_quantity + obj_redelivery_quantity,
                picked_quantity_before=obj.picked_quantity_before + obj.picked_quantity - obj_return_quantity ,
                remaining_quantity=obj.pickup_quantity - (obj.picked_quantity_before + obj.picked_quantity),
                picked_quantity=0,
                picking_sub=new_sub,
                product_id=obj.product_id,
                order=obj.order
            )
            new_item.before_save()
            bulk_info.append(new_item)
        OrderPickingProduct.objects.filter(picking_sub=new_sub).delete()
        OrderPickingProduct.objects.bulk_create(bulk_info)
        return new_sub

    @classmethod
    def update_picking(cls, picking_obj_sub, return_quantity, redelivery_quantity, gr_product):
        picking_obj_sub.pickup_quantity = picking_obj_sub.pickup_quantity - return_quantity + redelivery_quantity
        picking_obj_sub.picked_quantity_before -= return_quantity
        picking_obj_sub.remaining_quantity += redelivery_quantity
        picking_obj_sub.save(update_fields=[
            'pickup_quantity', 'picked_quantity_before', 'remaining_quantity'
        ])
        for obj in OrderPickingProduct.objects.filter(picking_sub=picking_obj_sub):
            obj_return_quantity = return_quantity if obj.product == gr_product else 0
            obj_redelivery_quantity = redelivery_quantity if obj.product == gr_product else 0

            obj.pickup_quantity = obj.pickup_quantity - obj_return_quantity + obj_redelivery_quantity
            obj.picked_quantity_before -= obj_return_quantity
            obj.remaining_quantity += obj_redelivery_quantity
            obj.save(update_fields=[
                'pickup_quantity', 'picked_quantity_before', 'remaining_quantity'
            ])
        return True

    @classmethod
    def update_delivery(cls, goods_return, product_detail_list):
        """
        Có 2 TH:
        1) Nếu tất cả Picking đều Done: CREATE Picking mới > CREATE/UPDATE Delivery
        2) Nếu tồn tại Picking chưa Done: UPDATE Picking đó > UPDATE Delivery
        """
        return_quantity = 0
        redelivery_quantity = 0
        for item in product_detail_list:
            if item.get('type') == 0:
                return_quantity += item.get('default_return_number', 0)
                redelivery_quantity += item.get('default_redelivery_number', 0)
            elif item.get('type') == 1:
                return_quantity += item.get('lot_return_number', 0)
                redelivery_quantity += item.get('lot_redelivery_number', 0)
            elif item.get('type') == 2:
                return_quantity += item.get('is_return', 0)
                redelivery_quantity += item.get('is_redelivery', 0)

        picking_obj = goods_return.sale_order.picking_of_sale_order
        if picking_obj.sub.state == 1:
            new_sub = cls.create_new_picking(
                picking_obj.sub, return_quantity, redelivery_quantity, goods_return.product
            )
            picking_obj.sub = new_sub
            picking_obj.save(update_fields=['sub'])
        else:
            cls.update_picking(picking_obj.sub, return_quantity, redelivery_quantity, goods_return.product)
        return GoodsReturnSubSerializerForNonPicking.update_delivery(goods_return, product_detail_list, True)


# FUNCTIONS AFTER INSTANCE CREATED
class GReturnProductInformationHandle:

    @classmethod
    def main_handle(cls, instance):
        for return_product in instance.goods_return_product_detail.all():
            product = None
            value = 0
            is_redelivery = False
            if return_product.type == 1:  # lot
                product, value = cls.setup_by_lot(return_product=return_product)
                if return_product.lot_redelivery_number > 0:  # redelivery
                    is_redelivery = True
            if return_product.type == 2:  # serial
                product, value = cls.setup_by_serial(return_product=return_product)
                if return_product.is_redelivery is True:  # redelivery
                    is_redelivery = True
            if product and is_redelivery is False:  # update product no redelivery
                product.save(**{
                    'update_transaction_info': True,
                    'quantity_return': value,
                    'update_fields': ['stock_amount', 'available_amount']
                })
            if product and is_redelivery is True:  # update product with redelivery
                product.save(**{
                    'update_transaction_info': True,
                    'quantity_return_redelivery': value,
                    'update_fields': ['wait_delivery_amount', 'stock_amount', 'available_amount']
                })
        return True

    @classmethod
    def setup_by_lot(cls, return_product):
        product = None
        value = 0
        if return_product.type == 1:  # lot
            if return_product.lot_no:
                if return_product.lot_no.product_warehouse:
                    product = return_product.lot_no.product_warehouse.product
                    value = return_product.lot_return_number
        return product, value

    @classmethod
    def setup_by_serial(cls, return_product):
        product = None
        value = 0
        if return_product.type == 2:  # serial
            if return_product.serial_no:
                if return_product.serial_no.product_warehouse:
                    product = return_product.serial_no.product_warehouse.product
                    value = 1
        return product, value


class GReturnFinalAcceptanceHandle:

    @classmethod
    def main_handle(cls, instance):
        product_data_json = {}
        for return_product in instance.goods_return_product_detail.all():
            product_id = None
            value = 0
            if return_product.type == 1:  # lot
                product_id, value = cls.setup_by_lot(instance=instance, return_product=return_product)
            if return_product.type == 2:  # serial
                product_id, value = cls.setup_by_serial(instance=instance, return_product=return_product)
            if product_id:
                if str(product_id) not in product_data_json:
                    product_data_json.update({
                        str(product_id): value
                    })
                else:
                    product_data_json[str(product_id)] += value
            cls.update_fa_delivery(instance=instance, product_data_json=product_data_json)
        return True

    @classmethod
    def update_fa_delivery(cls, instance, product_data_json):
        for fa_ind_delivery in FinalAcceptanceIndicator.objects.filter_current(
                fill__tenant=True, fill__company=True,
                sale_order_id=instance.sale_order_id, delivery_sub_id=instance.delivery_id,
        ):
            fa_ind_product_id = str(fa_ind_delivery.product_id)
            if fa_ind_product_id in product_data_json:
                fa_ind_delivery.actual_value = fa_ind_delivery.actual_value - product_data_json[fa_ind_product_id]
                fa_ind_delivery.save(update_fields=['actual_value'])
        return True

    @classmethod
    def setup_by_lot(cls, instance, return_product):
        product_id = None
        value = 0
        if return_product.type == 1:  # lot
            if return_product.lot_no:
                if return_product.lot_no.product_warehouse:
                    product_id = return_product.lot_no.product_warehouse.product_id
                    warehouse_id = return_product.lot_no.product_warehouse.warehouse_id
                    pw_inventory = ReportInventorySub.objects.filter(
                        report_inventory__tenant_id=instance.tenant_id,
                        report_inventory__company_id=instance.company_id,
                        product_id=product_id,
                        warehouse_id=warehouse_id,
                    ).first()
                    value = pw_inventory.current_cost * return_product.lot_return_number if pw_inventory else 0
        return product_id, value

    @classmethod
    def setup_by_serial(cls, instance, return_product):
        product_id = None
        value = 0
        if return_product.type == 2:  # serial
            if return_product.serial_no:
                if return_product.serial_no.product_warehouse:
                    product_id = return_product.serial_no.product_warehouse.product_id
                    warehouse_id = return_product.serial_no.product_warehouse.warehouse_id
                    pw_inventory = ReportInventorySub.objects.filter(
                        report_inventory__tenant_id=instance.tenant_id,
                        report_inventory__company_id=instance.company_id,
                        product_id=product_id,
                        warehouse_id=warehouse_id,
                    ).first()
                    value = pw_inventory.current_cost if pw_inventory else 0
        return product_id, value
