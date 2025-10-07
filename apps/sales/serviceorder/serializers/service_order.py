from rest_framework import serializers
from apps.core.attachments.models import update_files_is_approved
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account
from apps.sales.opportunity.models import Opportunity
from apps.sales.opportunity.msg import OpportunityOnlyMsg
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile
)
from apps.sales.serviceorder.serializers.service_order_sub import (
    ServiceOrderShipmentSerializer, ServiceOrderExpenseSerializer,
    ServiceOrderServiceDetailSerializer, ServiceOrderWorkOrderSerializer, ServiceOrderPaymentSerializer,
    ServiceOrderCommonFunc,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate
)


__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderUpdateSerializer'
]


class ServiceOrderListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'title',
            'code',
            'customer_data',
            'employee_created',
            'date_created',
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
    service_detail_data = ServiceOrderServiceDetailSerializer(many=True)
    work_order_data = ServiceOrderWorkOrderSerializer(many=True)
    payment_data = ServiceOrderPaymentSerializer(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)

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

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            if value is None:
                return value
            return Opportunity.objects.get_on_company(id=value).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': OpportunityOnlyMsg.OPP_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            if value is None:
                return value
            return Employee.objects.get_on_company(id=value).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit_id': OpportunityOnlyMsg.EMP_NOT_EXIST})

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

        expense_data = validate_data.get('expense', [])
        validate_data = ServiceOrderCommonFunc.calculate_total_expense(validate_data, expense_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        shipment_data = validated_data.pop('shipment', [])
        expense_data = validated_data.pop('expense', [])
        attachment = validated_data.pop('attachment', [])
        service_detail_data = validated_data.pop('service_detail_data', [])
        work_order_data = validated_data.pop('work_order_data', [])
        payment_data = validated_data.pop('payment_data', [])
        service_order_obj = ServiceOrder.objects.create(**validated_data)
        shipment_map_id = ServiceOrderCommonFunc.create_shipment(service_order_obj, shipment_data)
        ServiceOrderCommonFunc.create_expense(service_order_obj, expense_data)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
            model_cls=ServiceOrderAttachMapAttachFile,
            instance=service_order_obj,
            attachment_result=attachment
        )
        service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(service_order_obj, service_detail_data)
        ServiceOrderCommonFunc.create_work_order(
            service_order_obj, work_order_data, service_detail_id_map, shipment_map_id
        )
        ServiceOrderCommonFunc.create_payment(service_order_obj, payment_data, service_detail_id_map)

        # adhoc case after create SO
        update_files_is_approved(
            ServiceOrderAttachMapAttachFile.objects.filter(
                service_order=service_order_obj, attachment__is_approved=False
            ),
            service_order_obj
        )
        return service_order_obj

    class Meta:
        model = ServiceOrder
        fields = (
            'opportunity_id',
            'employee_inherit_id',
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipment',
            'expense',
            'attachment',
            'service_detail_data',
            'work_order_data',
            'payment_data',
            'exchange_rate_data'
        )


class ServiceOrderDetailSerializer(AbstractDetailSerializerModel):
    shipment = serializers.SerializerMethodField()
    expense = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    service_detail_data = serializers.SerializerMethodField()
    work_order_data = serializers.SerializerMethodField()
    payment_data = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

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
                            'id':  str(item.package_type.id),
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
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

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
            'duration': service_detail.duration_value if hasattr(service_detail, 'duration_value') else 0,
            'has_attributes': bool(service_detail.selected_attributes and service_detail.selected_attributes != {}),
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
                'unit_cost': contribution.unit_cost,
                'total_cost': contribution.total_cost,
                'has_package': contribution.has_package,
                'package_data': contribution.package_data,
            } for contribution in work_order.work_order_contributions.all()],

            # tasks
            'task_data': [
                {
                    'id': str(work_order_task.task_id),
                    'title': work_order_task.task.title,
                    'employee_created': work_order_task.task.employee_created.get_detail_minimal()
                    if work_order_task.task.employee_created else {},
                    'employee_inherit': work_order_task.task.employee_inherit.get_detail_minimal()
                    if work_order_task.task.employee_inherit else {},
                    'percent_completed': work_order_task.task.percent_completed,
                } if work_order_task.task else {}
                for work_order_task in work_order.service_order_work_order_task_wo.all()
            ],

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
                'tax_data': detail.service_detail.tax_data if payment.is_invoice_required else None,
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

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'customer': obj.customer_data,
            'is_deal_close': obj.opportunity.is_deal_close,
        } if obj.opportunity else {}

    class Meta:
        model = ServiceOrder
        fields = (
            'opportunity',
            'employee_inherit',
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
            'expense',
            'exchange_rate_data'
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

        expense_data = validate_data.get('expense', [])
        validate_data = ServiceOrderCommonFunc.calculate_total_expense(validate_data, expense_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        shipment_data = validated_data.pop('shipment', [])
        expense_data = validated_data.pop('expense', [])
        attachment = validated_data.pop('attachment', [])
        service_detail_data = validated_data.pop('service_detail_data', [])
        work_order_data = validated_data.pop('work_order_data', [])
        payment_data = validated_data.pop('payment_data', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        shipment_map_id = ServiceOrderCommonFunc.create_shipment(instance, shipment_data)

        ServiceOrderCommonFunc.create_shipment(instance, shipment_data)
        ServiceOrderCommonFunc.create_expense(instance, expense_data)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
            model_cls=ServiceOrderAttachMapAttachFile,
            instance=instance,
            attachment_result=attachment
        )
        service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(instance, service_detail_data)
        ServiceOrderCommonFunc.create_work_order(instance, work_order_data, service_detail_id_map, shipment_map_id)
        ServiceOrderCommonFunc.create_payment(instance, payment_data, service_detail_id_map)
        # adhoc case update file to KMS
        update_files_is_approved(
            ServiceOrderAttachMapAttachFile.objects.filter(
                service_order=instance, attachment__is_approved=False
            ),
            instance
        )
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
            'payment_data',
            'exchange_rate_data',
        )
