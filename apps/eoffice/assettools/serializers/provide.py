__all__ = ['AssetToolsProvideCreateSerializer', 'AssetToolsProvideListSerializer', 'AssetToolsProvideDetailSerializer',
           'AssetToolsProvideUpdateSerializer']

from rest_framework import serializers

from apps.shared import HRMsg, ProductMsg, AbstractDetailSerializerModel, SYSTEM_STATUS
from apps.core.workflow.tasks import decorator_run_workflow
from ..models import AssetToolsProvide, AssetToolsProvideProduct


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
            asset_tools_provide=instance,
            product_id=item['product'],
            order=item['order'],
            tax_id=item['tax'],
            uom_id=item['uom'],
            quantity=item['quantity'],
            price=item['price'],
            subtotal=item['subtotal'],
            product_remark=item['product_remark']
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

    @decorator_run_workflow
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


class AssetToolsProvideDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()  # noqa
    system_status = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = AssetToolsProvide
        fields = ('id', 'title', 'code', 'employee_inherit',
                  'remark',
                  'attachments',
                  'products',
                  'date_created',
                  'pretax_amount',
                  'taxes',
                  'total_amount',
                  'system_status')

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": obj.employee_inherit.get_full_name()
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None

    @classmethod
    def get_products(cls, obj):
        if obj.products:
            products_list = []
            for item in list(obj.asset_provide_map_product.all()):
                products_list.append(
                    {
                        'id': item.id,
                        'product': item.product_data if hasattr(item, 'product_data') else {},
                        'order': item.order,
                        'product_remark': item.product_remark,
                        'uom': item.uom_data if hasattr(item, 'uom_data') else {},
                        'tax': item.tax_data if hasattr(item, 'tax_data') else {},
                        'quantity': item.quantity,
                        'price': item.price,
                        'subtotal': item.subtotal
                    }
                )
            return products_list
        return []


class AssetToolsProvideUpdateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    products = AssetToolsProvideMapProductSerializer(many=True, required=False)

    class Meta:
        model = AssetToolsProvide
        fields = ('title', 'code', 'employee_inherit_id',
                  'remark',
                  'attachments',
                  'products',
                  'date_created',
                  'pretax_amount',
                  'taxes',
                  'total_amount',
                  'system_status')

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    def update(self, instance, validated_data):
        products = []
        if 'products' in validated_data and validated_data['products']:
            del validated_data['products']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if products:
            create_products(instance, products)
        return instance
