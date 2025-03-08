from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from celery import shared_task

from apps.core.process.utils import ProcessRuntimeControl
from apps.sales.delivery.models import (
    DeliveryConfig,
    OrderPicking, OrderPickingSub, OrderPickingProduct,
    OrderDelivery, OrderDeliveryProduct, OrderDeliverySub
)
from apps.sales.leaseorder.models import LeaseOrder, LeaseOrderProduct
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct

__all__ = [
    'task_active_delivery_from_sale_order',
    'task_active_delivery_from_lease_order',
]


class OrderActiveDeliverySerializer:
    def __init__(
            self,
            order_obj,  # SaleOrder || LeaseOrder
            order_products: list,
            delivery_config_obj: DeliveryConfig,
            process_id = None,
    ):
        if order_obj:
            self.tenant_id = order_obj.tenant_id
            self.company_id = order_obj.company_id

            self.order_obj = order_obj
            self.order_products = order_products
            self.config_obj = delivery_config_obj
        else:
            raise AttributeError('instance must be required')
        self.process_id = process_id
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

    def setup_product_kwargs(self, m2m_obj):
        result = {
            'asset_type': None,
            'offset': None,
            'offset_data': {},
            'uom_time': None,
            'uom_time_data': {},
            'product_quantity': m2m_obj.product_quantity,
            'product_quantity_new': m2m_obj.product_quantity,
            'remaining_quantity_new': m2m_obj.product_quantity,
            'product_quantity_leased': 0,
            'product_quantity_leased_data': [],
            'product_quantity_time': 0,
            'product_unit_price': m2m_obj.product_unit_price,
            'product_subtotal_price': m2m_obj.product_subtotal_price,

            'product_depreciation_subtotal': 0,
            'product_depreciation_price': 0,
            'product_depreciation_method': 0,
            'product_depreciation_adjustment': 0,
            'product_depreciation_time': 0,
            'product_depreciation_start_date': None,
            'product_depreciation_end_date': None,
        }
        if all(hasattr(m2m_obj, attr) for attr in [
            "asset_type", "offset", "offset_data",
            "product_quantity_new", "product_quantity_leased", "product_quantity_leased_data", "product_quantity_time"
        ]):
            for data in m2m_obj.product_quantity_leased_data:
                data.update({'remaining_quantity_leased': 1, 'picked_quantity': 0, 'delivery_data': []})
            result.update({
                'asset_type': m2m_obj.asset_type,
                'offset': m2m_obj.offset,
                'offset_data': m2m_obj.offset_data,
                'uom_time': m2m_obj.uom_time,
                'uom_time_data': m2m_obj.uom_time_data,
                'product_quantity_new': m2m_obj.product_quantity_new,
                'remaining_quantity_new': m2m_obj.product_quantity_new,
                'product_quantity_leased': m2m_obj.product_quantity_leased,
                'product_quantity_leased_data': m2m_obj.product_quantity_leased_data,
                'product_quantity_time': m2m_obj.product_quantity_time,
            })

            if m2m_obj.product and m2m_obj.offset:
                cost_product = m2m_obj.offset.lease_order_cost_offset.filter(
                    lease_order=self.order_obj, product=m2m_obj.product
                ).first()
                if cost_product:
                    result.update({
                        'product_unit_price': cost_product.product_cost_price,
                        'product_subtotal_price': cost_product.product_subtotal_price,

                        'product_depreciation_subtotal': cost_product.product_depreciation_subtotal,
                        'product_depreciation_price': cost_product.product_depreciation_price,
                        'product_depreciation_method': cost_product.product_depreciation_method,
                        'product_depreciation_adjustment': cost_product.product_depreciation_adjustment,
                        'product_depreciation_time': cost_product.product_depreciation_time,
                        'product_depreciation_start_date': cost_product.product_depreciation_start_date,
                        'product_depreciation_end_date': cost_product.product_depreciation_end_date,
                    })

        return result

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

            kwargs = self.setup_product_kwargs(m2m_obj=m2m_obj)

            obj_tmp = OrderDeliveryProduct(
                delivery_sub_id=sub_id,
                product=m2m_obj.product,
                product_data=m2m_obj.product_data,
                uom=m2m_obj.unit_of_measure,
                uom_data=m2m_obj.uom_data,

                delivery_quantity=m2m_obj.product_quantity,
                delivered_quantity_before=0,
                remaining_quantity=m2m_obj.product_quantity,
                ready_quantity=stock_ready,
                picked_quantity=0,
                order=m2m_obj.order,
                is_promotion=m2m_obj.is_promotion,
                product_tax_value=m2m_obj.product_tax_value,
                tenant_id=m2m_obj.tenant_id,
                company_id=m2m_obj.company_id,

                **kwargs,
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
                "opportunity": {
                    'id': str(self.order_obj.opportunity_id), 'title': self.order_obj.opportunity.title,
                    'code': self.order_obj.opportunity.code,
                } if self.order_obj.opportunity else {},
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
            picked_quantity=0,
            pickup_data={},
            employee_inherit=self.config_obj.lead_picking
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
            },
            employee_inherit=self.config_obj.lead_picking
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
        state = 0
        if not self.config_obj.is_partial_ship and not self.config_obj.is_picking \
                or self.config_obj.is_partial_ship and not self.config_obj.is_picking or \
                self.check_has_prod_services:
            state = 1

        sale_order, sale_order_data = None, {}
        lease_order, lease_order_data = None, {}
        app_code = str(self.order_obj.__class__.get_model_code())
        if app_code == "saleorder.saleorder":
            sale_order = self.order_obj
            sale_order_data = {
                "id": str(self.order_obj.id),
                "title": str(self.order_obj.title),
                "code": str(self.order_obj.code),
                "shipping_address": {
                    "id": str(self.order_obj.customer_shipping_id),
                    "address": self.order_obj.customer_shipping.full_address
                } if self.order_obj.customer_shipping else {},
                "billing_address": {
                    "id": str(self.order_obj.customer_billing_id),
                    "bill": self.order_obj.customer_billing.full_address
                } if self.order_obj.customer_billing else {},
                "opportunity": {
                    'id': str(self.order_obj.opportunity_id), 'title': self.order_obj.opportunity.title,
                    'code': self.order_obj.opportunity.code,
                } if self.order_obj.opportunity else {},
            }
        if app_code == "leaseorder.leaseorder":
            lease_order = self.order_obj
            lease_order_data = {
                "id": str(self.order_obj.id),
                "title": str(self.order_obj.title),
                "code": str(self.order_obj.code),
                "opportunity": {
                    'id': str(self.order_obj.opportunity_id), 'title': self.order_obj.opportunity.title,
                    'code': self.order_obj.opportunity.code,
                } if self.order_obj.opportunity else {},
            }

        order_delivery = OrderDelivery.objects.create(
            process_id=self.process_id,
            title=self.order_obj.title if self.order_obj else '',
            employee_created=self.order_obj.employee_created if self.order_obj else None,
            #
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            sale_order=sale_order,
            sale_order_data=sale_order_data,
            lease_order=lease_order,
            lease_order_data=lease_order_data,
            from_picking_area='',
            customer=self.order_obj.customer,
            customer_data={
                "id": str(self.order_obj.customer_id),
                "title": str(self.order_obj.customer.name),
                "code": str(self.order_obj.customer.code),
            } if self.order_obj.customer else {},
            contact=self.order_obj.contact,
            contact_data={
                "id": str(self.order_obj.contact_id),
                "title": str(self.order_obj.contact.fullname),
                "code": str(self.order_obj.contact.code),
            } if self.order_obj.contact else {},
            kind_pickup=0 if self.config_obj.is_picking else 1,
            sub=None,
            delivery_option=0 if not self.config_obj.is_partial_ship else 1,
            state=state,
            delivery_quantity=delivery_quantity,
            delivered_quantity_before=0,
            remaining_quantity=delivery_quantity,
            ready_quantity=delivery_quantity if self.check_has_prod_services > 0 else 0,
            delivery_data=[],
            date_created=timezone.now(),
            employee_inherit=self.config_obj.lead_delivery,
            system_status=1
        )
        # handle opp stage & win_rate
        if self.order_obj.opportunity:
            self.order_obj.opportunity.handle_stage_win_rate(obj=self.order_obj.opportunity)
        return order_delivery

    def _create_order_delivery_sub(self, obj_delivery, sub_id, delivery_quantity):
        sub_obj = OrderDeliverySub.objects.create(
            process=obj_delivery.process,
            process_stage_app=obj_delivery.process_stage_app,
            title=obj_delivery.title,
            employee_created=obj_delivery.employee_created,
            #
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
            lease_order_data=obj_delivery.lease_order_data,
            customer_data=obj_delivery.customer_data,
            contact_data=obj_delivery.contact_data,
            date_created=obj_delivery.date_created,
            config_at_that_point={
                "is_picking": self.config_obj.is_picking,
                "is_partial_ship": self.config_obj.is_partial_ship
            },
            system_status=obj_delivery.system_status,
            employee_inherit=self.config_obj.lead_delivery
        )
        return sub_obj

    def active(self, app_code) -> (bool, str):
        condition = False
        if app_code == "saleorder.saleorder":
            condition = (
                        not OrderPicking.objects.filter(sale_order=self.order_obj).exists()
                        and not OrderDelivery.objects.filter(sale_order=self.order_obj).exists()
                )
        if app_code == "leaseorder.leaseorder":
            condition = (not OrderDelivery.objects.filter(lease_order=self.order_obj).exists())
        try:
            with transaction.atomic():
                if condition:
                    sub_id, delivery_quantity, _y = self.__prepare_order_delivery_product()
                    if self.config_obj.is_picking is True and app_code == "saleorder.saleorder":
                        if self.check_has_prod_services != len(self.order_products):
                            # nếu saleorder product toàn là dịch vụ thì ko cần tạo picking
                            # nều leaseorder thì không cần tạo picking
                            self._create_order_picking()
                    obj_delivery = self._create_order_delivery(delivery_quantity=delivery_quantity)
                    # setup SUB
                    sub_obj = self._create_order_delivery_sub(
                        obj_delivery=obj_delivery,
                        sub_id=sub_id,
                        delivery_quantity=delivery_quantity
                    )
                    obj_delivery.sub = sub_obj
                    obj_delivery.save(update_fields=['sub'])
                    delivery_product_list = OrderDeliveryProduct.objects.bulk_create(_y)

                    # update sale order delivery_status
                    self.order_obj.delivery_status = 1
                    self.order_obj.save(update_fields=['delivery_status'])

                    # regis OrderDelivery to Process
                    if sub_obj.process:
                        ProcessRuntimeControl(process_obj=sub_obj.process).register_doc(
                            process_stage_app_obj=sub_obj.process_stage_app,
                            app_id=OrderDeliverySub.get_app_id(),
                            doc_id=sub_obj.id,
                            doc_title=sub_obj.title,
                            employee_created_id=sub_obj.employee_created_id,
                            date_created=sub_obj.date_created,
                        )

                    if obj_delivery:
                        return True, ''
                    raise ValueError('Have exception in create picking or delivery process')
                return False, 'Sale Order had exist delivery'
        except Exception as err:
            print(err)
            return False, str(err)


