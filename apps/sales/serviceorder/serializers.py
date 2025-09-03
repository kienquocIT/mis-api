from django.db import transaction
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderPackage, ServiceOrderContainer, ServiceOrderShipment,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel, AttachmentMsg,
    SerializerCommonValidate, SerializerCommonHandle,
)

__all__ = [
    'ServiceOrderListSerializer',
    'ServiceOrderDetailSerializer',
    'ServiceOrderCreateSerializer',
    'ServiceOrderUpdateSerializer',
]


# ================================ COMMON FUNC =====================================
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
    def assign_packages_to_containers(shipment, packages_data):
        containers = ServiceOrderContainer.objects.filter(shipment=shipment)

        container_list = list(containers)
        package_list = []

        for i, package_data in enumerate(packages_data):
            target_container = container_list[i % len(container_list)]


    @staticmethod
    def create_service_order_packages(shipment, container, packages_data):
        package_list = []

        for item in packages_data:
            package = ServiceOrderPackage(
                shipment_id=str(shipment.id),
                container_reference_id=str(container.id),
                order=item.get('order', 1),
                package_type_id=item.get('package_type')
            )
            package_list.append(package)

        # bulk create packages
        ServiceOrderPackage.objects.bulk_create(package_list)
        return True

    @staticmethod
    def create_service_order_containers(shipment, containers_data):
        container_list = []
        all_packages_data = []
        for item in containers_data:
            packages_data = item.pop('packages', [])

            container = ServiceOrderContainer(
                shipment_id=str(shipment.id),
                order=item.get('order', 1),
                container_type_id=item.get('container_type'),
            )
            container_list.append(container)
            all_packages_data.append(packages_data)

        # bulk create containers
        created_containers = ServiceOrderContainer.objects.bulk_create(container_list)

        # create packages for each container
        for i, container in enumerate(created_containers):
            packages_data = all_packages_data[i]
            if packages_data:
                ServiceOrderCommonFunc.create_service_order_packages(shipment, container, packages_data)
        return True

    @staticmethod
    def create_service_order_shipment(service_order, shipment_data):
        containers_data = shipment_data.pop('containers', [])
        packages_data = shipment_data.pop('packages', [])

        shipment = ServiceOrderShipment.objects.create(
            service_order_id=str(service_order.id),
            reference_number=shipment_data.get('reference_number', ''),
            weight=shipment_data.get('weight', 0),
            dimension=shipment_data.get('dimension', 0),
            description=shipment_data.get('description', ''),
            is_container=shipment_data.get('is_container', True),
            company=service_order.company,
            tenant=service_order.tenant
        )

        if containers_data:
            ServiceOrderCommonFunc.create_service_order_containers(shipment, containers_data)
        if packages_data:
            ServiceOrderCommonFunc.assign_packages_to_containers(shipment, packages_data)

        return True


# ================================ SHIPMENT =====================================
class ServiceOrderPackageSerializer(serializers.Serializer):
    order = serializers.IntegerField(default=1)
    package_type = serializers.CharField(required=False, allow_null=True)
    package_type_title = serializers.CharField(read_only=True)


class ServiceOrderContainerSerializer(serializers.Serializer):
    order = serializers.IntegerField(default=1)
    container_type = serializers.CharField(required=False, allow_null=True)
    packages = ServiceOrderPackageSerializer(many=True, required=False)
    container_type_title = serializers.CharField(read_only=True)


class ServiceOderShipmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    reference_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    weight = serializers.FloatField(default=0)
    dimension = serializers.FloatField(default=0)
    description = serializers.CharField(required=True, allow_blank=True)
    is_container = serializers.BooleanField(default=True)

    # nested containers
    containers = ServiceOrderContainerSerializer(many=True, required=False)
    packages = ServiceOrderPackageSerializer(many=True, required=False)


# ================================ MAIN =====================================
class ServiceOrderListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'date_created',
            'employee_created',
            'system_status'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ServiceOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    shipments = ServiceOderShipmentSerializer(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=ServiceOrderAttachMapAttachFile, value=value
        )

    def validate(self, validate_data):
        start_date = validate_data.get('start_date', '')
        end_date = validate_data.get('end_date', '')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        with transaction.atomic():
            shipments = validated_data.pop('shipments', [])
            attachment = validated_data.pop('attachment', [])
            service_order = ServiceOrder.objects.create(**validated_data)
            ServiceOrderCommonFunc.create_service_order_shipments(service_order.id, shipments)
            ServiceOrderCommonFunc.create_attachment(service_order.id, attachment)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
                model_cls=ServiceOrderAttachMapAttachFile,
                instance=service_order,
                attachment_result=attachment
            )
        return service_order

    class Meta:
        model = ServiceOrder
        fields = (
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipments',
            'attachment'
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
