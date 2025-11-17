from django.db import transaction
from rest_framework import serializers
from apps.core.attachments.models import update_files_is_approved
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, ExpenseItem, UnitOfMeasure, Tax
from apps.sales.opportunity.models import Opportunity
from apps.sales.opportunity.msg import OpportunityOnlyMsg
from apps.sales.servicequotation.models import (
    ServiceQuotation, ServiceQuotationAttachMapAttachFile, ServiceQuotationShipment,
    ServiceQuotationWorkOrder, ServiceQuotationServiceDetail, ServiceQuotationExpense, ServiceQuotationPayment,
    ServiceQuotationContainer,
    ServiceQuotationPackage, ServiceQuotationWorkOrderCost, ServiceQuotationWorkOrderContribution,
    ServiceQuotationPaymentDetail,
    ServiceQuotationPaymentReconcile,
)
from apps.sales.servicequotation.serializers.service_quotation_sub import (
    ServiceQuotationShipmentSerializer, ServiceQuotationExpenseSerializer,
    ServiceQuotationServiceDetailSerializer, ServiceQuotationWorkOrderSerializer, ServiceQuotationPaymentSerializer,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate
)

__all__ = [
    'ServiceQuotationListSerializer',
    'ServiceQuotationCreateSerializer',
    'ServiceQuotationDetailSerializer',
    'ServiceQuotationUpdateSerializer',
]


class ServiceQuotationListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()

    class Meta:
        model = ServiceQuotation
        fields = (
            'id',
            'title',
            'code',
            'customer_data',
            'employee_created',
            'date_created',
            'system_status',
            'opportunity'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'customer': obj.customer_data,
            'is_deal_close': obj.opportunity.is_deal_close,
        } if obj.opportunity else {}


class ServiceQuotationCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    shipment = ServiceQuotationShipmentSerializer(many=True)
    expenses_data = ServiceQuotationExpenseSerializer(many=True)
    service_detail_data = ServiceQuotationServiceDetailSerializer(many=True)
    work_order_data = ServiceQuotationWorkOrderSerializer(many=True)
    payment_data = ServiceQuotationPaymentSerializer(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=ServiceQuotationAttachMapAttachFile, value=value
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
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({'error': SVOMsg.DATE_COMPARE_ERROR})

        expense_data = validate_data.get('expenses_data', [])
        validate_data = ServiceQuotationCommonFunc.calculate_total_expense(validate_data, expense_data)

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        with transaction.atomic():
            shipment_data = validated_data.pop('shipment', [])
            expense_data = validated_data.pop('expenses_data', [])
            attachment = validated_data.pop('attachment', [])
            service_detail_data = validated_data.pop('service_detail_data', [])
            work_order_data = validated_data.pop('work_order_data', [])
            payment_data = validated_data.pop('payment_data', [])

            service_quotation_obj = ServiceQuotation.objects.create(**validated_data)

            shipment_map_id = ServiceQuotationCommonFunc.create_shipment(service_quotation_obj, shipment_data)
            ServiceQuotationCommonFunc.create_expense(service_quotation_obj, expense_data)

            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="c9e131ec-760c-45af-8ae6-5349f2bb542e").first(),
                model_cls=ServiceQuotationAttachMapAttachFile,
                instance=service_quotation_obj,
                attachment_result=attachment
            )

            service_detail_id_map = ServiceQuotationCommonFunc.create_service_detail(service_quotation_obj,
                                                                                     service_detail_data)
            ServiceQuotationCommonFunc.create_work_order(
                service_quotation_obj, work_order_data, service_detail_id_map, shipment_map_id
            )
            ServiceQuotationCommonFunc.create_payment(service_quotation_obj, payment_data, service_detail_id_map)

            # adhoc case after create SQ
            update_files_is_approved(
                ServiceQuotationAttachMapAttachFile.objects.filter(
                    service_quotation=service_quotation_obj, attachment__is_approved=False
                ), service_quotation_obj,
            )

            return service_quotation_obj

    class Meta:
        model = ServiceQuotation
        fields = (
            'opportunity_id',
            'employee_inherit_id',
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipment',
            'expenses_data',
            'attachment',
            'service_detail_data',
            'work_order_data',
            'payment_data',
            'exchange_rate_data'
        )


