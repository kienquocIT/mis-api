from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from celery import shared_task

from apps.core.process.utils import ProcessRuntimeControl
from apps.sales.delivery.models import (
    DeliveryConfig,
    OrderPicking, OrderPickingSub, OrderPickingProduct,
    OrderDelivery, OrderDeliveryProduct, OrderDeliverySub,
    OrderDeliveryProductAsset, OrderDeliveryProductTool
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
            estimated_delivery_date=None,
            remarks="",
            process_id=None,
    ):
        if order_obj:
            self.order_obj = order_obj
            self.order_products = order_products
            self.config_obj = delivery_config_obj

            self.estimated_delivery_date = estimated_delivery_date
            self.remarks = remarks
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

    @classmethod
    def append_depreciation_data(cls, cost_product):
        data_json = {}
        if cost_product:
            data_json.update({
                'product_depreciation_subtotal': cost_product.product_depreciation_subtotal,
                'product_depreciation_price': cost_product.product_depreciation_price,
                'product_depreciation_method': cost_product.product_depreciation_method,
                'product_depreciation_adjustment': cost_product.product_depreciation_adjustment,
                'product_depreciation_time': cost_product.product_depreciation_time,
                'product_depreciation_start_date': str(cost_product.product_depreciation_start_date),
                'product_depreciation_end_date': str(cost_product.product_depreciation_end_date),
                'product_lease_start_date': str(cost_product.product_lease_start_date),
                'product_lease_end_date': str(cost_product.product_lease_end_date),

                'depreciation_data': cost_product.depreciation_data,
            })
        return data_json

    def setup_lease_offset_kwargs(self, m2m_obj, result):
        if m2m_obj.product and m2m_obj.offset:
            cost_product = m2m_obj.offset.lease_order_cost_offset.filter(
                lease_order=self.order_obj, product=m2m_obj.product
            ).first()
            if cost_product:
                result.update({
                    'product_cost': cost_product.product_cost_price,
                    'product_subtotal_cost': cost_product.product_subtotal_price,
                    'product_convert_into': cost_product.product_convert_into,
                    'asset_type_data': cost_product.asset_type_data,
                    'asset_group_manage_data': cost_product.asset_group_manage_data,
                    'asset_group_using_data': cost_product.asset_group_using_data,
                    'tool_type_data': cost_product.tool_type_data,
                    'tool_group_manage_data': cost_product.tool_group_manage_data,
                    'tool_group_using_data': cost_product.tool_group_using_data,
                })
                result.update(OrderActiveDeliverySerializer.append_depreciation_data(cost_product=cost_product))
        return result

    def setup_lease_tool_kwargs(self, m2m_obj, result):
        if m2m_obj.product and m2m_obj.tool_data:
            for m2m_obj_tool in m2m_obj.lease_order_product_tool_lo_product.all():
                cost_product = m2m_obj_tool.tool.lease_order_cost_tool.filter(
                    lease_order=self.order_obj, product=m2m_obj_tool.product
                ).first()
                if cost_product:
                    for tool_data in result.get('tool_data', []):
                        tool_data.update({'uom_time_id': str(m2m_obj.uom_time_id)})
                        tool_data.update({'uom_time_data': m2m_obj.uom_time_data})
                        tool_data.update({'product_quantity_time': m2m_obj.product_quantity_time})
                        tool_data.update({'remaining_quantity': tool_data.get("product_quantity", 0)})
                        if tool_data.get('tool_id', None) == str(m2m_obj_tool.tool_id):
                            tool_data.update(OrderActiveDeliverySerializer.append_depreciation_data(
                                cost_product=cost_product
                            ))
                            break
        return result

    def setup_lease_asset_kwargs(self, m2m_obj, result):
        if m2m_obj.product and m2m_obj.asset_data:
            for m2m_obj_asset in m2m_obj.lease_order_product_asset_lo_product.all():
                cost_product = m2m_obj_asset.asset.lease_order_cost_asset.filter(
                    lease_order=self.order_obj, product=m2m_obj_asset.product
                ).first()
                if cost_product:
                    for asset_data in result.get('asset_data', []):
                        asset_data.update({'uom_time_id': str(m2m_obj.uom_time_id)})
                        asset_data.update({'uom_time_data': m2m_obj.uom_time_data})
                        asset_data.update({'product_quantity_time': m2m_obj.product_quantity_time})
                        asset_data.update({'remaining_quantity': asset_data.get("product_quantity", 0)})
                        if asset_data.get('asset_id', None) == str(m2m_obj_asset.asset_id):
                            asset_data.update(OrderActiveDeliverySerializer.append_depreciation_data(
                                cost_product=cost_product
                            ))
                            break
        return result

    def setup_product_kwargs(self, m2m_obj):
        result = {
            'product_quantity': m2m_obj.product_quantity,
            'product_quantity_time': 0,
            'product_cost': m2m_obj.product_unit_price,
            'product_subtotal_cost': m2m_obj.product_subtotal_price,
        }
        if m2m_obj._meta.label_lower == "leaseorder.leaseorderproduct":
            result.update({
                'asset_type': m2m_obj.asset_type,
                'offset': m2m_obj.offset,
                'offset_data': m2m_obj.offset_data,
                'tool_data': m2m_obj.tool_data,
                'asset_data': m2m_obj.asset_data,
                'uom_time': m2m_obj.uom_time,
                'uom_time_data': m2m_obj.uom_time_data,
                'product_quantity_time': m2m_obj.product_quantity_time,
            })
            result = self.setup_lease_offset_kwargs(m2m_obj=m2m_obj, result=result)
            result = self.setup_lease_tool_kwargs(m2m_obj=m2m_obj, result=result)
            result = self.setup_lease_asset_kwargs(m2m_obj=m2m_obj, result=result)

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
                tax=m2m_obj.tax,
                tax_data=m2m_obj.tax_data,

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
            tenant_id=self.order_obj.tenant_id if self.order_obj else None,
            company_id=self.order_obj.company_id if self.order_obj else None,
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
            estimated_delivery_date=self.estimated_delivery_date,
            state=0,
            remarks=self.remarks,
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
            tenant_id=self.order_obj.tenant_id if self.order_obj else None,
            company_id=self.order_obj.company_id if self.order_obj else None,
            id=sub_id,
            order_picking=obj,
            date_done=None,
            previous_step=None,
            times=1,
            pickup_quantity=pickup_quantity,
            picked_quantity_before=0,
            picked_quantity=0,
            pickup_data={},
            sale_order_data=obj.sale_order_data,
            ware_house=None,
            ware_house_data={},
            estimated_delivery_date=self.estimated_delivery_date,
            state=0,
            delivery_option=obj.delivery_option,
            remarks=self.remarks,
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
            tenant_id=self.order_obj.tenant_id if self.order_obj else None,
            company_id=self.order_obj.company_id if self.order_obj else None,
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
            estimated_delivery_date=self.estimated_delivery_date,
            remarks=self.remarks,
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
            tenant_id=self.order_obj.tenant_id if self.order_obj else None,
            company_id=self.order_obj.company_id if self.order_obj else None,
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
            sale_order_id=obj_delivery.sale_order_id,
            sale_order_data=obj_delivery.sale_order_data,
            lease_order_id=obj_delivery.lease_order_id,
            lease_order_data=obj_delivery.lease_order_data,
            customer_data=obj_delivery.customer_data,
            contact_data=obj_delivery.contact_data,
            estimated_delivery_date=self.estimated_delivery_date,
            remarks=self.remarks,
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
                            # nếu leaseorder thì không cần tạo picking
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
                    for delivery_product in delivery_product_list:
                        OrderDeliveryProductTool.objects.bulk_create([OrderDeliveryProductTool(
                            tenant_id=delivery_product.tenant_id, company_id=delivery_product.company_id,
                            delivery_product=delivery_product, **tool_data,
                        ) for tool_data in delivery_product.tool_data])
                        OrderDeliveryProductAsset.objects.bulk_create([OrderDeliveryProductAsset(
                            tenant_id=delivery_product.tenant_id, company_id=delivery_product.company_id,
                            delivery_product=delivery_product, **asset_data,
                        ) for asset_data in delivery_product.asset_data])

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
def task_active_delivery_from_sale_order(sale_order_id, estimated_delivery_date=None, remarks="", process_id=None):
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
            estimated_delivery_date=estimated_delivery_date,
            remarks=remarks,
            process_id=process_id,
        ).active(app_code="saleorder.saleorder")
        if state is True:
            sale_order_obj.delivery_call = True
            sale_order_obj.save(update_fields=['delivery_call'])
    return state, msg_returned


@shared_task
def task_active_delivery_from_lease_order(lease_order_id, estimated_delivery_date=None, remarks="", process_id=None):
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
            estimated_delivery_date=estimated_delivery_date,
            remarks=remarks,
            process_id=process_id,
        ).active(app_code="leaseorder.leaseorder")
        if state is True:
            lease_order_obj.delivery_call = True
            lease_order_obj.save(update_fields=['delivery_call'])
    return state, msg_returned
