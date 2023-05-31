from uuid import uuid4

from celery import shared_task
from django.db import transaction

from apps.sales.delivery.models import (
    DeliveryConfig,
    OrderPicking, OrderPickingSub, OrderPickingProduct,
    OrderDelivery,
)
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct

__all__ = [
    'task_active_delivery_from_sale_order',
]


class SaleOrderActiveDeliverySerializer:
    def __init__(
            self, sale_order_obj: SaleOrder, order_products: list[SaleOrderProduct], delivery_config_obj: DeliveryConfig
    ):
        if sale_order_obj:
            self.tenant_id = sale_order_obj.tenant_id
            self.company_id = sale_order_obj.company_id

            self.order_obj = sale_order_obj
            self.order_products = order_products
            self.config_obj = delivery_config_obj
        else:
            raise AttributeError('instance must be required')

    def __create_order_picking_sub_map_product(self):
        sub_id = uuid4()
        m2m_obj_arr = []
        pickup_quantity = 0
        for m2m_obj in self.order_products:
            if m2m_obj.product_quantity and isinstance(m2m_obj.product_quantity, int):
                pickup_quantity += m2m_obj.product_quantity
            obj_tmp = OrderPickingProduct(
                picking_sub_id=sub_id,
                product=m2m_obj.product,
                product_data={
                    'id': str(m2m_obj.product.id),
                    'title': str(m2m_obj.product.title),
                    'code': str(m2m_obj.product.code),
                    'remarks': ''
                } if m2m_obj.product else {},
                uom=m2m_obj.unit_of_measure,
                uom_data={
                    'id': str(m2m_obj.unit_of_measure.id),
                    'title': str(m2m_obj.unit_of_measure.title),
                    'code': str(m2m_obj.unit_of_measure.code),
                } if m2m_obj.unit_of_measure else {},

                pickup_quantity=m2m_obj.product_quantity,
                picked_quantity_before=0,
                remaining_quantity=m2m_obj.product_quantity,
                picked_quantity=0,
            )
            obj_tmp.before_save()
            m2m_obj_arr.append(obj_tmp)
        return sub_id, pickup_quantity, m2m_obj_arr

    def _create_order_picking(self):
        # data
        sub_id, pickup_quantity, m2m_obj_arr = self.__create_order_picking_sub_map_product()

        # setup MAIN
        obj = OrderPicking.objects.create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order=self.order_obj,
            title=self.order_obj.title,
            sale_order_data={
                "id": str(self.order_obj.id),
                "title": str(self.order_obj.title),
                "code": str(self.order_obj.code),
            },
            ware_house=None,
            ware_house_data={},
            estimated_delivery_date=None,
            state=0,
            remarks='',
            delivery_option=1 if self.config_obj.is_partial_ship else 0,  # 0: Full, 1: Partial
            sub=None,

            pickup_quantity=pickup_quantity,
            picked_quantity_before=0,
            # remaining_quantity=0, # autofill by pickup_quantity - picked_quantity_before
            picked_quantity=0,
            pickup_data={},
        )

        # setup SUB
        sub_obj = OrderPickingSub.objects.create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            id=sub_id,
            order_picking=obj,
            date_done=None,
            previous_step=None,
            times=1,

            pickup_quantity=pickup_quantity,
            picked_quantity_before=0,
            # remaining_quantity=0, # autofill by pickup_quantity - picked_quantity_before
            picked_quantity=0,
            pickup_data={},
        )
        OrderPickingProduct.objects.bulk_create(m2m_obj_arr)

        # update sub
        obj.sub = sub_obj
        obj.save(update_fields=['sub'])
        return obj

    def _create_order_delivery(
            self,
            delivery_quantity,

    ):
        return OrderDelivery.objects.create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order=self.order_obj,
            sale_order_data={
                "id": str(self.order_obj.id),
                "title": str(self.order_obj.title),
                "code": str(self.order_obj.code),
            },
            from_picking_area='',
            customer=self.order_obj.customer,
            customer_data={
                "id": str(self.order_obj.customer_id),
                "title": str(self.order_obj.customer.title),
                "code": str(self.order_obj.customer.code),
            },
            contact=self.order_obj.contact,
            contact_data={
                "id": str(self.order_obj.contact_id),
                "title": str(self.order_obj.contact.title),
                "code": str(self.order_obj.contact.code),
            },
            kind_pickup=0 if self.config_obj.is_picking else 1,
            sub=None,
            delivery_option=0 if not self.config_obj.is_partial_ship else 1,

            delivery_quantity=delivery_quantity,
            delivered_quantity_before=0,
            remaining_quantity=delivery_quantity,
            ready_quantity=0,
            delivery_data={},
        )

    def active(self) -> (bool, str):
        try:
            with transaction.atomic():
                if (
                        not OrderPicking.objects.filter(sale_order=self.order_obj).exists()
                        and not OrderDelivery.objects.filter(sale_order=self.order_obj).exists()
                ):
                    if self.config_obj.is_picking is True:
                        obj_picking = self._create_order_picking()
                        obj_delivery = self._create_order_delivery(delivery_quantity=obj_picking.pickup_quantity)
                        print(obj_picking, obj_delivery)
                    else:
                        _id, pickup_quantity, _y = self.__create_order_picking_sub_map_product()
                        obj_delivery = self._create_order_delivery(delivery_quantity=pickup_quantity)
                        print(pickup_quantity, obj_delivery)
                    # raise ValueError('Cancel with check!')
                    if obj_delivery:
                        return True, ''
                    raise ValueError('Have exception in create picking or deliver process')
                return False, 'Sale Order had exist delivery'
        except Exception as err:
            print(err)
            return False, str(err)


@shared_task
def task_active_delivery_from_sale_order(sale_order_id):
    sale_order_obj = SaleOrder.objects.get(pk=sale_order_id)
    sale_order_products = SaleOrderProduct.objects.select_related(
        'product', 'unit_of_measure'
    ).filter(
        sale_order=sale_order_obj
    )
    config_obj = DeliveryConfig.objects.get(company=sale_order_obj.company)
    state, msg_returned = SaleOrderActiveDeliverySerializer(
        sale_order_obj=sale_order_obj,
        order_products=sale_order_products,
        delivery_config_obj=config_obj,
    ).active()
    if state is True:
        sale_order_obj.delivery_call = True
        sale_order_obj.save(update_fields=['delivery_call'])
    return state, msg_returned
