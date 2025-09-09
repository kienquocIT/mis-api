from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, ExpenseItem, UnitOfMeasure, Tax, Product, Currency
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderShipment, ServiceOrderContainer, ServiceOrderPackage,
    ServiceOrderWorkOrder, ServiceOrderServiceDetail, ServiceOrderWorkOrderCost, ServiceOrderWorkOrderContribution,
    ServiceOrderPayment, ServiceOrderPaymentDetail, ServiceOrderPaymentReconcile,
    ServiceOrderExpense,
)
from apps.sales.task.models import OpportunityTask
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate, BaseMsg
)

__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderUpdateSerializer',
    'ServiceOrderShipmentSerializer'
]


# COMMON FUNCTION
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

    # @staticmethod
    # def create_expense(service_order_obj, expense_data):
    #     bulk_info_expense = []
    #     for expense_data_item in expense_data:
    #         expense_item_obj = expense_data_item.get('expense_item')
    #         uom_obj = expense_data_item.get('uom')
    #         tax_obj = expense_data_item.get('tax')
    #
    #         expense_obj = ServiceOrderExpense(
    #             service_order=service_order_obj,
    #             title=expense_data_item.get('title'),
    #             expense_item=expense_item_obj,
    #             expense_item_data={
    #                 "id": str(expense_item_obj.id),
    #                 "code": expense_item_obj.code,
    #                 "title": expense_item_obj.title,
    #             } if expense_item_obj else {},
    #             uom=uom_obj,
    #             uom_data={
    #                 "id": str(uom_obj.id),
    #                 "code": uom_obj.code,
    #                 "title": uom_obj.title,
    #             } if uom_obj else {},
    #             quantity=expense_data_item.get('quantity', 0),
    #             expense_price=expense_data_item.get('expense_price', 0),
    #             tax=tax_obj,
    #             tax_data={
    #                 "id": str(tax_obj.id),
    #                 "code": tax_obj.code,
    #                 "title": tax_obj.title,
    #                 "rate": tax_obj.rate
    #             } if tax_obj else {},
    #             subtotal_price=expense_data_item.get('subtotal_price', 0)
    #         )
    #         bulk_info_expense.append(expense_obj)
    #
    #     # bulk create expense
    #     ServiceOrderExpense.objects.filter(service_order=service_order_obj).delete()
    #     ServiceOrderExpense.objects.bulk_create(bulk_info_expense)
    #
    #     return True
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


class ServiceOrderShipmentSerializer(serializers.ModelSerializer):
    container_type = serializers.JSONField(required=False, allow_null=True)
    package_type = serializers.JSONField(required=False, allow_null=True)

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


# SERVICE DETAIL
class ServiceOrderServiceDetailSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    uom = serializers.UUIDField()
    tax = serializers.UUIDField()
    id = serializers.CharField(required=False)

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
            'total_payment_value'
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


