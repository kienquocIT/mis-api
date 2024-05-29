from apps.masterdata.saledata.models import AccountActivity
from apps.sales.acceptance.models import FinalAcceptance
from apps.sales.delivery.models import OrderPickingSub, OrderPickingProduct
from apps.sales.report.models import ReportCashflow, ReportCustomer, ReportProduct, ReportRevenue
from apps.shared import DisperseModel


class DocHandler:
    @classmethod
    def get_model(cls, app_code):
        model_cls = DisperseModel(app_model=app_code).get_model()
        if model_cls and hasattr(model_cls, 'objects'):
            return model_cls
        return None


class SOFinishHandler:
    @classmethod
    def push_product_info(cls, instance):
        for product_order in instance.sale_order_product_sale_order.all():
            if product_order.product:
                final_ratio = cls.get_final_uom_ratio(
                    product_obj=product_order.product, uom_transaction=product_order.unit_of_measure
                )
                product_order.product.save(**{
                    'update_transaction_info': True,
                    'quantity_order': product_order.product_quantity * final_ratio,
                    'update_fields': ['wait_delivery_amount', 'available_amount']
                })
        return True

    @classmethod
    def push_to_report_revenue(cls, instance):
        ReportRevenue.push_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id if instance.employee_inherit else None,
            date_approved=instance.date_approved,
            revenue=instance.indicator_revenue,
            gross_profit=instance.indicator_gross_profit,
            net_income=instance.indicator_net_income,
        )
        return True

    @classmethod
    def find_discount_diff(cls, instance):
        total_pretax = instance.total_product_pretax_amount
        total_discount = instance.total_product_discount
        total_discount_product = 0
        for so_product in instance.sale_order_product_sale_order.filter(
                is_promotion=False, is_shipping=False, is_group=False,
        ):
            price_ad = so_product.product_unit_price - so_product.product_discount_amount
            subtotal_ad = price_ad * so_product.product_quantity
            subtotal = so_product.product_unit_price * so_product.product_quantity
            total_discount_product += (subtotal - subtotal_ad)
        total_discount_diff = total_discount - total_discount_product
        return total_discount_diff / total_pretax * 100

    @classmethod
    def push_to_report_product(cls, instance):
        gross_profit_rate = 0
        net_income_rate = 0
        discount_diff_rate = cls.find_discount_diff(instance=instance)
        if instance.indicator_revenue > 0:
            gross_profit_rate = instance.indicator_gross_profit / instance.indicator_revenue
            net_income_rate = instance.indicator_net_income / instance.indicator_revenue
        for so_product in instance.sale_order_product_sale_order.filter(
                is_promotion=False, is_shipping=False, is_group=False,
        ):
            product_discount_diff = so_product.product_unit_price * discount_diff_rate / 100
            price_ad = so_product.product_unit_price - so_product.product_discount_amount - product_discount_diff
            revenue = price_ad * so_product.product_quantity
            gross_profit = revenue * gross_profit_rate
            net_income = revenue * net_income_rate
            ReportProduct.push_from_so(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                sale_order_id=instance.id,
                product_id=so_product.product_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                group_inherit_id=instance.employee_inherit.group_id if instance.employee_inherit else None,
                date_approved=instance.date_approved,
                revenue=revenue,
                gross_profit=gross_profit,
                net_income=net_income,
            )
        return True

    @classmethod
    def push_to_report_customer(cls, instance):
        ReportCustomer.push_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            customer_id=instance.customer_id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id if instance.employee_inherit else None,
            date_approved=instance.date_approved,
            revenue=instance.indicator_revenue,
            gross_profit=instance.indicator_gross_profit,
            net_income=instance.indicator_net_income,
        )
        return True

    @classmethod
    def push_to_report_cashflow(cls, instance):
        bulk_data = [ReportCashflow(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            cashflow_type=2,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id if instance.employee_inherit else None,
            due_date=payment_stage.due_date,
            value_estimate_sale=payment_stage.value_before_tax,
        ) for payment_stage in instance.payment_stage_sale_order.all()]
        ReportCashflow.push_from_so_po(bulk_data)
        return True

    @classmethod
    def push_final_acceptance_so(cls, instance):
        list_data_indicator = [
            {
                'tenant_id': instance.tenant_id,
                'company_id': instance.company_id,
                'sale_order_id': instance.id,
                'sale_order_indicator_id': so_ind.id,
                'indicator_id': so_ind.quotation_indicator_id,
                'indicator_value': so_ind.indicator_value,
                'different_value': 0 - so_ind.indicator_value,
                'rate_value': 100 if so_ind.quotation_indicator.code == 'IN0001' else 0,
                'order': so_ind.order,
                'acceptance_affect_by': 1,
            }
            for so_ind in instance.sale_order_indicator_sale_order.all()
        ]
        FinalAcceptance.push_final_acceptance(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            opportunity_id=instance.opportunity_id,
            list_data_indicator=list_data_indicator,
        )
        return True

    @classmethod
    def update_opportunity_stage_by_so(cls, instance):
        if instance.opportunity:
            instance.opportunity.save(**{
                'sale_order_status': instance.system_status,
            })
        return True

    @classmethod
    def push_to_customer_activity(cls, instance):
        if instance.customer:
            AccountActivity.push_activity(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                account_id=instance.customer_id,
                app_code=instance.__class__.get_model_code(),
                document_id=instance.id,
                title=instance.title,
                code=instance.code,
                date_activity=instance.date_approved,
                revenue=instance.indicator_revenue,
            )
        return True

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1


