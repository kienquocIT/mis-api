from django.db import transaction
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, ExpenseItem, UnitOfMeasure, Tax
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderShipment, ServiceOrderContainer, ServiceOrderPackage,
    ServiceOrderExpense,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SVOMsg, SerializerCommonHandle, SerializerCommonValidate
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
    def get_mapped_data(shipment_data_item):
        if shipment_data_item.get('is_container', True):
            return {
                'title': shipment_data_item.get('containerName', ''),
                'reference_number': shipment_data_item.get('containerRefNumber', ''),
                'weight': shipment_data_item.get('containerWeight', 0),
                'dimension': shipment_data_item.get('containerDimension', 0),
                'description': shipment_data_item.get('containerNote'),
                'is_container': True,
                'reference_container': None,
                'container_type_id': str(shipment_data_item.get("containerType", {}).get("id"))
            }
        return {
            'title': shipment_data_item.get('packageName', ''),
            'reference_number': shipment_data_item.get('containerRefNumber', ''),
            'weight': shipment_data_item.get('packageWeight', 0),
            'dimension': shipment_data_item.get('packageDimension', 0),
            'description': shipment_data_item.get('packageNote'),
            'is_container': False,
            'reference_container': shipment_data_item.get('packageContainerRef'),
            'package_type_id': str(shipment_data_item.get("packageType", {}).get("id")),
        }

    @staticmethod
    def create_shipment(service_order_obj, shipment_data):
        bulk_info_shipment = []
        bulk_info_container = []
        for _, shipment_data_item in enumerate(shipment_data):
            item_data_parsed = ServiceOrderCommonFunc.get_mapped_data(shipment_data_item)
            shipment_obj = ServiceOrderShipment(
                service_order=service_order_obj,
                company=service_order_obj.company,
                tenant=service_order_obj.tenant,
                **item_data_parsed
            )
            bulk_info_shipment.append(shipment_obj)

            # get container
            ctn_order = 1
            if shipment_obj.is_container:
                bulk_info_container.append(ServiceOrderContainer(
                    service_order=service_order_obj,
                    shipment=shipment_obj,
                    order=ctn_order,
                    container_type_id=str(shipment_data_item.get("containerType", {}).get("id")),
                    company=service_order_obj.company,
                    tenant=service_order_obj.tenant,
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
                        service_order=service_order_obj,
                        shipment=ctn_mapped.shipment,
                        order=pkg_order,
                        package_type_id=str(shipment_data_item.get("packageType", {}).get("id")),
                        container_reference_id=str(ctn_mapped.id),
                        company=service_order_obj.company,
                        tenant=service_order_obj.tenant,
                    ))
                    pkg_order += 1

        # bulk create package
        ServiceOrderPackage.objects.bulk_create(bulk_info_packages)
        return True

    @staticmethod
    def create_expense(service_order_obj, expense_data):
        bulk_info_expense = []
        for expense_data_item in expense_data:
            expense_item_obj = expense_data_item.get('expense_item')
            uom_obj = expense_data_item.get('uom')
            tax_obj = expense_data_item.get('tax')

            expense_obj = ServiceOrderExpense(
                service_order=service_order_obj,
                title=expense_data_item.get('expense_name'),
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
                quantity=expense_data_item.get('quantity', 0),
                expense_price=expense_data_item.get('expense_price', 0),
                tax=tax_obj,
                tax_data={
                    "id": str(tax_obj.id),
                    "code": tax_obj.code,
                    "title": tax_obj.title,
                    "rate": tax_obj.rate
                } if tax_obj else {},
                subtotal_price=expense_data_item.get('subtotal', 0)
            )
            bulk_info_expense.append(expense_obj)

        # bulk create expense
        ServiceOrderExpense.objects.filter(service_order=service_order_obj).delete()
        ServiceOrderExpense.objects.bulk_create(bulk_info_expense)

        return True


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
    expense_name = serializers.CharField()
    expense_item = serializers.UUIDField(required=False, allow_null=True)
    uom = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.FloatField(required=False, allow_null=True)
    expense_price = serializers.FloatField(required=False, allow_null=True)
    tax = serializers.UUIDField(required=False, allow_null=True)
    subtotal = serializers.FloatField(required=False, allow_null=True)

    @classmethod
    def validate_expense_item(cls, value):
        try:
            expense_item_obj = ExpenseItem.objects.get(id=value)
            return expense_item_obj
        except ExpenseItem.DoesNotExist:
            raise serializers.ValidationError({'expense_item': SVOMsg.EXPENSE_ITEM_NOT_EXIST})

    @classmethod
    def validate_uom(cls, value):
        try:
            uom_obj = UnitOfMeasure.objects.get(id=value)
            return uom_obj
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': SVOMsg.UOM_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                tax_obj = Tax.objects.get(id=value)
                return tax_obj
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'tax': SVOMsg.TAX_NOT_EXIST})
        return None


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
    expense_pretax_value = serializers.FloatField(required=False, allow_null=True)
    expense_tax_value = serializers.FloatField(required=False, allow_null=True)
    expense_total_value = serializers.FloatField(required=False, allow_null=True)
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
            service_order_obj = ServiceOrder.objects.create(**validated_data)
            ServiceOrderCommonFunc.create_shipment(service_order_obj, shipment_data)
            ServiceOrderCommonFunc.create_expense(service_order_obj, expense_data)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
                model_cls=ServiceOrderAttachMapAttachFile,
                instance=service_order_obj,
                attachment_result=attachment
            )
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
            'attachment'
        )


class ServiceOrderDetailSerializer(AbstractDetailSerializerModel):
    shipment = serializers.SerializerMethodField()
    expense = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    @classmethod
    def get_shipment(cls, obj):
        shipment_list = []
        for item in obj.service_order_shipment_service_order.all():
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
                    'is_container': True
                })
            else:
                shipment_list.append({
                    'id': str(item.id),
                    'packageName': item.title,
                    'packageType': {
                        'id': str(item.package_type.id),
                        'code': item.package_type.code,
                        'title': item.package.title,
                    },
                    'packageRefNumber': item.reference_number,
                    'packageWeight': item.weight,
                    'packageDimension': item.dimension,
                    'packageNote': item.description,
                    'is_container': False
                })
        return shipment_list

    @classmethod
    def get_expense(cls, obj):
        expense_list = obj.service_order_expense_service_order.all().select_related(
            'expense_item',
            'uom',
            'tax'
        )
        pass

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]

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
            'expense',
            'expense_pretax_value',
            'expense_tax_value',
            'expense_total_value',
            'attachment'
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