# WORK ORDER
class ServiceOrderWorkOrderSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(allow_null=True, required=False)
    code = serializers.CharField(allow_blank=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    cost_data = serializers.JSONField()
    product_contribution = serializers.JSONField()
    task_id = serializers.UUIDField(required=False, allow_null=True)

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
            'task_id',
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

    @classmethod
    def validate_task_id(cls, value):
        try:
            return OpportunityTask.objects.get(id=value).id
        except OpportunityTask.DoesNotExist:
            raise serializers.ValidationError({'task_id': BaseMsg.NOT_EXIST})


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


# MAIN
class ServiceOrderListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'title',
            'code',
            'customer_data',
            'date_created',
            'end_date',
            'employee_created',
            'system_status'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ServiceOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    shipment = ServiceOrderShipmentSerializer(many=True)
    expense = ServiceOrderExpenseSerializer(many=True)
    expense_pretax_value = serializers.FloatField(required=False, allow_null=True)
    expense_tax_value = serializers.FloatField(required=False, allow_null=True)
    expense_total_value = serializers.FloatField(required=False, allow_null=True)
    service_detail_data = ServiceOrderServiceDetailSerializer(many=True)
    work_order_data = ServiceOrderWorkOrderSerializer(many=True)
    payment_data = ServiceOrderPaymentSerializer(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=ServiceOrderAttachMapAttachFile, value=value
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            customer_obj = Account.objects.get(id=value)
            return customer_obj
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': SVOMsg.CUSTOMER_NOT_EXIST})

    def validate(self, validate_data):
        customer_obj = validate_data.get('customer')
        validate_data["customer_data"] = {
            "id": str(customer_obj.id),
            "name": customer_obj.name,
            "code": customer_obj.code,
            "tax_code": customer_obj.tax_code,
        } if customer_obj else {}

        start_date = validate_data.get('start_date', '')
        end_date = validate_data.get('end_date', '')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({'error': SVOMsg.DATE_COMPARE_ERROR})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        with transaction.atomic():
            shipment_data = validated_data.pop('shipment', [])
            expense_data = validated_data.pop('expense', [])
            attachment = validated_data.pop('attachment', [])
            service_detail_data = validated_data.pop('service_detail_data', [])
            work_order_data = validated_data.pop('work_order_data', [])
            payment_data = validated_data.pop('payment_data', [])
            service_order_obj = ServiceOrder.objects.create(**validated_data)
            ServiceOrderCommonFunc.create_shipment(service_order_obj, shipment_data)
            ServiceOrderCommonFunc.create_expense(service_order_obj, expense_data)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
                model_cls=ServiceOrderAttachMapAttachFile,
                instance=service_order_obj,
                attachment_result=attachment
            )
            service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(service_order_obj, service_detail_data)
            ServiceOrderCommonFunc.create_work_order(service_order_obj, work_order_data, service_detail_id_map)
            ServiceOrderCommonFunc.create_payment(service_order_obj, payment_data, service_detail_id_map)
            return service_order_obj

    class Meta:
        model = ServiceOrder
        fields = (
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipment',
            'expense',
            'expense_pretax_value',
            'expense_tax_value',
            'expense_total_value',
            'attachment',
            'service_detail_data',
            'work_order_data',
            'payment_data'
        )


class ServiceOrderDetailSerializer(AbstractDetailSerializerModel):
    shipment = serializers.SerializerMethodField()
    expense = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    service_detail_data = serializers.SerializerMethodField()
    work_order_data = serializers.SerializerMethodField()
    payment_data = serializers.SerializerMethodField()

    @classmethod
    def get_shipment(cls, obj):
        shipment_list = []
        for item in obj.service_order_shipment_service_order.all():
            is_container = item.is_container
            if is_container:
                shipment_list.append(
                    {
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
                    }
                )
            else:
                shipment_list.append(
                    {
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
                    }
                )
        return shipment_list

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]

    @classmethod
    def get_service_detail_data(cls, obj):
        return [{
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
            'price': service_detail.price,
            'tax_data': service_detail.tax_data,
            'tax_code': service_detail.tax_data.get('code', ''),
            'sub_total_value': service_detail.sub_total_value,
            'total_value': service_detail.total_value,
            'delivery_balance_value': service_detail.delivery_balance_value,
            'total_contribution_percent': service_detail.total_contribution_percent,
            'total_payment_percent': service_detail.total_payment_percent,
            'total_payment_value': service_detail.total_payment_value,
        } for service_detail in obj.service_details.all()]

    @classmethod
    def get_work_order_data(cls, obj):
        return [{
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

            # nested costs
            'cost_data': [{
                'id': cost.id,
                'order': cost.order,
                'title': cost.title,
                'description': cost.description,
                'quantity': cost.quantity,
                'unit_cost': cost.unit_cost,
                'currency_id': cost.currency_id,
                'tax_id': cost.tax_id,
                'total_value': cost.total_value,
                'exchanged_total_value': cost.exchanged_total_value,
            } for cost in work_order.work_order_costs.all()],

            # nested contributions
            'product_contribution_data': [{
                'id': contribution.id,
                'service_id': contribution.service_detail_id,
                'order': contribution.order,
                'title': contribution.title,
                'is_selected': contribution.is_selected,
                'contribution_percent': contribution.contribution_percent,
                'balance_quantity': contribution.balance_quantity,
                'delivered_quantity': contribution.delivered_quantity,
            } for contribution in work_order.work_order_contributions.all()],

            # task
            'task_id': work_order.task_id,
            'task_data': {
                'id': str(work_order.task_id),
                'title': work_order.task.title,
                'employee_inherit': work_order.task.employee_inherit.get_detail_minimal()
                if work_order.task.employee_inherit else {},
            } if work_order.task else {},

        } for work_order in obj.work_orders.all()]

    @classmethod
    def get_payment_data(cls, obj):
        return [{
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

            # nested details
            'payment_detail_data': [{
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
                'reconcile_value': detail.reconcile_value,
                'receivable_value': detail.receivable_value,

                # nested reconciles
                'reconcile_data': [{
                    'id': reconcile.id,
                    'advance_payment_detail_id': reconcile.advance_payment_detail_id,
                    'advance_payment_id': reconcile.advance_payment_detail.service_order_payment.id
                    if reconcile.advance_payment_detail.service_order_payment else None,
                    'payment_detail_id': reconcile.payment_detail_id,
                    'service_id': reconcile.service_detail_id if reconcile.service_detail else None,
                    'installment': reconcile.installment,
                    'total_value': reconcile.total_value,
                    'reconcile_value': reconcile.reconcile_value,
                } for reconcile in detail.payment_detail_reconciles.all()]
            } for detail in payment.payment_details.all()]

        } for payment in obj.payments.all()]

    @classmethod
    def get_expense(cls, obj):
        return [{
            'id': str(item.id),
            'title': item.title,
            'expense_item_data': item.expense_item_data,
            'uom_data': item.uom_data,
            'quantity': item.quantity,
            'expense_price': item.expense_price,
            'tax_data': item.tax_data,
            'subtotal_price': item.subtotal_price
        } for item in obj.service_order_expense_service_order.all()]

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'code',
            'title',
            'date_created',
            'customer_data',
            'start_date',
            'end_date',
            'shipment',
            'expense_pretax_value',
            'expense_tax_value',
            'expense_total_value',
            'attachment',
            'service_detail_data',
            'work_order_data',
            'payment_data',
            'expense'
        )


class ServiceOrderUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    service_detail_data = ServiceOrderServiceDetailSerializer(many=True)
    work_order_data = ServiceOrderWorkOrderSerializer(many=True)
    payment_data = ServiceOrderPaymentSerializer(many=True)

    class Meta:
        model = ServiceOrder
        fields = (
            'title',
            'service_detail_data',
            'work_order_data',
            'payment_data'
        )

    def validate(self, validate_data):
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            service_detail_data = validated_data.pop('service_detail_data', [])
            work_order_data = validated_data.pop('work_order_data', [])
            payment_data = validated_data.pop('payment_data', [])

            service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(instance, service_detail_data)
            ServiceOrderCommonFunc.create_work_order(instance, work_order_data, service_detail_id_map)
            ServiceOrderCommonFunc.create_payment(instance, payment_data, service_detail_id_map)

            return instance