class DocumentChangeHandler:

    @classmethod
    def change_handle(cls, instance):
        if instance.is_change and instance.document_root_id and instance.document_change_order:
            doc_previous = cls.get_doc_previous(instance=instance)
            if doc_previous:
                # delivery
                cls.handle_delivery(instance=instance, doc_previous=doc_previous)
        return True

    @classmethod
    def get_doc_previous(cls, instance):
        data_filter = {'tenant_id': instance.tenant_id, 'company_id': instance.company_id}
        if instance.document_change_order == 1:
            data_filter.update({'id': instance.document_root_id})
        if instance.document_change_order > 1:
            data_filter.update({
                'is_change': True,
                'document_root_id': instance.document_root_id,
                'document_change_order': instance.document_change_order - 1,
            })
        model_cls = DocHandler.get_model(app_code=instance._meta.label_lower)
        if model_cls and hasattr(model_cls, 'objects'):
            return model_cls.objects.filter(**data_filter).first()
        return None

    # DELIVERY
    @classmethod
    def handle_delivery(cls, instance, doc_previous):
        instance.delivery_status = doc_previous.delivery_status
        instance.delivery_call = True
        so_data = {'id': str(instance.id), 'title': instance.title, 'code': instance.code}
        data_product_change = cls.setup_data_product_change(instance=instance, doc_previous=doc_previous)
        # picking
        cls.update_picking(
            instance=instance, doc_previous=doc_previous, so_data=so_data, data_product_change=data_product_change
        )
        # delivery
        cls.update_delivery(
            instance=instance, doc_previous=doc_previous, so_data=so_data, data_product_change=data_product_change
        )
        instance.save(update_fields=['delivery_status', 'delivery_call'])
        return True

    @classmethod
    def setup_data_product_change(cls, instance, doc_previous):
        data_product_change = {}
        for so_product in doc_previous.sale_order_product_sale_order.all():
            if so_product.product_id not in data_product_change:
                data_product_change.update({str(so_product.product_id): so_product.product_quantity})
            for so_product_change in instance.sale_order_product_sale_order.all():
                if so_product_change.product_id == so_product.product_id:
                    quantity_change = so_product_change.product_quantity - so_product.product_quantity
                    data_product_change[str(so_product.product_id)] = quantity_change
                    break
        return data_product_change

    @classmethod
    def update_picking(cls, instance, doc_previous, so_data, data_product_change):
        if hasattr(doc_previous, 'picking_of_sale_order'):  # picking
            doc_previous.picking_of_sale_order.sale_order = instance
            doc_previous.picking_of_sale_order.sale_order_data = so_data
            picking_update_fields = ['sale_order', 'sale_order_data']
            picking_sub = doc_previous.picking_of_sale_order.orderpickingsub_set.filter(**{
                'tenant_id': instance.tenant_id,
                'company_id': instance.company_id,
                'order_picking__sale_order_id': doc_previous.id,
                'state': 0,
            }).first()
            if picking_sub:
                picking_sub.sale_order_data = so_data
                picking_sub_update_fields = ['sale_order_data']
                change_quantity = cls.update_and_check_pick_product(
                    data_product_change=data_product_change, picking_sub=picking_sub,
                )
                picking_sub.pickup_quantity += change_quantity
                picking_sub.remaining_quantity += change_quantity
                picking_sub_update_fields.append('pickup_quantity')
                picking_sub_update_fields.append('remaining_quantity')
                if picking_sub.remaining_quantity == 0:
                    picking_sub.state = 1
                    picking_sub_update_fields.append('state')
                picking_sub.save(update_fields=picking_sub_update_fields)
            else:
                picking_sub = doc_previous.picking_of_sale_order.orderpickingsub_set.filter(**{
                    'tenant_id': instance.tenant_id,
                    'company_id': instance.company_id,
                    'order_picking__sale_order_id': doc_previous.id,
                    'state': 1,
                }).first()
                if picking_sub:
                    cls.create_new_picking_sub(
                        instance=picking_sub, data_product_change=data_product_change, sale_order_data=so_data
                    )
            doc_previous.picking_of_sale_order.save(update_fields=picking_update_fields)
        return True

    @classmethod
    def update_delivery(cls, instance, doc_previous, so_data, data_product_change):
        if hasattr(doc_previous, 'delivery_of_sale_order'):  # delivery
            doc_previous.delivery_of_sale_order.sale_order = instance
            doc_previous.delivery_of_sale_order.sale_order_data = so_data
            deli_update_fields = ['sale_order', 'sale_order_data']
            delivery_sub = doc_previous.delivery_of_sale_order.orderdeliverysub_set.filter(**{
                'tenant_id': instance.tenant_id,
                'company_id': instance.company_id,
                'order_delivery__sale_order_id': doc_previous.id,
                'state__in': [0, 1],
            }).first()
            if delivery_sub:
                delivery_sub.sale_order_data = so_data
                deli_sub_update_fields = ['sale_order_data']
                change_quantity = cls.update_and_check_deli_product(
                    data_product_change=data_product_change, delivery_sub=delivery_sub,
                )
                delivery_sub.delivery_quantity += change_quantity
                delivery_sub.remaining_quantity += change_quantity
                deli_sub_update_fields.append('delivery_quantity')
                deli_sub_update_fields.append('remaining_quantity')
                if delivery_sub.remaining_quantity == 0:
                    delivery_sub.state = 2
                    deli_sub_update_fields.append('state')
                    doc_previous.delivery_of_sale_order.state = 2
                    deli_update_fields.append('state')
                    instance.delivery_status = 3
                delivery_sub.save(update_fields=deli_sub_update_fields)
            doc_previous.delivery_of_sale_order.save(update_fields=deli_update_fields)
        return True

    @classmethod
    def update_and_check_deli_product(cls, data_product_change, delivery_sub):
        change_quantity = 0
        for product_deli in delivery_sub.delivery_product_delivery_sub.all():
            for key, value in data_product_change.items():
                if str(product_deli.product_id) == key:
                    product_deli.delivery_quantity += value
                    product_deli.remaining_quantity += value
                    if product_deli.remaining_quantity >= 0:
                        product_deli.save(update_fields=['delivery_quantity', 'remaining_quantity'])
                        change_quantity += value
                    break
        return change_quantity

    @classmethod
    def update_and_check_pick_product(cls, data_product_change, picking_sub):
        change_quantity = 0
        for product_pick in picking_sub.picking_product_picking_sub.all():
            for key, value in data_product_change.items():
                if str(product_pick.product_id) == key:
                    product_pick.pickup_quantity += value
                    product_pick.remaining_quantity += value
                    if product_pick.remaining_quantity >= 0:
                        product_pick.save(update_fields=['pickup_quantity', 'remaining_quantity'])
                        change_quantity += value
                    break
        return change_quantity

    @classmethod
    def create_new_picking_sub(cls, instance, data_product_change, sale_order_data):
        picking = instance.order_picking
        change_quantity = 0
        for key, value in data_product_change.items():
            change_quantity += value if value > 0 else 0
        if change_quantity > 0:
            pickup_quantity = instance.pickup_quantity + change_quantity
            picked_quantity_before = instance.picked_quantity_before + instance.picked_quantity
            remaining_quantity = pickup_quantity - picked_quantity_before
            # create new sub follow by prev sub
            new_sub = OrderPickingSub.objects.create(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                order_picking=picking,
                date_done=None,
                previous_step=instance,
                times=instance.times + 1,
                pickup_quantity=pickup_quantity,
                picked_quantity_before=picked_quantity_before,
                remaining_quantity=remaining_quantity,
                picked_quantity=0,
                pickup_data=instance.pickup_data,
                sale_order_data=sale_order_data,
                delivery_option=instance.delivery_option,
                config_at_that_point=instance.config_at_that_point,
                employee_inherit=instance.employee_inherit
            )
            picking.sub = new_sub
            picking.save(update_fields=['sub'])
            # create prod with new sub id
            obj_new_prod = []
            for product_pick in instance.picking_product_picking_sub.all():
                for key, value in data_product_change.items():
                    if str(product_pick.product_id) == key:
                        pickup_quantity = product_pick.pickup_quantity + value
                        picked_quantity_before = product_pick.picked_quantity_before + product_pick.picked_quantity
                        remaining_quantity = pickup_quantity - picked_quantity_before
                        new_item = OrderPickingProduct(
                            product_data=product_pick.product_data,
                            uom_data=product_pick.uom_data,
                            uom_id=product_pick.uom_id,
                            pickup_quantity=pickup_quantity,
                            picked_quantity_before=picked_quantity_before,
                            remaining_quantity=remaining_quantity,
                            picked_quantity=0,
                            picking_sub=new_sub,
                            product_id=product_pick.product_id,
                            order=product_pick.order
                        )
                        new_item.before_save()
                        obj_new_prod.append(new_item)
            OrderPickingProduct.objects.bulk_create(obj_new_prod)
        return True