class ServiceQuotationDetailSerializer(AbstractDetailSerializerModel):
    shipment = serializers.SerializerMethodField()
    expenses_data = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    service_detail_data = serializers.SerializerMethodField()
    work_order_data = serializers.SerializerMethodField()
    payment_data = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_shipment(cls, obj):
        shipment_list = []
        for item in obj.service_quotation_shipment_service_quotation.all():
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
            'service_percent': service_detail.service_percent,
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
            'selected_attributes': service_detail.selected_attributes,
            'attributes_total_cost': service_detail.attributes_total_cost,
            'duration_id': service_detail.duration_id if service_detail.duration else None,
            'duration_unit_data': service_detail.duration_unit_data,
            'duration': service_detail.duration_value if hasattr(service_detail,
                                                                 'duration_value') and service_detail.duration else 1,
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
                    'advance_payment_id': reconcile.advance_payment_detail.service_quotation_payment.id
                    if reconcile.advance_payment_detail.service_quotation_payment else None,
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
        } for item in obj.service_quotation_expense_service_quotation.all()]

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
        model = ServiceQuotation
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
            'expenses_data',
            'exchange_rate_data'
        )


class ServiceQuotationUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    shipment = ServiceQuotationShipmentSerializer(many=True)
    expenses_data = ServiceQuotationExpenseSerializer(many=True)
    expense_pretax_value = serializers.FloatField(required=False, allow_null=True)
    expense_tax_value = serializers.FloatField(required=False, allow_null=True)
    expense_total_value = serializers.FloatField(required=False, allow_null=True)
    service_detail_data = ServiceQuotationServiceDetailSerializer(many=True)
    work_order_data = ServiceQuotationWorkOrderSerializer(many=True)
    payment_data = ServiceQuotationPaymentSerializer(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=ServiceQuotationAttachMapAttachFile, value=value, doc_id=self.instance.id
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
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({'error': SVOMsg.DATE_COMPARE_ERROR})

        expense_data = validate_data.get('expenses_data', [])
        validate_data = ServiceQuotationCommonFunc.calculate_total_expense(validate_data, expense_data)

        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        with transaction.atomic():
            shipment_data = validated_data.pop('shipment', [])
            expense_data = validated_data.pop('expenses_data', [])
            attachment = validated_data.pop('attachment', [])
            service_detail_data = validated_data.pop('service_detail_data', [])
            work_order_data = validated_data.pop('work_order_data', [])
            payment_data = validated_data.pop('payment_data', [])

            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            shipment_map_id = ServiceQuotationCommonFunc.create_shipment(instance, shipment_data)
            ServiceQuotationCommonFunc.create_expense(instance, expense_data)

            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="c9e131ec-760c-45af-8ae6-5349f2bb542e").first(),
                model_cls=ServiceQuotationAttachMapAttachFile,
                instance=instance,
                attachment_result=attachment
            )

            service_detail_id_map = ServiceQuotationCommonFunc.create_service_detail(instance, service_detail_data)
            ServiceQuotationCommonFunc.create_work_order(instance, work_order_data, service_detail_id_map,
                                                         shipment_map_id)
            ServiceQuotationCommonFunc.create_payment(instance, payment_data, service_detail_id_map)

            # adhoc case update file to KMS
            update_files_is_approved(
                ServiceQuotationAttachMapAttachFile.objects.filter(
                    service_quotation=instance, attachment__is_approved=False
                ), instance,
            )

            return instance

    class Meta:
        model = ServiceQuotation
        fields = (
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipment',
            'expenses_data',
            'expense_pretax_value',
            'expense_tax_value',
            'expense_total_value',
            'attachment',
            'service_detail_data',
            'work_order_data',
            'payment_data',
            'exchange_rate_data',
        )


