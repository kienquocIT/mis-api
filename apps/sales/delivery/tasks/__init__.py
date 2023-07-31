from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from celery import shared_task
from apps.sales.delivery.models import (
    DeliveryConfig,
    OrderPicking, OrderPickingSub, OrderPickingProduct,
    OrderDelivery, OrderDeliveryProduct, OrderDeliverySub
)
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct, SaleOrderLogistic

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

        self.check_has_prod_services = 0

    def __create_order_picking_sub_map_product(self):
        sub_id = uuid4()
        m2m_obj_arr = []
        pickup_quantity = 0
        for m2m_obj in self.order_products:
            if m2m_obj.product_quantity and isinstance(m2m_obj.product_quantity, (float, int)):
                if 1 in m2m_obj.product.product_choice:
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
                order=m2m_obj.order,
                is_promotion=m2m_obj.is_promotion,
                product_unit_price=m2m_obj.product_unit_price,
                product_tax_value=m2m_obj.product_tax_value,
                product_subtotal_price=m2m_obj.product_subtotal_price,
            )
            obj_tmp.before_save()
            if 1 in m2m_obj.product.product_choice:
                # nếu product có trong kho thì mới thêm vào picking còn delivery thì vẫn show
                m2m_obj_arr.append(obj_tmp)
            else:
                self.check_has_prod_services += 1
        return sub_id, pickup_quantity, m2m_obj_arr

    def __prepare_order_delivery_product(self):
        sub_id = uuid4()
        m2m_obj_arr = []
        delivery_quantity = 0

        for m2m_obj in self.order_products:
            if m2m_obj.product_quantity and isinstance(m2m_obj.product_quantity, float):
                delivery_quantity += m2m_obj.product_quantity

            if 1 not in m2m_obj.product.product_choice:
                self.check_has_prod_services += 1

            stock_ready = 0
            if self.config_obj.is_picking is False or self.check_has_prod_services > 0:
                stock_ready = m2m_obj.product_quantity

            obj_tmp = OrderDeliveryProduct(
                delivery_sub_id=sub_id,
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

                delivery_quantity=m2m_obj.product_quantity,
                delivered_quantity_before=0,
                remaining_quantity=m2m_obj.product_quantity,
                ready_quantity=stock_ready,
                picked_quantity=0,
                order=m2m_obj.order,
                is_promotion=m2m_obj.is_promotion,
                product_unit_price=m2m_obj.product_unit_price,
                product_tax_value=m2m_obj.product_tax_value,
                product_subtotal_price=m2m_obj.product_subtotal_price,
            )
            obj_tmp.put_backup_data()
            m2m_obj_arr.append(obj_tmp)
        return sub_id, delivery_quantity, m2m_obj_arr

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
            code=obj.code,
            pickup_quantity=pickup_quantity,
            picked_quantity_before=0,
            # remaining_quantity=0, # autofill by pickup_quantity - picked_quantity_before
            picked_quantity=0,
            pickup_data={},
            sale_order_data=obj.sale_order_data,
            ware_house=None,
            ware_house_data={},
            estimated_delivery_date=None,
            state=0,
            delivery_option=obj.delivery_option,
            remarks='',
            config_at_that_point={
                "is_picking": self.config_obj.is_picking,
                "is_partial_ship": self.config_obj.is_partial_ship
            }
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
        logistic = SaleOrderLogistic.objects.filter(sale_order=self.order_obj).first()
        state = 0
        if not self.config_obj.is_partial_ship and not self.config_obj.is_picking \
                or self.config_obj.is_partial_ship and not self.config_obj.is_picking or \
                self.check_has_prod_services:
            state = 1

        return OrderDelivery.objects.create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order=self.order_obj,
            sale_order_data={
                "id": str(self.order_obj.id),
                "title": str(self.order_obj.title),
                "code": str(self.order_obj.code),
                "shipping_address": logistic.shipping_address,
                "billing_address": logistic.billing_address,
            },
            from_picking_area='',
            customer=self.order_obj.customer,
            customer_data={
                "id": str(self.order_obj.customer_id),
                "title": str(self.order_obj.customer.name),
                "code": str(self.order_obj.customer.code),
            },
            contact=self.order_obj.contact,
            contact_data={
                "id": str(self.order_obj.contact_id),
                "title": str(self.order_obj.contact.fullname),
                "code": str(self.order_obj.contact.code),
            },
            kind_pickup=0 if self.config_obj.is_picking else 1,
            sub=None,
            delivery_option=0 if not self.config_obj.is_partial_ship else 1,
            state=state,
            delivery_quantity=delivery_quantity,
            delivered_quantity_before=0,
            remaining_quantity=delivery_quantity,
            ready_quantity=delivery_quantity if self.check_has_prod_services > 0 else 0,
            delivery_data=[],
            date_created=timezone.now()
        )

    def active(self) -> (bool, str):
        try:
            with transaction.atomic():
                if (
                        not OrderPicking.objects.filter(sale_order=self.order_obj).exists()
                        and not OrderDelivery.objects.filter(sale_order=self.order_obj).exists()
                ):
                    sub_id, delivery_quantity, _y = self.__prepare_order_delivery_product()
                    if self.config_obj.is_picking is True:
                        if self.check_has_prod_services != len(self.order_products):
                            # nếu saleorder product toàn là dịch vụ thì ko cần tạo delivery
                            self._create_order_picking()
                        obj_delivery = self._create_order_delivery(delivery_quantity=delivery_quantity)
                    else:
                        obj_delivery = self._create_order_delivery(delivery_quantity=delivery_quantity)
                        # setup SUB
                    sub_obj = OrderDeliverySub.objects.create(
                        code=obj_delivery.code,
                        tenant_id=self.tenant_id,
                        company_id=self.company_id,
                        id=sub_id,
                        order_delivery=obj_delivery,
                        date_done=None,
                        previous_step=None,
                        times=1,
                        delivery_quantity=delivery_quantity,
                        delivered_quantity_before=0,
                        remaining_quantity=delivery_quantity,
                        ready_quantity=obj_delivery.ready_quantity,
                        delivery_data=[],
                        is_updated=False,
                        state=obj_delivery.state,
                        sale_order_data=obj_delivery.sale_order_data,
                        customer_data=obj_delivery.customer_data,
                        contact_data=obj_delivery.contact_data,
                        date_created=obj_delivery.date_created,
                        config_at_that_point={
                            "is_picking": self.config_obj.is_picking,
                            "is_partial_ship": self.config_obj.is_partial_ship
                        }
                    )
                    obj_delivery.sub = sub_obj
                    obj_delivery.save(update_fields=['sub'])
                    OrderDeliveryProduct.objects.bulk_create(_y)
                    # raise ValueError('Cancel with check!')
                    if obj_delivery:
                        return True, ''
                    raise ValueError('Have exception in create picking or delivery process')
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
        sale_order=sale_order_obj,
        product__isnull=False,
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
