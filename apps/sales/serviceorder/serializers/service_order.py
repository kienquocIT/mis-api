from django.db import transaction
from rest_framework import serializers

from apps.core.attachments.models import update_files_is_approved
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, ExpenseItem, UnitOfMeasure, Tax
from apps.sales.opportunity.models import Opportunity
from apps.sales.opportunity.msg import OpportunityOnlyMsg
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderShipment,
    ServiceOrderWorkOrder, ServiceOrderServiceDetail, ServiceOrderExpense, ServiceOrderPayment, ServiceOrderContainer,
    ServiceOrderPackage, ServiceOrderWorkOrderCost, ServiceOrderWorkOrderContribution, ServiceOrderPaymentDetail,
    ServiceOrderPaymentReconcile, ServiceOrderWorkOrderTask,
)
from apps.sales.serviceorder.serializers.service_order_sub import (
    ServiceOrderShipmentSerializer, ServiceOrderExpenseSerializer,
    ServiceOrderServiceDetailSerializer, ServiceOrderWorkOrderSerializer, ServiceOrderPaymentSerializer,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate
)


__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderUpdateSerializer',
    'ServiceOrderDetailSerializerForDashboard',
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
        with transaction.atomic():
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
                )
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
            'payment_data'
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
                            'id': str(item.container_type.id) if item.container_type else None,
                            'code': item.container_type.code if item.container_type else None,
                            'title': item.container_type.title if item.container_type else None,
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
                            'id':  str(item.package_type.id) if item.package_type else None,
                            'code': item.package_type.code if item.package_type else None,
                            'title': item.package_type.title if item.package_type else None,
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
            'customer': {
                'id': obj.opportunity.customer_id,
                'title': obj.opportunity.customer.title
            } if obj.opportunity.customer else {},
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

        expense_data = validate_data.get('expense', [])
        validate_data = ServiceOrderCommonFunc.calculate_total_expense(validate_data, expense_data)
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
                )
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
            'payment_data'
        )


class ServiceOrderDetailSerializerForDashboard(AbstractDetailSerializerModel):
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
            service_order_detail_list.append({
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
                } for wo_ctb_item in item.service_detail_contributions.all().order_by("work_order__order")]
            })
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
            ServiceOrderWorkOrderTask.objects.bulk_create([ServiceOrderWorkOrderTask(
                work_order=created_work_order,
                task_id=task_data.get('id', None),
                tenant_id=created_work_order.tenant_id,
                company_id=created_work_order.company_id,
            ) for task_data in created_work_order.task_data])

        for instance, raw_data in zip(created_work_orders, work_order_data):
            ServiceOrderCommonFunc.create_work_order_cost(instance, raw_data.get('cost_data', []))
            ServiceOrderCommonFunc.create_work_order_contribution(
                instance,
                raw_data.get('product_contribution', []),
                service_detail_id_map,
                shipment_map_id
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
    def create_work_order_contribution(work_order, contribution_data, service_detail_id_map, shipment_map_id):
        bulk_data = []
        for contribution in contribution_data:
            temp_id = contribution.get('service_id')
            service_detail_uuid = service_detail_id_map.get(temp_id)
            if not service_detail_uuid:
                return
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
                    has_package=contribution.get('has_package', False),
                    package_data=contribution.get('package_data', []),
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
