import json

from apps.core.attachments.models import processing_folder
from apps.core.log.models import DocumentLog
from apps.shared import DisperseModel, CustomizeEncoder


class ServiceOrderFinishHandler:

    @classmethod
    def re_processing_folder_task_files(cls, instance):
        model_application = DisperseModel(app_model='base.application').get_model()
        if model_application and hasattr(model_application, 'objects'):
            doc_app = model_application.objects.filter(app_label='task', code='opportunitytask').first()
            if doc_app:
                for work_order in instance.work_orders.all():
                    for task in work_order.tasks.all():
                        for task_attachment in task.task_attachment_file_task.all():
                            file = task_attachment.attachment
                            ServiceOrderFinishHandler.run_save_file(
                                file=file, task_id=task.id, doc_app=doc_app
                            )
        return True

    @classmethod
    def run_save_file(cls, file, task_id, doc_app):
        if file:
            if file.folder:
                file.folder.delete()
            folder_obj = processing_folder(doc_id=task_id, doc_app=doc_app)
            if folder_obj:
                file.folder = folder_obj
                file.save(update_fields=['folder'])
        return True

    @classmethod
    def save_log_snapshot(cls, instance):
        service_order_detail_json = cls.get_service_order_detail_json(instance)
        doc_log = DocumentLog.objects.create(
            tenant=instance.tenant,
            company=instance.company,
            date_created=instance.date_created,
            snapshot=json.loads(json.dumps(
                        service_order_detail_json,
                        cls=CustomizeEncoder
                    )),
            app_model_code='serviceorder',
            app_id=str(instance.id).replace('-', '')
        )
        return doc_log

    @classmethod
    def get_service_order_detail_json(cls, instance):
        """
        Generate complete JSON representation of a ServiceOrder instance
        matching the structure of ServiceOrderDetailSerializer

        Args:
            instance: ServiceOrder model instance

        Returns:
            dict: Complete JSON representation of the service order
        """

        # Get shipment data (containers and packages)
        shipment_list = []
        for item in instance.service_order_shipment_service_order.all():
            is_container = item.is_container
            if is_container:
                shipment_list.append({
                    'id': str(item.id),
                    'containerName': item.title,
                    'containerType': {
                        'id': str(item.container_type.id),
                        'code': item.container_type.code,
                        'title': item.container_type.title,
                    } if item.container_type else {},
                    'containerRefNumber': item.reference_number,
                    'containerWeight': item.weight,
                    'containerDimension': item.dimension,
                    'containerNote': item.description,
                    'is_container': True,
                    'order': item.order
                })
            else:
                shipment_list.append({
                    'id': str(item.id),
                    'packageName': item.title,
                    'packageType': {
                        'id': str(item.package_type.id),
                        'code': item.package_type.code,
                        'title': item.package_type.title,
                    },
                    'packageRefNumber': item.reference_number,
                    'packageWeight': item.weight,
                    'packageDimension': item.dimension,
                    'packageNote': item.description,
                    'packageContainerRef': item.reference_container,
                    'is_container': False,
                    'order': item.order
                })

        # Get attachment data
        attachment_data = [
            file_obj.get_detail()
            for file_obj in instance.attachment_m2m.all()
        ]

        # Get service detail data
        service_detail_data = []
        for service_detail in instance.service_details.all():
            service_detail_data.append({
                'id': service_detail.id,
                'title': service_detail.title,
                'code': service_detail.code,
                'product_id': service_detail.product_id if service_detail.product else None,
                'product': {
                    'id': service_detail.product.id,
                    'title': service_detail.product.title
                } if service_detail.product else None,
                'order': service_detail.order,
                'description': service_detail.description,
                'quantity': service_detail.quantity,
                'uom_title': service_detail.uom_data.get('title', ''),
                'uom_data': service_detail.uom_data,
                'service_percent': service_detail.service_percent,
                'price': service_detail.price,
                'tax_data': service_detail.tax_data,
                'tax_code': service_detail.tax_data.get('code', ''),
                'sub_total_value': service_detail.sub_total_value,
                'total_value': service_detail.total_value,
                'delivery_balance_value': service_detail.delivery_balance_value,
                'total_contribution_percent': service_detail.total_contribution_percent,
                'total_payment_percent': service_detail.total_payment_percent,
                'total_payment_value': service_detail.total_payment_value,
                'selected_attributes': service_detail.selected_attributes,
                'attributes_total_cost': service_detail.attributes_total_cost,
                'duration_id': service_detail.duration_id if service_detail.duration else None,
                'duration_unit_data': service_detail.duration_unit_data,
                'duration': service_detail.duration_value if hasattr(service_detail,
                                                                     'duration_value') and service_detail.duration else 1,
                'has_attributes': bool(service_detail.selected_attributes and service_detail.selected_attributes != {}),
            })

        # Get work order data with nested relationships
        work_order_data = []
        for work_order in instance.work_orders.all():
            # Get cost data
            cost_data = []
            for cost in work_order.work_order_costs.all():
                cost_data.append({
                    'id': cost.id,
                    'order': cost.order,
                    'title': cost.title,
                    'description': cost.description,
                    'quantity': cost.quantity,
                    'expense_data': {
                        'id': cost.expense_item.id,
                        'title': cost.expense_item.title,
                        'code': cost.expense_item.code,
                    } if cost.expense_item else {},
                    'expense_item_id': cost.expense_item.id if cost.expense_item else None,
                    'unit_cost': cost.unit_cost,
                    'currency_id': cost.currency_id,
                    'tax_id': cost.tax_id,
                    'total_value': cost.total_value,
                    'exchanged_total_value': cost.exchanged_total_value,
                })

            # Get contribution data
            product_contribution_data = []
            for contribution in work_order.work_order_contributions.all():
                product_contribution_data.append({
                    'id': contribution.id,
                    'service_id': contribution.service_detail_id,
                    'order': contribution.order,
                    'title': contribution.title,
                    'is_selected': contribution.is_selected,
                    'contribution_percent': contribution.contribution_percent,
                    'balance_quantity': contribution.balance_quantity,
                    'delivered_quantity': contribution.delivered_quantity,
                    'unit_cost': contribution.unit_cost,
                    'total_cost': contribution.total_cost,
                    'has_package': contribution.has_package,
                    'package_data': contribution.package_data,
                })

            # Get task data
            task_data = []
            for work_order_task in work_order.service_order_work_order_task_wo.all():
                if work_order_task.task:
                    task_data.append({
                        'id': str(work_order_task.task_id),
                        'title': work_order_task.task.title,
                        'employee_created': work_order_task.task.employee_created.get_detail_minimal()
                        if work_order_task.task.employee_created else {},
                        'employee_inherit': work_order_task.task.employee_inherit.get_detail_minimal()
                        if work_order_task.task.employee_inherit else {},
                        'percent_completed': work_order_task.task.percent_completed,
                    })
                else:
                    task_data.append({})

            work_order_data.append({
                'id': work_order.id,
                'title': work_order.title,
                'code': work_order.code,
                'product_id': work_order.product_id if work_order.product else None,
                'product': {
                    'id': work_order.product.id,
                    'name': work_order.product.title
                } if work_order.product else None,
                'order': work_order.order,
                'start_date': work_order.start_date,
                'end_date': work_order.end_date,
                'is_delivery_point': work_order.is_delivery_point,
                'quantity': work_order.quantity,
                'unit_cost': work_order.unit_cost,
                'total_value': work_order.total_value,
                'work_status': work_order.work_status,
                'cost_data': cost_data,
                'product_contribution_data': product_contribution_data,
                'task_data': task_data,
            })

        # Get payment data with nested details and reconciles
        payment_data = []
        for payment in instance.payments.all():
            payment_detail_data = []

            for detail in payment.payment_details.all():
                # Get reconcile data for each payment detail
                reconcile_data = []
                for reconcile in detail.payment_detail_reconciles.all():
                    reconcile_data.append({
                        'id': reconcile.id,
                        'advance_payment_detail_id': reconcile.advance_payment_detail_id,
                        'advance_payment_id': reconcile.advance_payment_detail.service_order_payment.id
                        if reconcile.advance_payment_detail.service_order_payment else None,
                        'payment_detail_id': reconcile.payment_detail_id,
                        'service_id': reconcile.service_detail_id if reconcile.service_detail else None,
                        'installment': reconcile.installment,
                        'total_value': reconcile.total_value,
                        'reconcile_value': reconcile.reconcile_value,
                    })

                payment_detail_data.append({
                    'id': detail.id,
                    'service_id': detail.service_detail_id,
                    'title': detail.title,
                    'sub_total_value': detail.sub_total_value,
                    'payment_percent': detail.payment_percent,
                    'payment_value': detail.payment_value,
                    'total_reconciled_value': detail.total_reconciled_value,
                    'issued_value': detail.issued_value,
                    'balance_value': detail.balance_value,
                    'tax_value': detail.tax_value,
                    'tax_data': detail.service_detail.tax_data if payment.is_invoice_required else None,
                    'reconcile_value': detail.reconcile_value,
                    'receivable_value': detail.receivable_value,
                    'reconcile_data': reconcile_data,
                })

            payment_data.append({
                'id': str(payment.id),
                'installment': payment.installment,
                'description': payment.description,
                'payment_type': payment.payment_type,
                'is_invoice_required': payment.is_invoice_required,
                'payment_value': payment.payment_value,
                'tax_value': payment.tax_value,
                'reconcile_value': payment.reconcile_value,
                'receivable_value': payment.receivable_value,
                'due_date': payment.due_date,
                'payment_detail_data': payment_detail_data,
            })

        # Get expenses data
        expenses_data = []
        for item in instance.service_order_expense_service_order.all():
            expenses_data.append({
                'id': str(item.id),
                'title': item.title,
                'expense_item_data': item.expense_item_data,
                'uom_data': item.uom_data,
                'quantity': item.quantity,
                'expense_price': item.expense_price,
                'tax_data': item.tax_data,
                'expense_subtotal_price': item.expense_subtotal_price
            })

        # Get opportunity data
        opportunity_data = {}
        if instance.opportunity:
            opportunity_data = {
                'id': instance.opportunity_id,
                'title': instance.opportunity.title,
                'code': instance.opportunity.code,
                'customer': instance.customer_data,
                'is_deal_close': instance.opportunity.is_deal_close,
            }

        # Get employee inherit data
        employee_inherit_data = {}
        if instance.employee_inherit:
            employee_inherit_data = instance.employee_inherit.get_detail_minimal()

        # Build and return the complete JSON structure
        return {
            'opportunity': opportunity_data,
            'employee_inherit': employee_inherit_data,
            'id': str(instance.id),
            'code': instance.code,
            'title': instance.title,
            'date_created': instance.date_created,
            'customer_data': instance.customer_data,
            'start_date': instance.start_date,
            'end_date': instance.end_date,
            'shipment': shipment_list,
            'attachment': attachment_data,
            'service_detail_data': service_detail_data,
            'work_order_data': work_order_data,
            'payment_data': payment_data,
            'expenses_data': expenses_data,
            'exchange_rate_data': instance.exchange_rate_data,

            # Financial totals
            'total_product_pretax_amount': instance.total_product_pretax_amount,
            'total_product_tax': instance.total_product_tax,
            'total_product': instance.total_product,
            'total_product_revenue_before_tax': instance.total_product_revenue_before_tax,

            'total_expense_pretax_amount': instance.total_expense_pretax_amount,
            'total_expense_tax': instance.total_expense_tax,
            'total_expense': instance.total_expense,

            # Indicators
            'service_order_indicators_data': instance.service_order_indicators_data,
            'indicator_revenue': instance.indicator_revenue,
            'indicator_gross_profit': instance.indicator_gross_profit,
            'indicator_net_income': instance.indicator_net_income,
        }