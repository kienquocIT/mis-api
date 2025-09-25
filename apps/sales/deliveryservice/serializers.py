from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.deliveryservice.models import DeliveryService, DeliveryServiceAttachmentFile, DeliveryServiceItem
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SerializerCommonValidate, SerializerCommonHandle
)


__all__ = [
    'DeliveryServiceListSerializer',
    'DeliveryServiceDetailSerializer',
    'DeliveryServiceCreateSerializer',
    'DeliveryServiceUpdateSerializer',
]


class DeliveryServiceListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryService
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'employee_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class DeliveryServiceCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = DeliveryService
        fields = (
            'title',
            'attachment'
        )

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=DeliveryServiceAttachmentFile, value=value
        )

    def validate(self, validate_data):
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        data_item_list = validated_data.pop('data_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        delivery_service_obj = DeliveryService.objects.create(**validated_data)

        DeliveryServiceCommonFunc.create_items_mapped(delivery_service_obj, data_item_list)
        DeliveryServiceCommonFunc.create_files_mapped(delivery_service_obj, attachment_list)

        return delivery_service_obj


class DeliveryServiceDetailSerializer(AbstractDetailSerializerModel):
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryService
        fields = (
            'id',
            'code',
            'title',
            'attachment',
        )

    @classmethod
    def get_attachment(cls, obj):
        return [item.attachment.get_detail() for item in obj.delivery_service_attachments.all()]


class DeliveryServiceUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = DeliveryService
        fields = (
            'title',
            'customer_mapped',
            'billing_address_id',
            'company_bank_account',
            'buyer_name',
            'invoice_method',
            'sale_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'note',
            'delivery_mapped_list',
            'data_item_list',
            'attachment'
        )

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=DeliveryServiceAttachmentFile, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        return DeliveryServiceCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        data_item_list = validated_data.pop('data_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        DeliveryServiceCommonFunc.create_items_mapped(instance, data_item_list)
        DeliveryServiceCommonFunc.create_files_mapped(instance, attachment_list)

        return instance


class DeliveryServiceCommonFunc:
    @staticmethod
    def create_items_mapped(delivery_service_obj, data_item_list):
        bulk_data = []
        for order, item in enumerate(data_item_list):
            bulk_data.append(DeliveryServiceItem(delivery_service=delivery_service_obj, order=order, **item))
        DeliveryServiceItem.objects.filter(delivery_service=delivery_service_obj).delete()
        DeliveryServiceItem.objects.bulk_create(bulk_data)
        return True

    @staticmethod
    def create_files_mapped(delivery_service_obj, attachment_list):
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id=DeliveryService.get_app_id()).first(),
            model_cls=DeliveryServiceAttachmentFile,
            instance=delivery_service_obj,
            attachment_result=attachment_list,
        )
        return True
