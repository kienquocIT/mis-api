__all__ = ['AssetToolsProvideCreateSerializer', 'AssetToolsProvideListSerializer', 'AssetToolsProvideDetailSerializer',
           'AssetToolsProvideUpdateSerializer', 'AssetToolsProductListByProvideIDSerializer']

from rest_framework import serializers

from apps.core.base.models import Application
from apps.shared import HRMsg, ProductMsg, AbstractDetailSerializerModel, SYSTEM_STATUS
from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared.translations.base import AttachmentMsg
from ..models import AssetToolsProvide, AssetToolsProvideProduct, AssetToolsProvideAttachmentFile


class AssetToolsProvideMapProductSerializer(serializers.Serializer):  # noqa
    order = serializers.IntegerField()
    product = serializers.UUIDField()
    product_remark = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    uom = serializers.UUIDField()
    tax = serializers.UUIDField(allow_null=True, required=False)
    quantity = serializers.FloatField(allow_null=True, required=False)
    price = serializers.FloatField(allow_null=True, required=False)
    subtotal = serializers.FloatField(allow_null=True, required=False)


def create_products(instance, prod_list):
    AssetToolsProvideProduct.objects.filter(asset_tools_provide=instance).delete()
    create_lst = []
    for item in prod_list:
        temp = AssetToolsProvideProduct(
            company=instance.company,
            tenant=instance.tenant,
            employee_inherit=instance.employee_inherit,
            asset_tools_provide=instance,
            order=item['order'],
            product_id=item['product'],
            product_remark=item['product_remark'],
            uom_id=item['uom'],
            quantity=item['quantity'],
            tax_id=item['tax'] if 'tax' in item else None,
            price=item['price'] if 'price' in item else 0,
            subtotal=item['subtotal'] if 'subtotal' in item else 0,
        )
        temp.before_save()
        create_lst.append(temp)
    AssetToolsProvideProduct.objects.bulk_create(create_lst)


def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="55ba3005-6ccc-4807-af27-7cc45e99e3f6")
        state = AssetToolsProvideAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class AssetToolsProvideCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    products = AssetToolsProvideMapProductSerializer(many=True)
    attachments = serializers.ListSerializer(allow_null=True, required=False, child=serializers.UUIDField())

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

    def validate_attachments(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = AssetToolsProvideAttachmentFile.valid_change(
                current_ids=[str(idx) for idx in attrs], employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validated_data):
        prod_list = validated_data['products']
        del validated_data['products']
        attachments = validated_data.pop('attachments', None)
        asset_tools_provide = AssetToolsProvide.objects.create(**validated_data)
        create_products(asset_tools_provide, prod_list)
        handle_attach_file(asset_tools_provide, attachments)
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
    attachments = serializers.SerializerMethodField()

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
                  'system_status',

                  )

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
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

    @classmethod
    def get_attachments(cls, obj):
        att_objs = AssetToolsProvideAttachmentFile.objects.select_related('attachment').filter(asset_tools_provide=obj)
        return [item.attachment.get_detail() for item in att_objs]


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

    def validate_attachments(self, attrs):
        user = self.context.get('user', None)
        instance = self.instance
        if user and hasattr(user, 'employee_current_id') and instance and hasattr(instance, 'id'):
            state, result = AssetToolsProvideAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=instance.id
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


class AssetToolsProductListByProvideIDSerializer(serializers.ModelSerializer):
    product_available = serializers.SerializerMethodField()
    product_warehouse = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    @classmethod
    def get_product_available(cls, obj):
        if obj.product:
            prod_warehouse = obj.product.product_warehouse_product.all()
            temp = {}
            for warehouse in prod_warehouse:
                temp[str(warehouse.warehouse.id)] = warehouse.stock_amount - warehouse.used_amount if warehouse else 0
            return temp

        return 0

    @classmethod
    def get_product_warehouse(cls, obj):
        if obj.product:
            prod_warehouse = obj.product.product_warehouse_product.all()
            return [{
                "id": str(warehouse.warehouse.id),
                "title": warehouse.warehouse.title
            } for warehouse in prod_warehouse
            ]
        return []

    @classmethod
    def get_product(cls, obj):
        if obj.product_data:
            return obj.product_data
        return {}

    class Meta:
        model = AssetToolsProvideProduct
        fields = (
            'product',
            'uom_data',
            'product_available',
            'product_warehouse',
            'order',
            'quantity',
            'delivered',
        )
