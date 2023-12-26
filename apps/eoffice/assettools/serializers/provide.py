__all__ = ['AssetToolsProvideCreateSerializer', 'AssetToolsProvideListSerializer']

from rest_framework import serializers

from ..models import AssetToolsProvide, AssetToolsProvideProduct
from apps.shared import HRMsg, ProductMsg


class AssetToolsProvideMapProductSerializer(serializers.Serializer):  # noqa
    product = serializers.UUIDField()
    order = serializers.IntegerField()
    tax = serializers.UUIDField(allow_null=True, required=False)
    uom = serializers.UUIDField()
    quantity = serializers.FloatField()
    price = serializers.FloatField()
    subtotal = serializers.FloatField()
    product_remark = serializers.CharField()


def create_products(instance, prod_list):
    AssetToolsProvideProduct.objects.filter(asset_tools_provide=instance).delete()
    create_lst = []
    for item in prod_list:
        temp = AssetToolsProvideProduct(
            product=item.product,
            order=item.order,
            tax=item.tax,
            uom=item.uom,
            quantity=item.quantity,
            price=item.price,
            subtotal=item.subtotal,
            product_remark=item.product_remark

        )
        temp.before_save()
        create_lst.append(temp)
    AssetToolsProvideProduct.objects.bulk_create(create_lst)


class AssetToolsProvideCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    products = AssetToolsProvideMapProductSerializer(many=True)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_products(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': ProductMsg.DOES_NOT_EXIST})
        return value

    def create(self, validated_data):
        prod_list = validated_data['products']
        del validated_data['products']
        asset_tools_provide = AssetToolsProvide.objects.create(**validated_data)
        create_products(asset_tools_provide, prod_list)
        # handle_attach_file(user, business_request, validated_data)
        return asset_tools_provide

    class Meta:
        model = AssetToolsProvide
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachments',
            'products',
            'date_created',
            'system_status',
            'pretax_amount',
            'taxes',
            'total_amount',
        )


class AssetToolsProvideListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "full_name": obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    class Meta:
        model = AssetToolsProvide
        fields = (
            'id',
            'title',
            'employee_inherit',
            'code',
            'system_status',
            'date_created'
        )
