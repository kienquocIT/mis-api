from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models import ExpenseItem, UnitOfMeasure, Tax, Product, Currency
from apps.sales.serviceorder.models import (
    ServiceOrderShipment, ServiceOrderExpense, ServiceOrderServiceDetail, ServiceOrderWorkOrder, ServiceOrderPayment,
    ServiceOrder, ServiceOrderContainer, ServiceOrderPackage, ServiceOrderWorkOrderCost, ServiceOrderWorkOrderTask,
    ServiceOrderPaymentReconcile, ServiceOrderPaymentDetail, ServiceOrderWorkOrderContribution,
)
from apps.shared import SVOMsg, AbstractDetailSerializerModel

__all__ = [
    'ServiceOrderServiceDetailSerializer',
    'ServiceOrderWorkOrderSerializer',
    'ServiceOrderShipmentSerializer',
    'ServiceOrderExpenseSerializer',
    'ServiceOrderPaymentSerializer',
    'ServiceOrderDetailDashboardSerializer',
    'ServiceOrderCommonFunc',
    'SVODeliveryWorkOrderDetailSerializer'
]


# SERVICE DETAIL
class ServiceOrderServiceDetailSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    uom = serializers.UUIDField(required=False, allow_null=True)
    tax = serializers.UUIDField(required=False, allow_null=True)
    id = serializers.CharField(required=False)
    duration = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = ServiceOrderServiceDetail
        fields = (
            'id',
            'product',
            'order',
            'code',
            'title',
            'description',
            'quantity',
            'uom',
            'uom_data',
            'price',
            'tax',
            'tax_data',
            'sub_total_value',
            'total_value',
            'delivery_balance_value',
            'total_contribution_percent',
            'total_payment_percent',
            'total_payment_value',
            'selected_attributes',
            'attributes_total_cost',
            'duration_value',
            'duration',
            'duration_unit_data'
        )

    @classmethod
    def validate_product(cls, value):
        if value:
            try:
                product = Product.objects.get_on_company(id=value)
                return product
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': _('Product does not exist')})
        return None

    @classmethod
    def validate_uom(cls, value):
        if value:
            try:
                uom = UnitOfMeasure.objects.get_on_company(id=value)
                return uom
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'uom': _('Unit of Measure does not exist')})
        raise serializers.ValidationError({'uom': _('Unit of Measure is required')})

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                tax = Tax.objects.get_on_company(id=value)
                return tax
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'tax': _('Tax does not exist')})
        raise serializers.ValidationError({'tax': _('Tax is required')})

    @classmethod
    def validate_duration(cls, value):
        if value:
            try:
                duration = UnitOfMeasure.objects.get_on_company(id=value)
                return duration
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'duration': _('Duration does not exist')})
        raise serializers.ValidationError({'duration': _('Duration is required')})


