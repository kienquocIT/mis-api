from django.db import transaction
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderAttachMapAttachFile, ServiceOrderPackage, ServiceOrderContainer, ServiceOrderShipment,
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
    def create_shipment(service_order, shipment_data):
        # new_shipment = []
        # for shipment in shipment_data:
        #
        # pass
        pass


# SHIPMENT
class ServiceOderShipmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    reference_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    weight = serializers.FloatField(default=0)
    dimension = serializers.FloatField(default=0)
    description = serializers.CharField(required=True, allow_blank=True)
    reference_container = serializers.CharField(max_length=100, required=False, allow_null=True)
    is_container = serializers.BooleanField(default=True)

    class Meta:
        model = ServiceOrderShipment
        fields = (
            'title',
            'reference_number',
            'weight',
            'dimension',
            'description',
            'is_container',
            'reference_container'
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
    customer = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    shipment = ServiceOderShipmentSerializer(many=True)
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
            "id": customer_obj.id,
            "title": customer_obj.title,
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
            shipment = validated_data.pop('shipment', [])
            attachment = validated_data.pop('attachment', [])
            service_order = ServiceOrder.objects.create(**validated_data)
            ServiceOrderCommonFunc.create_service_order_shipments(service_order.id, shipment)
            # ServiceOrderCommonFunc.create_attachment(service_order.id, attachment)
            # SerializerCommonHandle.handle_attach_file(
            #     relate_app=Application.objects.filter(id="36f25733-a6e7-43ea-b710-38e2052f0f6d").first(),
            #     model_cls=ServiceOrderAttachMapAttachFile,
            #     instance=service_order,
            #     attachment_result=attachment
            # )
        return service_order

    class Meta:
        model = ServiceOrder
        fields = (
            'title',
            'customer',
            'start_date',
            'end_date',
            'shipment',
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
