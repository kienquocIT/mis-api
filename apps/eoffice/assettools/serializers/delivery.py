__all__ = [
    'AssetToolsDeliveryCreateSerializer', 'AssetToolsDeliveryDetailSerializer', 'AssetToolsProductUsedListSerializer',
    'AssetToolsDeliveryListSerializer', 'AssetToolsDeliveryUpdateSerializer'
]

from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.assettools.models import AssetToolsDeliveryAttachmentFile, AssetToolsDelivery, \
    ProductDeliveredMapProvide
from apps.shared import HRMsg, ProductMsg, AbstractDetailSerializerModel
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.eoffices import AssetToolsMsg


class AssetToolsProductsMapDeliverySerializer(serializers.Serializer):  # noqa
    product = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    order = serializers.IntegerField()
    request_number = serializers.FloatField()
    delivered_number = serializers.FloatField()
    done = serializers.IntegerField()
    date_delivered = serializers.DateTimeField()
    is_inventory = serializers.BooleanField()


def create_products(instance, prod_list):
    old_data = ProductDeliveredMapProvide.objects.filter(delivery=instance)
    if old_data.exists():
        old_data.delete()
    create_lst = []
    for item in prod_list:
        date_delivered = timezone.now()
        if isinstance(item['date_delivered'], datetime):
            date_delivered.replace(
                year=item['date_delivered'].year, month=item['date_delivered'].month, day=item['date_delivered'].day
            )
        temp = ProductDeliveredMapProvide(
            tenant=instance.tenant,
            company=instance.company,
            delivery=instance,
            order=item['order'],
            product_id=item['product'],
            warehouse_id=item['warehouse'],
            employee_inherit=instance.employee_inherit,
            request_number=item['request_number'],
            delivered_number=item['delivered_number'],
            done=item['done'],
            date_delivered=date_delivered,
            is_inventory=item['is_inventory']
        )
        temp.before_save()
        create_lst.append(temp)
    ProductDeliveredMapProvide.objects.bulk_create(create_lst)
    return True


def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="41abd4e9-da89-450b-a44a-da1d6f8a5cd2")
        state = AssetToolsDeliveryAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class AssetToolsDeliveryCreateSerializer(serializers.ModelSerializer):
    products = AssetToolsProductsMapDeliverySerializer(many=True)
    attachments = serializers.ListSerializer(allow_null=True, required=False, child=serializers.UUIDField())
    employee_inherit_id = serializers.UUIDField()

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return str(value)

    def validate_attachments(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = AssetToolsDeliveryAttachmentFile.valid_change(
                current_ids=[str(idx) for idx in attrs], employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_products(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': ProductMsg.DOES_NOT_EXIST})
        return value

    @classmethod
    def validate_provide(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': AssetToolsMsg.EMPTY_PROVIDE})
        return value

    @decorator_run_workflow
    def create(self, validated_data):
        products_list = validated_data.pop('products', None)
        attachments = validated_data.pop('attachments', None)
        delivery = AssetToolsDelivery.objects.create(**validated_data)
        create_products(delivery, products_list)
        handle_attach_file(delivery, attachments)
        return delivery

    class Meta:
        model = AssetToolsDelivery
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachments',
            'provide',
            'products',
            'date_created',
            'system_status',
        )


class AssetToolsDeliveryDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    provide = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        if obj.products:
            products_list = []
            for item in list(obj.provide_map_delivery.all()):
                products_list.append(
                    {
                        'order': item.order,
                        'product_available': item.product.stock_amount,
                        'product': {**item.product_data, } if hasattr(item, 'product_data') else {},
                        'warehouse': item.warehouse_data if hasattr(item, 'warehouse_data') else {},
                        'request_number': item.request_number,
                        'delivered_number': item.delivered_number,
                        'done': item.done,
                        'date_delivered': item.date_delivered,
                    }
                )
            return products_list
        return []

    @classmethod
    def get_provide(cls, obj):
        return obj.provide_data if obj.provide_data else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit_data if obj.employee_inherit_data else {}

    class Meta:
        model = AssetToolsDelivery
        fields = (
            'id',
            'title',
            'code',
            'products',
            'employee_inherit',
            'remark',
            'attachments',
            'provide',
            'date_created',
            'system_status',
        )


class AssetToolsDeliveryListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit_data if obj.employee_inherit_data else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': str(obj.employee_created.id),
            'full_name': obj.employee_created.get_full_name(),
        } if obj.employee_created else {}

    class Meta:
        model = AssetToolsDelivery
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'employee_created',
            'date_created',
            'system_status'
        )


class AssetToolsProductUsedListSerializer(serializers.ModelSerializer):
    # employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit_data if obj.employee_inherit else {}

    class Meta:
        model = ProductDeliveredMapProvide
        fields = (
            'product_data',
            'done'
        )


class AssetToolsDeliveryUpdateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    products = AssetToolsProductsMapDeliverySerializer(many=True, required=False)

    class Meta:
        model = AssetToolsDelivery
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachments',
            'provide',
            'products',
            'date_created',
            'system_status',
        )

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    def validate_attachments(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = AssetToolsDeliveryAttachmentFile.valid_change(
                current_ids=[str(idx) for idx in attrs], employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def update(self, instance, validated_data):
        attachments = validated_data.pop('attachments', None)
        products = validated_data.pop('products', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if products is not None:
            create_products(instance, products)

        if attachments is not None:
            handle_attach_file(instance, attachments)
        return instance
