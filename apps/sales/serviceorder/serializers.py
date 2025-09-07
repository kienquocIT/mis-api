from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, Product, UnitOfMeasure, Tax, Currency
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderShipment, ServiceOrderContainer, ServiceOrderPackage,
    ServiceOrderWorkOrder, ServiceOrderServiceDetail, ServiceOrderWorkOrderCost, ServiceOrderWorkOrderContribution,
    ServiceOrderPayment, ServiceOrderPaymentDetail, ServiceOrderPaymentReconcile,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel, AttachmentMsg,
    SVOMsg
)

__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderUpdateSerializer',
    'ServiceOderShipmentSerializer'
]


# COMMON FUNCTION
class ServiceOrderCommonFunc:
    @staticmethod
    def create_attachment(doc_id, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.get(id="36f25733-a6e7-43ea-b710-38e2052f0f6d")
            state = ServiceOrderAttachMapAttachFile.resolve_change(
                result=attachment_result,
                doc_id=doc_id,
                doc_app=relate_app
            )
            if state:
                return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True

    @staticmethod
    def get_mapped_data(shipment_data_item):
        if shipment_data_item.get('is_container', True):
            return {
                'title': shipment_data_item.get('containerName', ''),
                'reference_number': shipment_data_item.get('containerRefNumber', ''),
                'weight': shipment_data_item.get('containerWeight', 0),
                'dimension': shipment_data_item.get('containerDimension', 0),
                'description': shipment_data_item.get('containerNote'),
                'is_container': True,
                'reference_container': None
            }
        return {
            'title': shipment_data_item.get('packageName', ''),
            'reference_number': shipment_data_item.get('containerRefNumber', ''),
            'weight': shipment_data_item.get('packageWeight', 0),
            'dimension': shipment_data_item.get('packageDimension', 0),
            'description': shipment_data_item.get('packageNote'),
            'is_container': False,
            'reference_container': shipment_data_item.get('packageContainerRef'),
        }

    @staticmethod
    def create_shipment(service_order_obj, shipment_data):
        bulk_info_shipment = []
        bulk_info_container = []
        for _, shipment_data_item in enumerate(shipment_data):
            item_data_parsed = ServiceOrderCommonFunc.get_mapped_data(shipment_data_item)
            shipment_obj = ServiceOrderShipment(service_order=service_order_obj, **item_data_parsed)
            bulk_info_shipment.append(shipment_obj)
            # get container
            ctn_order = 1
            if shipment_obj.is_container:
                bulk_info_container.append(ServiceOrderContainer(
                    shipment=shipment_obj,
                    order=ctn_order,
                    container_type_id=shipment_data_item.get("containerType", {}).get("id")
                ))
                ctn_order += 1

        # bulk create shipments
        ServiceOrderShipment.objects.filter(service_order=service_order_obj).delete()
        ServiceOrderShipment.objects.bulk_create(bulk_info_shipment)

        # bulk create container
        container_created = ServiceOrderContainer.objects.bulk_create(bulk_info_container)

        # create package part
        bulk_info_packages = []
        for _, shipment_data_item in enumerate(shipment_data):
            # get package
            pkg_order = 1
            if not shipment_data_item.get('is_container'):
                ctn_mapped = None
                for ctn in container_created:
                    if ctn.shipment.reference_number == shipment_data_item.get('packageContainerRef'):
                        ctn_mapped = ctn
                if ctn_mapped:
                    bulk_info_packages.append(ServiceOrderPackage(
                        shipment=ctn_mapped.shipment,
                        order=pkg_order,
                        package_type_id=str(shipment_data_item.get("packageType", {}).get("id")),
                        container_reference_id=str(ctn_mapped.id)
                    ))
                    pkg_order += 1

        # bulk create package
        ServiceOrderPackage.objects.bulk_create(bulk_info_packages)
        return True

    @staticmethod
    def create_expense(service_order_obj, expense_data):
        pass

    @staticmethod
    def create_service_detail(service_order, service_detail_data):
        service_order_id = service_order.id
        bulk_data = []
        service_detail_id_map = {}
        for service_detail in service_detail_data:
            bulk_data.append(ServiceOrderServiceDetail(
                service_order_id=service_order_id,
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
            ))

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
            bulk_data.append(ServiceOrderWorkOrderCost(
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
            ))

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
            bulk_data.append(ServiceOrderWorkOrderContribution(
                work_order=work_order,
                service_detail_id=service_detail_uuid,
                order=contribution.get('order', 0),
                title=contribution.get('title', ''),
                contribution_percent=contribution.get('contribution_percent', 0),
                balance_quantity=contribution.get('balance_quantity', 0),
                delivered_quantity=contribution.get('delivered_quantity', 0),
            ))
        work_order.work_order_contributions.all().delete()
        ServiceOrderWorkOrderContribution.objects.bulk_create(bulk_data)

    @staticmethod
    def create_payment(service_order, payment_data, service_detail_id_map):
        service_order_id = service_order.id
        bulk_data = []
        for payment in payment_data:
            bulk_data.append(ServiceOrderPayment(
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
            ))
        service_order.payments.all().delete()
        created_payments = ServiceOrderPayment.objects.bulk_create(bulk_data)
        payment_detail_id_map = {}
        for instance, raw_data in zip(created_payments, payment_data):
            payment_detail_id_map.update(ServiceOrderCommonFunc.create_payment_detail(
                instance,
                raw_data.get('payment_detail_data', []),
                service_detail_id_map
            ))

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
                return
            bulk_data.append(ServiceOrderPaymentDetail(
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
            ))

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

            bulk_data.append(ServiceOrderPaymentReconcile(
                advance_payment_detail_id=advance_payment_detail_uuid,
                payment_detail_id=payment_detail_uuid,
                service_detail_id=service_uuid,
                installment=reconcile.get('installment', 0),
                total_value=reconcile.get('total_value', 0),
                reconcile_value=reconcile.get('reconcile_value', 0)
            ))
        ServiceOrderPaymentReconcile.objects.bulk_create(bulk_data)

# SHIPMENT
class ServiceOderShipmentSerializer(serializers.Serializer):
    is_container = serializers.BooleanField(default=True)

    # container field
    containerName = serializers.CharField(max_length=100, required=False, allow_null=True)
    containerRefNumber = serializers.CharField(max_length=100, required=False, allow_null=True)
    containerWeight = serializers.FloatField(required=False, allow_null=True)
    containerDimension = serializers.FloatField(required=False, allow_null=True)
    containerNote = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    containerType = serializers.JSONField(required=False, allow_null=True)

    packageName = serializers.CharField(max_length=100, required=False, allow_null=True)
    packageRefNumber = serializers.CharField(max_length=100, required=False, allow_null=True)
    packageWeight = serializers.FloatField(required=False, allow_null=True)
    packageDimension = serializers.FloatField(required=False, allow_null=True)
    packageNote = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    packageContainerRef = serializers.CharField(max_length=100, required=False, allow_null=True)
    packageType = serializers.JSONField(required=False, allow_null=True)

    def validate(self, validate_data):
        if validate_data.get('is_container', True):
            if not validate_data.get('containerName'):
                raise serializers.ValidationError({'container name': SVOMsg.CONTAINER_NAME_NOT_EXIST})
            if not validate_data.get('containerRefNumber'):
                raise serializers.ValidationError({'Container Reference Number': SVOMsg.CONTAINER_REF_NOT_EXIST})

        else:
            if not validate_data.get('packageName'):
                raise serializers.ValidationError({'Package Name': SVOMsg.PACKAGE_NAME_NOT_EXIST})
            if not validate_data.get('packageContainerRef'):
                raise serializers.ValidationError({'Package Reference Container': SVOMsg.PACKAGE_REF_NOT_EXIST})

        return validate_data


# EXPENSE
class ServiceOrderExpenseSerializer(serializers.Serializer):
    pass


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
            'product_contribution'
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
                    raise serializers.ValidationError({'work_order_cost': _('Currency of work order cost does not exist')})
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

# PAYMENT
class ServiceOrderPaymentSerializer(serializers.ModelSerializer):
    payment_detail_data = serializers.JSONField()
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
    shipment = ServiceOderShipmentSerializer(many=True)
    expense = ServiceOrderExpenseSerializer(many=True)
    service_detail_data = ServiceOrderServiceDetailSerializer(many=True)
    work_order_data = ServiceOrderWorkOrderSerializer(many=True)
    payment_data = ServiceOrderPaymentSerializer(many=True)
    # attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    # def validate_attachment(self, value):
    #     user = self.context.get('user', None)
    #     return SerializerCommonValidate.validate_attachment(
    #         user=user, model_cls=ServiceOrderAttachMapAttachFile, value=value
    #     )


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
        shipment_data = validated_data.pop('shipment', [])
        expense_data = validated_data.pop('expense', [])
        service_detail_data = validated_data.pop('service_detail_data', [])
        work_order_data = validated_data.pop('work_order_data', [])
        payment_data = validated_data.pop('payment_data', [])
        # attachment = validated_data.pop('attachment', [])
        service_order_obj = ServiceOrder.objects.create(**validated_data)
        ServiceOrderCommonFunc.create_shipment(service_order_obj, shipment_data)
        ServiceOrderCommonFunc.create_expense(service_order_obj, expense_data)
        service_detail_id_map = ServiceOrderCommonFunc.create_service_detail(service_order_obj, service_detail_data)
        ServiceOrderCommonFunc.create_work_order(service_order_obj, work_order_data, service_detail_id_map)
        ServiceOrderCommonFunc.create_payment(service_order_obj, payment_data, service_detail_id_map)
        # ServiceOrderCommonFunc.create_attachment(service_order.id, attachment)
        # SerializerCommonHandle.handle_attach_file(
        #     relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
        #     model_cls=ServiceOrderAttachMapAttachFile,
        #     instance=service_order,
        #     attachment_result=attachment
        # )
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
            'service_detail_data',
            'work_order_data',
            'payment_data'
            # 'attachment'
        )


class ServiceOrderDetailSerializer(AbstractDetailSerializerModel):
    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'code',
            'title',
        )


class ServiceOrderUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ServiceOrder
        fields = (
            'title',
        )

    def validate(self, validate_data):
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance
