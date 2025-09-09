from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, ExpenseItem, UnitOfMeasure, Tax, Product, Currency
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderShipment,
    ServiceOrderWorkOrder, ServiceOrderServiceDetail, ServiceOrderExpense, ServiceOrderPayment,
)
from apps.sales.serviceorder.serializers import ServiceOrderCommonFunc
from apps.sales.task.models import OpportunityTask
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate, BaseMsg,
)

__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderUpdateSerializer',
]


# SHIPMENT
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
            user=user, model_cls=ServiceOrderAttachMapAttachFile, value=value, doc_id=self.instance.id
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
    def update(self, instance, validated_data):
        with transaction.atomic():
            shipment_data = validated_data.pop('shipment', [])
            expense_data = validated_data.pop('expense', [])
            attachment = validated_data.pop('attachment', [])
            service_detail_data = validated_data.pop('service_detail_data', [])
            work_order_data = validated_data.pop('work_order_data', [])
            payment_data = validated_data.pop('payment_data', [])

            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            ServiceOrderCommonFunc.create_shipment(instance, shipment_data)
            ServiceOrderCommonFunc.create_expense(instance, expense_data)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
                model_cls=ServiceOrderAttachMapAttachFile,
                instance=instance,
                attachment_result=attachment
            )
            service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(instance, service_detail_data)
            ServiceOrderCommonFunc.create_work_order(instance, work_order_data, service_detail_id_map)
            ServiceOrderCommonFunc.create_payment(instance, payment_data, service_detail_id_map)

            return instance

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