# WORK ORDER
class ServiceOrderWorkOrderSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(allow_null=True, required=False)
    code = serializers.CharField(allow_blank=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    cost_data = serializers.JSONField()
    product_contribution = serializers.JSONField()

    class Meta:
        model = ServiceOrderWorkOrder
        fields = (
            'product',
            'order',
            'code',
            'title',
            'start_date',
            'end_date',
            'is_delivery_point',
            'quantity',
            'unit_cost',
            'total_value',
            'work_status',
            'cost_data',
            'product_contribution',
            'task_data',
        )

    @classmethod
    def validate_product(cls, value):
        if value:
            try:
                product = Product.objects.get_on_company(id=value)
                return product
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': _('Product does not exist')})
        return None

    @classmethod
    def validate_cost_data(cls, cost_data):
        for cost in cost_data:
            currency_id = cost.get('currency_id', None)
            if currency_id:
                try:
                    Currency.objects.get(id=currency_id)
                except Currency.DoesNotExist:
                    raise serializers.ValidationError(
                        {'work_order_cost': _('Currency of work order cost does not exist')}
                    )
            else:
                raise serializers.ValidationError({'work_order_cost': _('Currency of work order cost is missing')})

            tax_id = cost.get('tax_id', None)
            if tax_id:
                try:
                    Tax.objects.get(id=tax_id)
                except Tax.DoesNotExist:
                    raise serializers.ValidationError({'work_order_cost': _('Tax of work order cost does not exist')})
            else:
                raise serializers.ValidationError({'work_order_cost': _('Tax of work order cost is missing')})
        return cost_data


# SHIPMENT
class ServiceOrderShipmentSerializer(serializers.ModelSerializer):
    container_type = serializers.JSONField(required=False, allow_null=True)
    package_type = serializers.JSONField(required=False, allow_null=True)
    id = serializers.CharField(required=False)

    def validate(self, validate_data):
        if validate_data.get('is_container', True):
            if not validate_data.get('title'):
                raise serializers.ValidationError({'container name': SVOMsg.CONTAINER_NAME_NOT_EXIST})
            if not validate_data.get('reference_number'):
                raise serializers.ValidationError({'Container Reference Number': SVOMsg.CONTAINER_REF_NOT_EXIST})
        else:
            if not validate_data.get('title'):
                raise serializers.ValidationError({'Package Name': SVOMsg.PACKAGE_NAME_NOT_EXIST})
            if not validate_data.get('reference_container'):
                raise serializers.ValidationError({'Package Reference Container': SVOMsg.PACKAGE_REF_NOT_EXIST})

        return validate_data

    class Meta:
        model = ServiceOrderShipment
        fields = (
            'id',
            'code',
            'title',
            'order',
            'reference_number',
            'weight',
            'dimension',
            'description',
            'reference_container',
            'is_container',
            'container_type',
            'package_type'
        )


# EXPENSE
class ServiceOrderExpenseSerializer(serializers.ModelSerializer):
    expense_item = serializers.UUIDField()
    uom = serializers.UUIDField()
    tax = serializers.UUIDField(required=False, allow_null=True)

    @staticmethod
    def validate_expense_item(value):
        if not ExpenseItem.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.EXPENSE_ITEM_NOT_EXIST)
        return value

    @staticmethod
    def validate_uom(value):
        if not UnitOfMeasure.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.UOM_NOT_EXIST)
        return value

    @staticmethod
    def validate_tax(value):
        if value and not Tax.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.TAX_NOT_EXIST)
        return value

    class Meta:
        model = ServiceOrderExpense
        fields = (
            "id",
            "code",
            "title",
            "expense_item",
            "uom",
            "quantity",
            "expense_price",
            "tax",
            "subtotal_price",
        )


# PAYMENT
class ServiceOrderPaymentSerializer(serializers.ModelSerializer):
    payment_detail_data = serializers.JSONField(required=False)
    reconcile_data = serializers.JSONField()

    class Meta:
        model = ServiceOrderPayment
        fields = (
            'installment',
            'description',
            'payment_type',
            'is_invoice_required',
            'payment_value',
            'tax_value',
            'reconcile_value',
            'receivable_value',
            'due_date',
            'payment_detail_data',
            'reconcile_data'
        )


# DASHBOARD
class ServiceOrderDetailDashboardSerializer(AbstractDetailSerializerModel):
    contract_value = serializers.SerializerMethodField()
    contract_value_delivered = serializers.SerializerMethodField()
    service_order_detail_list = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'code',
            'title',
            'customer_data',
            'start_date',
            'end_date',
            'contract_value',
            'contract_value_delivered',
            'service_order_detail_list'
        )

    @classmethod
    def get_contract_value(cls, obj):
        return sum(list(obj.service_details.all().values_list('total_value', flat=True)))

    @classmethod
    def get_contract_value_delivered(cls, obj):
        return sum(list(obj.service_details.all().values_list('delivery_balance_value', flat=True)))

    @classmethod
    def get_service_order_detail_list(cls, obj):
        service_order_detail_list = []
        for item in obj.service_details.all():
            service_order_detail_list.append(
                {
                    'id': item.id,
                    'product_data': {
                        'id': str(item.product_id),
                        'code': item.product.code,
                        'title': item.product.title
                    } if item.product else {},
                    'description': item.description,
                    'total_value': item.total_value,
                    'total_contribution_percent': item.total_contribution_percent,
                    'work_order_contribute_list': [{
                        'id': str(wo_ctb_item.id),
                        'is_selected': wo_ctb_item.is_selected,
                        'title': wo_ctb_item.title,
                        'contribution_percent': wo_ctb_item.contribution_percent,
                        'balance_quantity': wo_ctb_item.balance_quantity,
                        'delivered_quantity': wo_ctb_item.delivered_quantity,
                        'work_order_data': {
                            'id': str(wo_ctb_item.work_order.id),
                            'code': wo_ctb_item.work_order.code,
                            'title': wo_ctb_item.work_order.title,
                            'start_date': wo_ctb_item.work_order.start_date,
                            'end_date': wo_ctb_item.work_order.end_date,
                            'is_delivery_point': wo_ctb_item.work_order.is_delivery_point,
                            'quantity': wo_ctb_item.work_order.quantity,
                            'unit_cost': wo_ctb_item.work_order.unit_cost,
                            'total_value': wo_ctb_item.work_order.total_value,
                            'work_status': wo_ctb_item.work_order.work_status,
                            'task_data_list': [{
                                'id': str(wo_task_item.task.id),
                                'code': wo_task_item.task.code,
                                'title': wo_task_item.task.title,
                                'remark': wo_task_item.task.remark,
                                'assignee_data': wo_task_item.task.employee_inherit.get_detail_with_group()
                                if wo_task_item.task.employee_inherit else {},
                                'percent_completed': wo_task_item.task.percent_completed,
                            } for wo_task_item in wo_ctb_item.work_order.service_order_work_order_task_wo.all()]
                        } if wo_ctb_item.work_order else {},
                    } for wo_ctb_item in item.service_detail_contributions.filter(
                        is_selected=True
                    ).order_by("work_order__order")]
                }
            )
        return service_order_detail_list