@shared_task
def task_active_delivery_from_sale_order(sale_order_id, process_id=None):
    state, msg_returned = False, ""
    sale_order_obj = SaleOrder.objects.filter(id=sale_order_id).first()
    if sale_order_obj:
        sale_order_products = SaleOrderProduct.objects.select_related(
            'product', 'unit_of_measure'
        ).filter(sale_order=sale_order_obj, product__isnull=False,)
        config_obj = DeliveryConfig.objects.get(company=sale_order_obj.company)
        state, msg_returned = OrderActiveDeliverySerializer(
            order_obj=sale_order_obj,
            order_products=sale_order_products,
            delivery_config_obj=config_obj,
            process_id=process_id,
        ).active(app_code="saleorder.saleorder")
        if state is True:
            sale_order_obj.delivery_call = True
            sale_order_obj.save(update_fields=['delivery_call'])
    return state, msg_returned


@shared_task
def task_active_delivery_from_lease_order(lease_order_id, process_id=None):
    state, msg_returned = False, ""
    lease_order_obj = LeaseOrder.objects.filter(id=lease_order_id).first()
    if lease_order_obj:
        lease_order_products = LeaseOrderProduct.objects.select_related(
            'product', 'unit_of_measure'
        ).filter(lease_order=lease_order_obj, product__isnull=False,)
        config_obj = DeliveryConfig.objects.get(company=lease_order_obj.company)
        state, msg_returned = OrderActiveDeliverySerializer(
            order_obj=lease_order_obj,
            order_products=lease_order_products,
            delivery_config_obj=config_obj,
            process_id=process_id,
        ).active(app_code="leaseorder.leaseorder")
        if state is True:
            lease_order_obj.delivery_call = True
            lease_order_obj.save(update_fields=['delivery_call'])
    return state, msg_returned
