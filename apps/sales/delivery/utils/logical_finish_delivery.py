from apps.masterdata.saledata.models import Product
from apps.sales.acceptance.models import FinalAcceptance


class DeliFinishHandler:

    @classmethod
    def push_product_info(cls, instance, validated_product=None):
        if not validated_product:
            for deli_product in instance.delivery_product_delivery_sub.all():
                if deli_product.product:
                    deli_product.product.save(**{
                        'update_transaction_info': True,
                        'quantity_delivery': deli_product.picked_quantity,
                        'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                    })
        else:
            for product_data in validated_product:
                if all(key in product_data for key in ('product_id', 'done')):
                    product_obj = Product.objects.filter(
                        tenant_id=instance.tenant_id, company_id=instance.company_id, id=product_data['product_id']
                    ).first()
                    if product_obj:
                        product_obj.save(**{
                            'update_transaction_info': True,
                            'quantity_delivery': product_data['done'],
                            'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                        })
        return True

    @classmethod
    def push_so_status(cls, instance):
        if instance.order_delivery.sale_order:
            # update sale order delivery_status (Partially delivered)
            if instance.order_delivery.sale_order.delivery_status in [0, 1]:
                instance.order_delivery.sale_order.delivery_status = 2
                instance.order_delivery.sale_order.save(update_fields=['delivery_status'])
            # update sale order delivery_status (Delivered)
            if instance.order_delivery.sale_order.delivery_status in [2] and instance.order_delivery.state == 2:
                instance.order_delivery.sale_order.delivery_status = 3
                instance.order_delivery.sale_order.save(update_fields=['delivery_status'])
        return True

    @classmethod
    def push_opp_stage(cls, instance):
        if instance.order_delivery.sale_order and instance.order_delivery.state == 2:
            if instance.order_delivery.sale_order.opportunity:
                instance.order_delivery.sale_order.opportunity.save(**{
                    'delivery_status': instance.order_delivery.state,
                })
        return True

    @classmethod
    def push_final_acceptance(cls, instance, validated_product):
        list_data_indicator = []
        for item in validated_product:
            # setup final acceptance
            actual_value = 0
            if all(key in item for key in ('product_id', 'delivery_data')):
                product_obj = Product.objects.filter(id=item['product_id']).first()
                if product_obj:
                    for data_deli in item['delivery_data']:
                        if all(key in data_deli for key in ('warehouse', 'stock')):
                            cost = product_obj.get_unit_cost_by_warehouse(
                                warehouse_id=data_deli.get('warehouse', None), get_type=1
                            )
                            actual_value += cost * data_deli['stock']
                    list_data_indicator.append({
                        'tenant_id': instance.tenant_id,
                        'company_id': instance.company_id,
                        'sale_order_id': instance.order_delivery.sale_order_id,
                        'delivery_sub_id': instance.id,
                        'product_id': item['product_id'],
                        'actual_value': actual_value,
                        'acceptance_affect_by': 3,
                    })
        FinalAcceptance.push_final_acceptance(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.order_delivery.sale_order_id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            opportunity_id=instance.order_delivery.sale_order.opportunity_id,
            list_data_indicator=list_data_indicator,
        )
        return True
