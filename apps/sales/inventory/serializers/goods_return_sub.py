from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.delivery.models import OrderDeliveryProduct, OrderDeliverySub
from apps.sales.delivery.serializers import OrderDeliverySubUpdateSerializer
from apps.sales.inventory.models import GoodsReturnProductDetail


class GoodsReturnSubSerializer:
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
    def create_prod(cls, new_sub, latest_delivery, return_quantity, redelivery_quantity, gr_product):
        """
        (TH delivery đã DONE hết)
        Trả hàng 'gr_product':
        B1: Lọc hết sản phẩm của 'latest_delivery'
        B2: Chạy vòng lặp for:
            + Nếu sản phẩm đó trùng với 'gr_product' thì TẠO MỚI với:
            > 'delivered_quantity_before' -= số lượng return
            > 'remaining_quantity' và 'ready_quantity' = số lượng redelivery
            + Else: giữ nguyên 'delivered_quantity_before', 'remaining_quantity' và 'ready_quantity' = 0
        B3: Bulk create
        """
        prod_arr = []
        for obj in OrderDeliveryProduct.objects.filter(delivery_sub=latest_delivery):
            obj_return_quantity = return_quantity if obj.product == gr_product else 0
            obj_redelivery_quantity = redelivery_quantity if obj.product == gr_product else 0
            new_delivery_quantity = obj.delivery_quantity - obj_return_quantity + obj_redelivery_quantity
            new_prod = OrderDeliveryProduct(
                delivery_sub=new_sub,
                product=obj.product,
                uom=obj.uom,
                delivery_quantity=new_delivery_quantity,
                delivered_quantity_before=obj.delivery_quantity - obj_return_quantity,
                remaining_quantity=obj_redelivery_quantity,
                ready_quantity=obj_redelivery_quantity,
                picked_quantity=0,
                order=obj.order,
                delivery_data=obj.delivery_data
            )
            new_prod.put_backup_data()
            prod_arr.append(new_prod)
        OrderDeliveryProduct.objects.filter(delivery_sub=new_sub).delete()
        OrderDeliveryProduct.objects.bulk_create(prod_arr)
        return True

    @classmethod
    def update_prod(cls, ready_sub, return_quantity, redelivery_quantity, gr_product):
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
            obj.delivery_quantity = obj.delivery_quantity - obj_return_quantity + obj_redelivery_quantity
            obj.delivered_quantity_before -= obj_return_quantity
            obj.remaining_quantity += obj_redelivery_quantity
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
    def update_warehouse_prod(cls, product_detail_list, gr_product):
        for item in product_detail_list:
            type_value = item.get('type')
            if type_value == 0:  # General
                product = ProductWareHouse.objects.filter(product=gr_product).first()
                if product:  # update warehouse
                    product.stock_amount += item.get('default_return_number')
                    product.sold_amount -= item.get('default_return_number')
                    product.save(update_fields=['stock_amount', 'sold_amount'])
            elif type_value == 1:  # LOT
                lot = ProductWareHouseLot.objects.filter(id=item.get('lot_no_id')).first()
                if lot:  # update warehouse
                    lot.product_warehouse.stock_amount += item.get('lot_return_number')
                    lot.product_warehouse.sold_amount -= item.get('lot_return_number')
                    lot.quantity_import += item.get('lot_return_number')
                    lot.save(update_fields=['quantity_import'])
                    lot.product_warehouse.save(update_fields=['stock_amount', 'sold_amount'])
            elif type_value == 2:  # SN
                serial = ProductWareHouseSerial.objects.filter(id=item.get('serial_no_id')).first()
                if serial:  # update warehouse
                    serial.product_warehouse.stock_amount += 1
                    serial.product_warehouse.sold_amount -= 1
                    serial.is_delete = 0
                    serial.save(update_fields=['is_delete'])
                    serial.product_warehouse.save(update_fields=['stock_amount', 'sold_amount'])
        return True

    @classmethod
    def update_delivery(cls, goods_return, product_detail_list):
        sub_delivery = goods_return.delivery
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

        if goods_return.sale_order.delivery_status in [1, 2]:  # Have not done delivery
            ready_sub = OrderDeliverySub.objects.filter(order_delivery=sub_delivery.order_delivery, state=1).first()
            if ready_sub:
                ready_sub.delivery_quantity = ready_sub.delivery_quantity - return_quantity + redelivery_quantity
                ready_sub.delivered_quantity_before -= return_quantity
                ready_sub.remaining_quantity += redelivery_quantity
                ready_sub.ready_quantity += redelivery_quantity
                ready_sub.save(
                    update_fields=[
                        'delivery_quantity', 'delivered_quantity_before',
                        'remaining_quantity', 'ready_quantity'
                    ],
                    for_goods_return=True
                )
                cls.update_prod(ready_sub, return_quantity, redelivery_quantity, goods_return.product)
                cls.update_warehouse_prod(product_detail_list, goods_return.product)
        elif goods_return.sale_order.delivery_status == 3:  # Done delivery
            if redelivery_quantity != 0:
                filtered_delivery = OrderDeliverySub.objects.filter(order_delivery=sub_delivery.order_delivery)
                latest_delivery = filtered_delivery.latest('date_created')
                new_sub = OrderDeliverySub.objects.create(
                    company_id=latest_delivery.company_id,
                    tenant_id=latest_delivery.tenant_id,
                    order_delivery=latest_delivery.order_delivery,
                    date_done=None,
                    code=OrderDeliverySubUpdateSerializer.create_new_code(),
                    previous_step=latest_delivery,
                    times=filtered_delivery.count() + 1,
                    delivery_quantity=latest_delivery.delivery_quantity - return_quantity + redelivery_quantity,
                    delivered_quantity_before=latest_delivery.delivery_quantity - return_quantity,
                    remaining_quantity=redelivery_quantity,
                    ready_quantity=redelivery_quantity,
                    delivery_data=None,
                    is_updated=False,
                    state=1,
                    sale_order_data=latest_delivery.sale_order_data,
                    estimated_delivery_date=latest_delivery.estimated_delivery_date,
                    actual_delivery_date=latest_delivery.actual_delivery_date,
                    customer_data=latest_delivery.customer_data,
                    contact_data=latest_delivery.contact_data,
                    config_at_that_point=latest_delivery.config_at_that_point,
                    employee_inherit=latest_delivery.employee_inherit
                )
                cls.create_prod(new_sub, latest_delivery, return_quantity, redelivery_quantity, goods_return.product)
            cls.update_warehouse_prod(product_detail_list, goods_return.product)
        return True