class ServiceQuotationCommonFunc:
    @staticmethod
    def build_shipments(service_quotation_obj, shipment_data):
        bulk_info_shipment, bulk_info_container = [], []
        ctn_shipment, ctn_order = 1, 1
        for shipment_data_item in shipment_data:
            package_type = shipment_data_item.get("package_type")
            container_type = shipment_data_item.get("container_type")
            shipment_obj = ServiceQuotationShipment(
                service_quotation=service_quotation_obj,
                order=ctn_shipment,
                title=shipment_data_item.get("title", ""),
                container_type_id=container_type.get("id") if container_type else None,
                package_type_id=package_type.get("id") if package_type else None,
                company=service_quotation_obj.company,
                tenant=service_quotation_obj.tenant,
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
                    ServiceQuotationContainer(
                        service_quotation=service_quotation_obj,
                        shipment=shipment_obj,
                        order=ctn_order,
                        container_type_id=container_type.get("id") if container_type else None,
                        company=service_quotation_obj.company,
                        tenant=service_quotation_obj.tenant,
                    )
                )
                ctn_order += 1
            ctn_shipment += 1
        return bulk_info_shipment, bulk_info_container

    @staticmethod
    def build_packages(service_quotation_obj, shipment_data, container_created):
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
                        ServiceQuotationPackage(
                            service_quotation=service_quotation_obj,
                            shipment=ctn_mapped.shipment,
                            order=pkg_order,
                            package_type_id=package_type.get("id") if package_type else None,
                            container_reference_id=str(ctn_mapped.id),
                            company=service_quotation_obj.company,
                            tenant=service_quotation_obj.tenant,
                        )
                    )
                    pkg_order += 1
        return bulk_info_packages

    @staticmethod
    def create_shipment(service_quotation_obj, shipment_data):
        shipment_map_id = {}
        # build shipment and containers
        bulk_info_shipment, bulk_info_container = ServiceQuotationCommonFunc.build_shipments(
            service_quotation_obj, shipment_data
        )
        ServiceQuotationShipment.objects.filter(service_quotation=service_quotation_obj).delete()
        created_shipments = ServiceQuotationShipment.objects.bulk_create(bulk_info_shipment)
        container_created = ServiceQuotationContainer.objects.bulk_create(bulk_info_container)

        # Map temp id
        for shipment_data_item, created_shipment_item in zip(shipment_data, created_shipments):
            temp_id = shipment_data_item.get('id')
            if temp_id:
                shipment_map_id[temp_id] = created_shipment_item.id

        # build packages
        bulk_info_packages = ServiceQuotationCommonFunc.build_packages(service_quotation_obj, shipment_data,
                                                                       container_created)
        ServiceQuotationPackage.objects.bulk_create(bulk_info_packages)

        return shipment_map_id

    @staticmethod
    def create_expense(service_quotation_obj, expense_data):
        bulk_info_expense = []
        for expense_data_item in expense_data:
            # Resolve UUID → instance
            expense_item_id = expense_data_item.get("expense_item")
            uom_id = expense_data_item.get("uom")
            tax_id = expense_data_item.get("tax")

            expense_item_obj = ExpenseItem.objects.filter(id=expense_item_id).first() if expense_item_id else None
            uom_obj = UnitOfMeasure.objects.filter(id=uom_id).first() if uom_id else None
            tax_obj = Tax.objects.filter(id=tax_id).first() if tax_id else None

            expense_obj = ServiceQuotationExpense(
                service_quotation=service_quotation_obj,
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
                company=service_quotation_obj.company,
                tenant=service_quotation_obj.tenant,
            )
            bulk_info_expense.append(expense_obj)

        # Replace old expenses
        ServiceQuotationExpense.objects.filter(service_quotation=service_quotation_obj).delete()
        ServiceQuotationExpense.objects.bulk_create(bulk_info_expense)

        return True

    @staticmethod
    def create_service_detail(service_quotation, service_detail_data):
        service_quotation_id = service_quotation.id
        bulk_data = []
        service_detail_id_map = {}

        for service_detail in service_detail_data:
            duration_obj = service_detail.get('duration')
            product_obj = service_detail.get('product')

            # Prepare duration_unit_data based on duration object
            duration_unit_data = {}
            if duration_obj:
                duration_unit_data = {
                    "id": str(duration_obj.id),
                    "code": duration_obj.code,
                    "title": duration_obj.title,
                }

            bulk_data.append(
                ServiceQuotationServiceDetail(
                    service_quotation_id=service_quotation_id,
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
                    service_percent=service_detail.get('service_percent'),
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
                    selected_attributes=service_detail.get('selected_attributes', {}),
                    attributes_total_cost=service_detail.get('attributes_total_cost', 0),
                    duration=duration_obj,
                    duration_value=service_detail.get('duration_value', 0),
                    duration_unit_data=duration_unit_data or service_detail.get('duration_unit_data', {}),
                )
            )

        service_quotation.service_details.all().delete()
        created_service_details = ServiceQuotationServiceDetail.objects.bulk_create(bulk_data)

        for frontend_data, backend_data in zip(service_detail_data, created_service_details):
            temp_id = frontend_data.get('id')
            if temp_id:
                service_detail_id_map[temp_id] = backend_data.id

        return service_detail_id_map

    @staticmethod
    def create_work_order(service_quotation, work_order_data, service_detail_id_map, shipment_map_id):
        service_quotation_id = service_quotation.id
        bulk_data = []

        for work_order in work_order_data:
            instance = ServiceQuotationWorkOrder(
                service_quotation_id=service_quotation_id,
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
                tenant_id=service_quotation.tenant_id,
                company_id=service_quotation.company_id,
            )
            bulk_data.append(instance)

        service_quotation.work_orders.all().delete()
        created_work_orders = ServiceQuotationWorkOrder.objects.bulk_create(bulk_data)

        for instance, raw_data in zip(created_work_orders, work_order_data):
            ServiceQuotationCommonFunc.create_work_order_cost(instance, raw_data.get('cost_data', []))
            ServiceQuotationCommonFunc.create_work_order_contribution(
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
                ServiceQuotationWorkOrderCost(
                    work_order=work_order,
                    order=cost.get('order', 0),
                    title=cost.get('title', ''),
                    description=cost.get('description', ''),
                    quantity=cost.get('quantity', 0),
                    unit_cost=cost.get('unit_cost', 0),
                    currency_id=cost.get('currency_id'),
                    expense_item_id=cost.get('expense_item_id'),
                    tax_id=cost.get('tax_id'),
                    total_value=cost.get('total_value', 0),
                    exchanged_total_value=cost.get('exchanged_total_value', 0),
                )
            )
        work_order.work_order_costs.all().delete()
        ServiceQuotationWorkOrderCost.objects.bulk_create(bulk_data)

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
                ServiceQuotationWorkOrderContribution(
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
        ServiceQuotationWorkOrderContribution.objects.bulk_create(bulk_data)

    @staticmethod
    def create_payment(service_quotation, payment_data, service_detail_id_map):
        service_quotation_id = service_quotation.id
        bulk_data = []

        for payment in payment_data:
            bulk_data.append(
                ServiceQuotationPayment(
                    service_quotation_id=service_quotation_id,
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

        service_quotation.payments.all().delete()
        created_payments = ServiceQuotationPayment.objects.bulk_create(bulk_data)

        payment_detail_id_map = {}
        for instance, raw_data in zip(created_payments, payment_data):
            payment_detail_id_map.update(
                ServiceQuotationCommonFunc.create_payment_detail(
                    instance,
                    raw_data.get('payment_detail_data', []),
                    service_detail_id_map
                )
            )

        for instance, raw_data in zip(created_payments, payment_data):
            ServiceQuotationCommonFunc.create_reconcile_data(
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
                ServiceQuotationPaymentDetail(
                    service_quotation_payment=payment,
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

        created_payment_details = ServiceQuotationPaymentDetail.objects.bulk_create(bulk_data)

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
                ServiceQuotationPaymentReconcile(
                    advance_payment_detail_id=advance_payment_detail_uuid,
                    payment_detail_id=payment_detail_uuid,
                    service_detail_id=service_uuid,
                    installment=reconcile.get('installment', 0),
                    total_value=reconcile.get('total_value', 0),
                    reconcile_value=reconcile.get('reconcile_value', 0)
                )
            )

        ServiceQuotationPaymentReconcile.objects.bulk_create(bulk_data)

    @staticmethod
    def calculate_total_expense(service_quotation_obj, expense_data: []):
        service_quotation_obj['expense_pretax_value'] = 0
        service_quotation_obj['expense_tax_value'] = 0
        service_quotation_obj['expense_total_value'] = 0

        if len(expense_data) > 0:
            for expense_item in expense_data:
                pretax_value = expense_item.get('quantity', 0) * expense_item.get('expense_price', 0)
                service_quotation_obj['expense_pretax_value'] += pretax_value

                tax_id = expense_item.get("tax")
                tax_obj = Tax.objects.filter(id=tax_id).first() if tax_id else None
                tax_rate = tax_obj.rate if tax_obj else 0
                service_quotation_obj['expense_tax_value'] += pretax_value * tax_rate / 100

            service_quotation_obj['expense_total_value'] = service_quotation_obj['expense_pretax_value'] + \
                                                           service_quotation_obj['expense_tax_value']

        return service_quotation_obj
