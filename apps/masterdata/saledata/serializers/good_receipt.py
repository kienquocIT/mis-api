from rest_framework import serializers
from apps.shared import GRMsg

from apps.masterdata.saledata.models import ( GoodReceipt, Account, GoodReceiptProduct, ProductWareHouse)

__all__ = ['GoodReceiptListSerializer', 'GoodReceiptCreateSerializer', 'GoodReceiptDetailSerializer',
           'GoodReceiptUpdateSerializer']


class ProductListUtil:

    @staticmethod
    def create_update_product_list(product_list, instance):
        """
        step 1: kiểm tra ds theo good_receipt ko có thì delete đi
        step 2: tạo objs mới gọi func before_save add thêm field_data cho các Foreign key
        step 3: sau đó save bulk_create (do bulk_create ko chạy qua hàm before_save
        """
        if product_list and isinstance(product_list, list):
            check_pro_list = GoodReceiptProduct.objects.filter(good_receipt=instance)
            if check_pro_list.count():
                check_pro_list.delete()
            objs = []
            for prod in product_list:
                obj = GoodReceiptProduct(**prod, good_receipt=instance)
                obj.before_save()
                objs.append(obj)

            GoodReceiptProduct.objects.bulk_create(objs)

            # push data to ProductWareHouse
            for prod_receipt in objs:
                ProductWareHouse.push_from_receipt(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    product_id=prod_receipt.product_id,
                    warehouse_id=prod_receipt.warehouse_id,
                    uom_id=prod_receipt.uom_id,
                    tax_id=prod_receipt.tax_id,
                    amount=prod_receipt.quantity,
                    unit_price=prod_receipt.unit_price,
                )


class GoodReceiptListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = GoodReceipt
        fields = (
            'id',
            'code',
            'title',
            'supplier',
            'posting_date',
            'system_status'
        )

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code
            }
        return {}


class GoodReceiptProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodReceiptProduct
        fields = (
            'product',
            'warehouse',
            'uom',
            'quantity',
            'unit_price',
            'tax',
            'subtotal_price',
            'order'
        )


class GoodReceiptCreateSerializer(serializers.ModelSerializer):
    supplier = serializers.UUIDField(required=False)
    product_list = GoodReceiptProductSerializer(many=True)

    class Meta:
        model = GoodReceipt
        fields = (
            'title',
            'supplier',
            'posting_date',
            'product_list',
            'pretax_amount',
            'taxes',
            'total_amount',
        )

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.TITLE)
        return value

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError(GRMsg.SUPPLIER)

    @classmethod
    def validate_product_list(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.PRODUCT_LIST)
        return value

    @staticmethod
    def reparse_product_list(data):
        """
        parse data từ object của GoodReceiptProductSerializer sang json và trả vể cho hàm create hoặc update
        """
        arr = []
        for item in data:
            item = dict(item)
            arr.append(
                {
                    'product': str(item['product']) if 'product' in item else None,
                    'warehouse': str(item['warehouse']) if 'warehouse' in item else None,
                    'uom': str(item['uom']) if 'uom' in item else None,
                    'tax': str(item['tax']) if 'tax' in item else None,
                    "quantity": item['quantity'] if 'quantity' in item else None,
                    "unit_price": item['unit_price'] if 'unit_price' in item else None,
                    "subtotal_price": item['subtotal_price'] if 'subtotal_price' in item else None,
                    "order": item['order'] if 'order' in item else None,
                }
            )
        return arr

    def create(self, validated_data):
        """
        do product_list được valid từ serializer nên khi trả vể validate sẽ là object
        trước khi save data thì cần parse lại json đồng thời tạo mới bảng phụ bằng func create_update_product_list.
        """
        product_list = validated_data.pop('product_list', [])
        instance = GoodReceipt.objects.create(
            **validated_data, product_list=self.reparse_product_list(self.data['product_list'])
        )
        if instance:
            ProductListUtil.create_update_product_list(product_list, instance)
        return instance


class GoodReceiptDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField(required=False)
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = GoodReceipt
        fields = (
            'id',
            'code',
            'title',
            'supplier',
            'date_created',
            'posting_date',
            'product_list',
            'pretax_amount',
            'taxes',
            'total_amount',
        )

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code,
            }
        return {}

    @classmethod
    def get_product_list(cls, obj):
        pd_list = GoodReceiptProduct.objects.filter(good_receipt=obj.id)
        if pd_list:
            parse_list = []
            for item in pd_list:
                parse_list.append(
                    {
                        'product': item.product_data,
                        'warehouse': item.warehouse_data,
                        'uom': item.uom_data,
                        'tax': item.tax_data,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'subtotal_price': item.subtotal_price,
                        'order': item.order
                    }
                )
            return parse_list
        return []


class GoodReceiptUpdateSerializer(serializers.ModelSerializer):
    supplier = serializers.UUIDField(required=False)
    product_list = GoodReceiptProductSerializer(many=True)

    class Meta:
        model = GoodReceipt
        fields = (
            'title',
            'supplier',
            'posting_date',
            'product_list',
            'pretax_amount',
            'taxes',
            'total_amount',
        )

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.TITLE)
        return value

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError(GRMsg.SUPPLIER)

    @classmethod
    def validate_product_list(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.PRODUCT_LIST)
        return value

    def update(self, instance, validated_data):
        product_list = validated_data.pop('product_list', [])
        validated_data['product_list'] = []
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if instance:
            ProductListUtil.create_update_product_list(product_list, instance)
        return instance
