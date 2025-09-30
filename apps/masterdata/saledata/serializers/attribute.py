from rest_framework import serializers

from apps.masterdata.saledata.models import Attribute, AttributeNumeric, AttributeList, AttributeWarranty, \
    AttributeListItem
from apps.masterdata.saledata.models.product import Product
from apps.shared import BaseMsg


class AttributeListSerializer(serializers.ModelSerializer):
    parent_n = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = (
            'id',
            'title',
            'parent_n',
            'price_config_type',
            'price_config_data',
            'is_category',
            'is_inventory',
        )

    @classmethod
    def get_parent_n(cls, obj):
        return {
            'id': obj.parent_n_id,
            'title': obj.parent_n.title,
            'code': obj.parent_n.code,
        } if obj.parent_n else {}


class AttributeHandler:

    @classmethod
    def create_update_subs(cls, attribute):
        if attribute.is_category is False:
            if attribute.price_config_type == 0:
                attribute.attribute_numeric_attribute.all().delete()
                AttributeNumeric.objects.create(
                    attribute=attribute,
                    tenant_id=attribute.tenant_id,
                    company_id=attribute.company_id,
                    **attribute.price_config_data
                )

            if attribute.price_config_type == 1:
                attribute.attribute_list_item_attribute.all().delete()
                attribute.attribute_list_attribute.all().delete()
                attribute_list = AttributeList.objects.create(
                    attribute=attribute,
                    tenant_id=attribute.tenant_id,
                    company_id=attribute.company_id,
                    **attribute.price_config_data
                )
                if attribute_list:
                    AttributeListItem.objects.bulk_create([AttributeListItem(
                        attribute=attribute,
                        attribute_list=attribute_list,
                        tenant_id=attribute.tenant_id,
                        company_id=attribute.company_id,
                        **list_item,
                    ) for list_item in attribute_list.list_item])

            if attribute.price_config_type == 2:
                attribute.attribute_warranty_attribute.all().delete()
                AttributeWarranty.objects.bulk_create([
                    AttributeWarranty(
                        attribute=attribute,
                        tenant_id=attribute.tenant_id,
                        company_id=attribute.company_id,
                        **warranty_item,
                    ) for warranty_item in attribute.price_config_data.get('warranty_item', [])
                ])
        return True


class AttributeCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Attribute
        fields = (
            'title',
            'parent_n',
            'price_config_type',
            'price_config_data',
            'is_category',
            'is_inventory',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            if value is None:
                return value
            return Attribute.objects.get_on_company(id=value)
        except Attribute.DoesNotExist:
            raise serializers.ValidationError({'parent': BaseMsg.NOT_EXIST})

    def create(self, validated_data):
        attribute = Attribute.objects.create(**validated_data)
        AttributeHandler.create_update_subs(attribute=attribute)

        return attribute


class AttributeUpdateSerializer(serializers.ModelSerializer):
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Attribute
        fields = (
            'title',
            'parent_n',
            'price_config_type',
            'price_config_data',
            'is_category',
            'is_inventory',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            if value is None:
                return value
            return Attribute.objects.get_on_company(id=value)
        except Attribute.DoesNotExist:
            raise serializers.ValidationError({'parent': BaseMsg.NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        AttributeHandler.create_update_subs(attribute=instance)
        return instance


class ProductAttributeDetailSerializer(serializers.ModelSerializer):
    attribute_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'attribute_list',
        )

    @classmethod
    def get_attribute_list(cls, obj):
        attribute_list = []

        for product_attribute in obj.product_attributes.all():
            attribute = product_attribute.attribute  # the related Attribute object

            # Check if this attribute is a category
            if attribute and attribute.is_category:
                # Get all child attributes of this category
                child_attributes = Attribute.objects.filter(
                    parent_n=attribute,
                    is_category=False  # Only get attribute
                )

                for child_attr in child_attributes:
                    attribute_list.append({
                        'id': child_attr.id,
                        'title': child_attr.title,
                        'price_config_type': child_attr.price_config_type,
                        'price_config_data': child_attr.price_config_data,
                        'is_category': child_attr.is_category,
                        'is_inventory': child_attr.is_inventory,
                        'parent_n': {
                            'id': attribute.id,
                            'title': attribute.title,
                            'code': attribute.code,
                        },
                    })

        return attribute_list
