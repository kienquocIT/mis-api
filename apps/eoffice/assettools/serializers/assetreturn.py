__all__ = [
    'AssetToolsReturnCreateSerializer', 'AssetToolsReturnDetailSerializer', 'AssetToolsReturnListSerializer',
    'AssetToolsReturnUpdateSerializer'
]

from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.assettools.models import AssetToolsReturnAttachmentFile, AssetToolsReturn, AssetToolsReturnMapProduct
from apps.shared import HRMsg, ProductMsg, AbstractDetailSerializerModel
from apps.shared.translations.base import AttachmentMsg


class AssetToolsProductsMapReturnSerializer(serializers.Serializer):  # noqa
    product = serializers.UUIDField()
    warehouse_stored_product = serializers.UUIDField()
    order = serializers.IntegerField()
    return_number = serializers.FloatField()


def create_products(instance, prod_list):
    old_data = AssetToolsReturnMapProduct.objects.filter(asset_return=instance)
    if old_data.exists():
        old_data.delete()
    create_lst = []
    for item in prod_list:
        date_return = timezone.now()
        if isinstance(item['date_return'], datetime):
            date_return.replace(
                year=item['date_return'].year, month=item['date_return'].month, day=item['date_return'].day
            )
        temp = AssetToolsReturnMapProduct(
            tenant=instance.tenant,
            company=instance.company,
            order=item['order'],
            product=item['product'],
            warehouse_stored_product_id=item['warehouse'],
            employee_inherit=instance.employee_inherit,
            return_number=item['return_number'],
            date_return=date_return,
        )
        temp.before_save()
        create_lst.append(temp)
    AssetToolsReturnMapProduct.objects.bulk_create(create_lst)
    return True


def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="08e41084-4379-4778-9e16-c09401f0a66e")
        state = AssetToolsReturnAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class AssetToolsReturnCreateSerializer(serializers.ModelSerializer):
    products = AssetToolsProductsMapReturnSerializer(many=True)
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
            state, result = AssetToolsReturnAttachmentFile.valid_change(
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

    @decorator_run_workflow
    def create(self, validated_data):
        products_list = validated_data.pop('products', None)
        attachments = validated_data.pop('attachments', None)
        asset_return = AssetToolsReturn.objects.create(**validated_data)
        create_products(asset_return, products_list)
        handle_attach_file(asset_return, attachments)
        return asset_return

    class Meta:
        model = AssetToolsReturn
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachments',
            'products',
            'date_created',
            'system_status',
        )


class AssetToolsReturnDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        if obj.products:
            products_list = []
            for item in list(obj.product_map_asset_return.all()):
                products_list.append(
                    {
                        'order': item.order,
                        'product': item.product_data if hasattr(item, 'product_data') else {},
                        'return_number': item.request_number,
                    }
                )
            return products_list
        return []

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit_data if obj.employee_inherit_data else {}

    class Meta:
        model = AssetToolsReturn
        fields = (
            'id',
            'title',
            'code',
            'products',
            'employee_inherit',
            'remark',
            'attachments',
            'date_return',
            'system_status',
        )


class AssetToolsReturnListSerializer(serializers.ModelSerializer):
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
        model = AssetToolsReturn
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'employee_created',
            'date_return',
            'date_created',
            'system_status'
        )


class AssetToolsReturnUpdateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    products = AssetToolsProductsMapReturnSerializer(many=True, required=False)

    class Meta:
        model = AssetToolsReturn
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachments',
            'products',
            'date_return',
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
            state, result = AssetToolsReturnAttachmentFile.valid_change(
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