class ServiceOrderCommonFunc:
    @staticmethod
    def build_shipments(service_order_obj, shipment_data):
        bulk_info_shipment, bulk_info_container = [], []
        ctn_shipment, ctn_order = 1, 1

        for shipment_data_item in shipment_data:
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
        return bulk_info_shipment, bulk_info_container

    @staticmethod
    def build_packages(service_order_obj, shipment_data, container_created):
        bulk_info_packages = []
        pkg_order = 1
        for shipment_data_item in shipment_data:
            package_type = shipment_data_item.get("package_type")
            if not shipment_data_item.get('is_container'):
                ctn_mapped = next(
                    (ctn for ctn in container_created if
                     ctn.shipment.reference_number == shipment_data_item.get('reference_container')),
                    None
                )
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
        return bulk_info_packages

    @staticmethod
    def create_shipment(service_order_obj, shipment_data):
        shipment_map_id = {}

        # build shipment and containers
        bulk_info_shipment, bulk_info_container = ServiceOrderCommonFunc.build_shipments(
            service_order_obj, shipment_data
        )
        ServiceOrderShipment.objects.filter(service_order=service_order_obj).delete()
        created_shipments = ServiceOrderShipment.objects.bulk_create(bulk_info_shipment)
        container_created = ServiceOrderContainer.objects.bulk_create(bulk_info_container)

        # Map temp id
        for shipment_data_item, created_shipment_item in zip(shipment_data, created_shipments):
            temp_id = shipment_data_item.get('id')
            if temp_id:
                shipment_map_id[temp_id] = created_shipment_item.id

        # build packages
        bulk_info_packages = ServiceOrderCommonFunc.build_packages(service_order_obj, shipment_data, container_created)
        ServiceOrderPackage.objects.bulk_create(bulk_info_packages)

        return shipment_map_id

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
                subtotal_price=expense_data_item.get("quantity", 0) * expense_data_item.get("expense_price", 0),
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
            product_obj = service_detail.get('product')
            duration_obj = service_detail.get('duration')

            # Prepare duration_unit_data based on duration object
            duration_unit_data = {}
            if duration_obj:
                duration_unit_data = {
                    "id": str(duration_obj.id),
                    "code": duration_obj.code,
                    "title": duration_obj.title,
                }

            bulk_data.append(
                ServiceOrderServiceDetail(
                    service_order_id=service_order_id,
                    title=service_detail.get('title'),
                    code=service_detail.get('code'),
                    product=product_obj,
                    product_data={
                        "id": str(product_obj.id),
                        "code": product_obj.code,
                        "title": product_obj.title,
                        "description": product_obj.description,
                    } if product_obj else {},
                    order=service_detail.get('order'),
                    description=service_detail.get('description'),
                    quantity=service_detail.get('quantity'),
                    uom=service_detail.get('uom'),
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
                    remain_for_purchase_request=service_detail.get('quantity'),
                    selected_attributes=service_detail.get('selected_attributes', {}),
                    attributes_total_cost=service_detail.get('attributes_total_cost', 0),
                    duration=duration_obj,
                    duration_value=service_detail.get('duration_value', 0),
                    duration_unit_data=duration_unit_data or service_detail.get('duration_unit_data', {}),
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
    def create_work_order(service_order, work_order_data, service_detail_id_map, shipment_map_id):
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
                task_data=work_order.get('task_data', []),
                tenant_id=service_order.tenant_id,
                company_id=service_order.company_id,
            )
            bulk_data.append(instance)

        service_order.work_orders.all().delete()
        created_work_orders = ServiceOrderWorkOrder.objects.bulk_create(bulk_data)
        for created_work_order in created_work_orders:
            ServiceOrderWorkOrderTask.objects.bulk_create(
                [ServiceOrderWorkOrderTask(
                    work_order=created_work_order,
                    task_id=task_data.get('id', None),
                    tenant_id=created_work_order.tenant_id,
                    company_id=created_work_order.company_id,
                ) for task_data in created_work_order.task_data]
            )

        for instance, raw_data in zip(created_work_orders, work_order_data):
            ServiceOrderCommonFunc.create_work_order_cost(instance, raw_data.get('cost_data', []))
            ServiceOrderCommonFunc.create_work_order_contribution(
                instance,
                raw_data.get('product_contribution', []),
                service_detail_id_map,
                shipment_map_id
            )
        return True

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
        return True

    @staticmethod
    def create_work_order_contribution(work_order, contribution_data, service_detail_id_map, shipment_map_id):
        bulk_data = []
        for contribution in contribution_data:
            temp_id = contribution.get('service_id')
            service_detail_uuid = service_detail_id_map.get(temp_id)
            if not service_detail_uuid:
                return False
            package_data = contribution.get('package_data', [])
            if package_data:
                for package in package_data:
                    package_temp_id = package.get('id')
                    package_uuid = shipment_map_id.get(package_temp_id)
                    package['id'] = str(package_uuid)
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
                    unit_cost=contribution.get('unit_cost', 0),
                    total_cost=contribution.get('total_cost', 0),
                    has_package=contribution.get('has_package', False),
                    package_data=contribution.get('package_data', []),
                )
            )
        work_order.work_order_contributions.all().delete()
        ServiceOrderWorkOrderContribution.objects.bulk_create(bulk_data)
        return True

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
        return True

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
                return False

            temp_advance_payment_detail_id = reconcile.get('advance_payment_detail_id')
            advance_payment_detail_uuid = payment_detail_id_map.get(temp_advance_payment_detail_id)
            if not advance_payment_detail_uuid:
                return False

            temp_payment_detail_id = reconcile.get('payment_detail_id')
            payment_detail_uuid = payment_detail_id_map.get(temp_payment_detail_id)
            if not payment_detail_uuid:
                return False

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
        return True

    @staticmethod
    def calculate_total_expense(service_order_obj, expense_data: []):
        service_order_obj['expense_pretax_value'] = 0
        service_order_obj['expense_tax_value'] = 0
        service_order_obj['expense_total_value'] = 0
        if len(expense_data) > 0:
            for expense_item in expense_data:
                pretax_value = expense_item.get('quantity', 0) * expense_item.get('expense_price', 0)
                service_order_obj['expense_pretax_value'] += pretax_value
                tax_id = expense_item.get("tax")
                tax_obj = Tax.objects.filter(id=tax_id).first() if tax_id else None
                tax_rate = tax_obj.rate if tax_obj else 0
                service_order_obj['expense_tax_value'] += pretax_value * tax_rate / 100
            service_order_obj['expense_total_value'] = service_order_obj['expense_pretax_value'] + service_order_obj[
                'expense_tax_value']
        return service_order_obj


class SVODeliveryWorkOrderDetailSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    @classmethod
    def get_product_list(cls, obj):
        product_list = []
        for item in obj.work_order_contributions.all():
            service_detail_obj = item.service_detail
            if service_detail_obj:
                product_list.append(
                    {
                        'id': str(service_detail_obj.product_id),
                        'code': service_detail_obj.product.code,
                        'title': service_detail_obj.product.title,
                        'description': service_detail_obj.product.description,
                        'delivered_quantity': item.delivered_quantity,
                        'product_data': service_detail_obj.product_data,
                    }
                )
        return product_list

    class Meta:
        model = ServiceOrderWorkOrder
        fields = (
            'id',
            'title',
            'code',
            'start_date',
            'end_date',
            'product_list'
        )
