from apps.masterdata.saledata.models import ExpenseItem, UnitOfMeasure, Tax
from apps.sales.serviceorder.models import (
    ServiceOrderContainer, ServiceOrderShipment, ServiceOrderExpense,
    ServiceOrderServiceDetail, ServiceOrderWorkOrder, ServiceOrderWorkOrderCost, ServiceOrderWorkOrderContribution,
    ServiceOrderPayment, ServiceOrderPaymentDetail, ServiceOrderPaymentReconcile, ServiceOrderPackage,
)


class ServiceOrderCommonFunc:
    @staticmethod
    def create_shipment(service_order_obj, shipment_data):
        bulk_info_shipment = []
        bulk_info_container = []
        ctn_shipment = 1
        ctn_order = 1
        for _, shipment_data_item in enumerate(shipment_data):
            package_type = shipment_data_item.get("package_type")
            container_type = shipment_data_item.get("container_type")

            shipment_obj = ServiceOrderShipment(
                service_order=service_order_obj,
                order=ctn_shipment,
                title=shipment_data_item.get("title", ""),
                container_type_id=container_type.get("id") if container_type else None,
                package_type_id=package_type.get("id") if package_type else None,
                company=service_order_obj.company,
                tenant=service_order_obj.tenant,
                reference_number=shipment_data_item.get("reference_number"),
                weight=shipment_data_item.get("weight", 0),
                dimension=shipment_data_item.get("dimension", 0),
                description=shipment_data_item.get("description", ""),
                reference_container=shipment_data_item.get("reference_container"),
                is_container=shipment_data_item.get("is_container", True),
            )
            bulk_info_shipment.append(shipment_obj)

            # get container
            if shipment_obj.is_container:
                bulk_info_container.append(
                    ServiceOrderContainer(
                        service_order=service_order_obj,
                        shipment=shipment_obj,
                        order=ctn_order,
                        container_type_id=container_type.get("id") if container_type else None,
                        company=service_order_obj.company,
                        tenant=service_order_obj.tenant,
                    )
                )
                ctn_order += 1
            ctn_shipment += 1

        # bulk create shipments
        ServiceOrderShipment.objects.filter(service_order=service_order_obj).delete()
        ServiceOrderShipment.objects.bulk_create(bulk_info_shipment)

        # bulk create container
        container_created = ServiceOrderContainer.objects.bulk_create(bulk_info_container)

        # create package part
        bulk_info_packages = []
        pkg_order = 1
        for _, shipment_data_item in enumerate(shipment_data):
            # get package
            if not shipment_data_item.get('is_container'):
                ctn_mapped = None
                for ctn in container_created:
                    if ctn.shipment.reference_number == shipment_data_item.get('reference_container'):
                        ctn_mapped = ctn
                if ctn_mapped:
                    bulk_info_packages.append(
                        ServiceOrderPackage(
                            service_order=service_order_obj,
                            shipment=ctn_mapped.shipment,
                            order=pkg_order,
                            package_type_id=package_type.get("id") if package_type else None,
                            container_reference_id=str(ctn_mapped.id),
                            company=service_order_obj.company,
                            tenant=service_order_obj.tenant,
                        )
                    )
                    pkg_order += 1

        # bulk create package
        ServiceOrderPackage.objects.bulk_create(bulk_info_packages)
        return True

    @staticmethod
    def create_expense(service_order_obj, expense_data):
        bulk_info_expense = []

        for expense_data_item in expense_data:
            # Resolve UUID → instance
            expense_item_id = expense_data_item.get("expense_item")
            uom_id = expense_data_item.get("uom")
            tax_id = expense_data_item.get("tax")

            expense_item_obj = ExpenseItem.objects.filter(id=expense_item_id).first() if expense_item_id else None
            uom_obj = UnitOfMeasure.objects.filter(id=uom_id).first() if uom_id else None
            tax_obj = Tax.objects.filter(id=tax_id).first() if tax_id else None

            expense_obj = ServiceOrderExpense(
                service_order=service_order_obj,
                title=expense_data_item.get("title"),
                expense_item=expense_item_obj,
                expense_item_data={
                    "id": str(expense_item_obj.id),
                    "code": expense_item_obj.code,
                    "title": expense_item_obj.title,
                } if expense_item_obj else {},
                uom=uom_obj,
                uom_data={
                    "id": str(uom_obj.id),
                    "code": uom_obj.code,
                    "title": uom_obj.title,
                } if uom_obj else {},
                quantity=expense_data_item.get("quantity", 0),
                expense_price=expense_data_item.get("expense_price", 0),
                tax=tax_obj,
                tax_data={
                    "id": str(tax_obj.id),
                    "code": tax_obj.code,
                    "title": tax_obj.title,
                    "rate": tax_obj.rate,
                } if tax_obj else {},
                subtotal_price=expense_data_item.get("subtotal_price", 0),
                company=service_order_obj.company,
                tenant=service_order_obj.tenant,
            )

            bulk_info_expense.append(expense_obj)

        # Replace old expenses
        ServiceOrderExpense.objects.filter(service_order=service_order_obj).delete()
        ServiceOrderExpense.objects.bulk_create(bulk_info_expense)

        return True

    @staticmethod
    def create_service_detail(service_order, service_detail_data):
        service_order_id = service_order.id
        bulk_data = []
        service_detail_id_map = {}
        for service_detail in service_detail_data:
            bulk_data.append(
                ServiceOrderServiceDetail(
                    service_order_id=service_order_id,
                    title=service_detail.get('title'),
                    code=service_detail.get('code'),
                    product_id=service_detail.get('product').id if service_detail.get('product') else None,
                    order=service_detail.get('order'),
                    description=service_detail.get('description'),
                    quantity=service_detail.get('quantity'),
                    uom_id=service_detail.get('uom_data', {}).get('id'),
                    uom_data=service_detail.get('uom_data'),
                    price=service_detail.get('price'),
                    tax_id=service_detail.get('tax_data', {}).get('id'),
                    tax_data=service_detail.get('tax_data'),
                    sub_total_value=service_detail.get('sub_total_value'),
                    total_value=service_detail.get('total_value'),
                    delivery_balance_value=service_detail.get('delivery_balance_value'),
                    total_contribution_percent=service_detail.get('total_contribution_percent'),
                    total_payment_percent=service_detail.get('total_payment_percent'),
                    total_payment_value=service_detail.get('total_payment_value'),
                )
            )

        service_order.service_details.all().delete()
        created_service_details = ServiceOrderServiceDetail.objects.bulk_create(bulk_data)

        for frontend_data, backend_data in zip(service_detail_data, created_service_details):
            temp_id = frontend_data.get('id')
            if temp_id:
                service_detail_id_map[temp_id] = backend_data.id

        return service_detail_id_map

    @staticmethod
    def create_work_order(service_order, work_order_data, service_detail_id_map):
        service_order_id = service_order.id
        bulk_data = []
        for work_order in work_order_data:
            instance = ServiceOrderWorkOrder(
                service_order_id=service_order_id,
                title=work_order.get('title'),
                code=work_order.get('code'),
                product_id=work_order.get('product').id if work_order.get('product') else None,
                order=work_order.get('order'),
                start_date=work_order.get('start_date'),
                end_date=work_order.get('end_date'),
                is_delivery_point=work_order.get('is_delivery_point'),
                quantity=work_order.get('quantity'),
                unit_cost=work_order.get('unit_cost'),
                total_value=work_order.get('total_value'),
                work_status=work_order.get('work_status'),
            )
            bulk_data.append(instance)

        service_order.work_orders.all().delete()
        created_work_orders = ServiceOrderWorkOrder.objects.bulk_create(bulk_data)

        for instance, raw_data in zip(created_work_orders, work_order_data):
            ServiceOrderCommonFunc.create_work_order_cost(instance, raw_data.get('cost_data', []))
            ServiceOrderCommonFunc.create_work_order_contribution(
                instance,
                raw_data.get('product_contribution', []),
                service_detail_id_map
            )

    @staticmethod
    def create_work_order_cost(work_order, cost_data):
        bulk_data = []
        for cost in cost_data:
            bulk_data.append(
                ServiceOrderWorkOrderCost(
                    work_order=work_order,
                    order=cost.get('order', 0),
                    title=cost.get('title', ''),
                    description=cost.get('description', ''),
                    quantity=cost.get('quantity', 0),
                    unit_cost=cost.get('unit_cost', 0),
                    currency_id=cost.get('currency_id'),
                    tax_id=cost.get('tax_id'),
                    total_value=cost.get('total_value', 0),
                    exchanged_total_value=cost.get('exchanged_total_value', 0),
                )
            )

        work_order.work_order_costs.all().delete()
        ServiceOrderWorkOrderCost.objects.bulk_create(bulk_data)

    @staticmethod
    def create_work_order_contribution(work_order, contribution_data, service_detail_id_map):
        bulk_data = []
        for contribution in contribution_data:
            temp_id = contribution.get('service_id')
            service_detail_uuid = service_detail_id_map.get(temp_id)
            if not service_detail_uuid:
                return
            bulk_data.append(
                ServiceOrderWorkOrderContribution(
                    work_order=work_order,
                    service_detail_id=service_detail_uuid,
                    order=contribution.get('order', 0),
                    title=contribution.get('title', ''),
                    is_selected=contribution.get('is_selected', False),
                    contribution_percent=contribution.get('contribution_percent', 0),
                    balance_quantity=contribution.get('balance_quantity', 0),
                    delivered_quantity=contribution.get('delivered_quantity', 0),
                )
            )
        work_order.work_order_contributions.all().delete()
        ServiceOrderWorkOrderContribution.objects.bulk_create(bulk_data)

    @staticmethod
    def create_payment(service_order, payment_data, service_detail_id_map):
        service_order_id = service_order.id
        bulk_data = []
        for payment in payment_data:
            bulk_data.append(
                ServiceOrderPayment(
                    service_order_id=service_order_id,
                    installment=payment.get('installment', 0),
                    description=payment.get('description', ''),
                    payment_type=payment.get('payment_type', 1),
                    is_invoice_required=payment.get('is_invoice_required', False),
                    payment_value=payment.get('payment_value', 0),
                    tax_value=payment.get('tax_value', 0),
                    reconcile_value=payment.get('reconcile_value', 0),
                    receivable_value=payment.get('receivable_value', 0),
                    due_date=payment.get('due_date'),
                )
            )
        service_order.payments.all().delete()
        created_payments = ServiceOrderPayment.objects.bulk_create(bulk_data)
        payment_detail_id_map = {}
        for instance, raw_data in zip(created_payments, payment_data):
            payment_detail_id_map.update(
                ServiceOrderCommonFunc.create_payment_detail(
                    instance,
                    raw_data.get('payment_detail_data', []),
                    service_detail_id_map
                )
            )

        for instance, raw_data in zip(created_payments, payment_data):
            ServiceOrderCommonFunc.create_reconcile_data(
                raw_data.get('reconcile_data', []),
                payment_detail_id_map,
                service_detail_id_map
            )

    @staticmethod
    def create_payment_detail(payment, payment_detail_data, service_detail_id_map):
        bulk_data = []
        payment_detail_id_map = {}
        for payment_detail in payment_detail_data:
            temp_id = payment_detail.get('service_id')
            payment_detail_uuid = service_detail_id_map.get(temp_id)
            if not payment_detail_uuid:
                return {}
            bulk_data.append(
                ServiceOrderPaymentDetail(
                    service_order_payment=payment,
                    service_detail_id=payment_detail_uuid,
                    title=payment_detail.get("title", ""),
                    sub_total_value=payment_detail.get("sub_total_value", 0),
                    payment_percent=payment_detail.get("payment_percent", 0),
                    payment_value=payment_detail.get("payment_value", 0),
                    total_reconciled_value=payment_detail.get("total_reconciled_value", 0),
                    issued_value=payment_detail.get("issued_value", 0),
                    balance_value=payment_detail.get("balance_value", 0),
                    tax_value=payment_detail.get("tax_value", 0),
                    reconcile_value=payment_detail.get("reconcile_value", 0),
                    receivable_value=payment_detail.get("receivable_value", 0),
                )
            )

        created_payment_details = ServiceOrderPaymentDetail.objects.bulk_create(bulk_data)

        for frontend_data, backend_data in zip(payment_detail_data, created_payment_details):
            temp_id = frontend_data.get('id')
            if temp_id:
                payment_detail_id_map[temp_id] = backend_data.id

        return payment_detail_id_map

    @staticmethod
    def create_reconcile_data(reconcile_data, payment_detail_id_map, service_detail_id_map):
        bulk_data = []
        for reconcile in reconcile_data:
            temp_service_id = reconcile.get('service_id')
            service_uuid = service_detail_id_map.get(temp_service_id)
            if not service_uuid:
                return

            temp_advance_payment_detail_id = reconcile.get('advance_payment_detail_id')
            advance_payment_detail_uuid = payment_detail_id_map.get(temp_advance_payment_detail_id)
            if not advance_payment_detail_uuid:
                return

            temp_payment_detail_id = reconcile.get('payment_detail_id')
            payment_detail_uuid = payment_detail_id_map.get(temp_payment_detail_id)
            if not payment_detail_uuid:
                return

            bulk_data.append(
                ServiceOrderPaymentReconcile(
                    advance_payment_detail_id=advance_payment_detail_uuid,
                    payment_detail_id=payment_detail_uuid,
                    service_detail_id=service_uuid,
                    installment=reconcile.get('installment', 0),
                    total_value=reconcile.get('total_value', 0),
                    reconcile_value=reconcile.get('reconcile_value', 0)
                )
            )
        ServiceOrderPaymentReconcile.objects.bulk_create(bulk_data)
