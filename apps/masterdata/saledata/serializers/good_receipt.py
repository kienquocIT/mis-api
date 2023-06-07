from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.shared import GRMsg

from ..models import WareHouseStock, GoodReceipt, Account, GoodReceiptProduct

__all__ = ['GoodReceiptListSerializer', 'GoodReceiptCreateSerializer', 'GoodReceiptDetailSerializer',
           'GoodReceiptUpdateSerializer']


class ProductListUtil:
    @staticmethod
    def sub_update_good_receipt(new_product_list_ids, prod_check, instance):
        for old_prod in prod_check:
            if str(old_prod.product_id) in new_product_list_ids:
                # nếu prod cũ có trong prod mới
                prod_warehouse = WareHouseStock.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    product=old_prod.product,
                    warehouse=old_prod.warehouse
                ).first()
                if old_prod.warehouse_id == new_product_list_ids[str(old_prod.product_id)][
                    'warehouse'].id and old_prod.quantity != new_product_list_ids[str(old_prod.product_id)][
                    'quantity']:
                    # 2 warehouse giống nhau so sánh lớn bé và update
                    # nếu 2 quantity cũ mới bằng nhau
                    prod_warehouse.stock += new_product_list_ids[
                                                str(old_prod.product_id)][
                                                'quantity'] - old_prod.quantity
                else:
                    # 2 warehouse khác nhau
                    # 1 trừ stock nhánh cũ
                    prod_warehouse.stock += -int(old_prod.quantity)
                    new_prod_warehouse = WareHouseStock.objects.filter_current(
                        fill__tenant=True,
                        fill__company=True,
                        product=new_product_list_ids[str(old_prod.product_id)]['product'],
                        warehouse=new_product_list_ids[str(old_prod.product_id)]['warehouse']
                    )
                    if new_prod_warehouse.exists():
                        # kiểm tra prod mới có chưa
                        new_prod_warehouse = new_prod_warehouse.first()

                        if new_prod_warehouse.stock != new_product_list_ids[str(old_prod.product_id)][
                            'quantity']:
                            # kiểm tra stock > or < hơn
                            new_prod_warehouse.stock += new_product_list_ids[
                                str(old_prod.product_id)][
                                'quantity']
                            new_prod_warehouse.save(update_fields=['stock'])
                    else:
                        #   ko có tạo mới với stock mới
                        WareHouseStock.objects.create(
                            company_id=instance.company_id,
                            tenant_id=instance.tenant_id,
                            product=new_product_list_ids[str(old_prod.product_id)]['product'],
                            warehouse=new_product_list_ids[str(old_prod.product_id)]['warehouse'],
                            stock=new_product_list_ids[str(old_prod.product_id)]['quantity']
                        )
                prod_warehouse.save(update_fields=['stock'])
            else:
                # nếu prod cũ ko có trong prod mới
                # trừ prod vs warehouse cũ
                old_prod_stock = WareHouseStock.objects.filter(
                    product=old_prod.product,
                    warehouse=old_prod.warehouse
                )
                old_prod_stock.stock += -int(old_prod.quantity)
                old_prod_stock.save(update_fields=['stock'])

    @classmethod
    def handle_product_stock(cls, instance, new_prod, prod_check):
        new_product_list = new_prod
        new_product_list_ids = {str(item['product'].id): {
            'product': item['product'],
            'warehouse': item['warehouse'],
            'quantity': item['quantity']
        } for item in new_product_list}
        try:
            with transaction.atomic():
                if not prod_check.exists():
                    # tạo mới good receipt
                    prod_create_temp = []
                    for item in new_product_list:
                        product = WareHouseStock.objects.filter_current(
                            fill__tenant=True,
                            fill__company=True,
                            product=item['product'],
                            warehouse=item['warehouse']
                        )
                        if product.exists():
                            # moi cong ty chi co mot uuid san pham duy nhat nen co the .first()
                            product = product.first()
                            product.stock += item['quantity']
                            product.save(update_fields=['stock'])
                        else:
                            prod_create_temp.append(
                                WareHouseStock(
                                    company_id=instance.company_id,
                                    tenant_id=instance.tenant_id,
                                    product=item['product'],
                                    warehouse=item['warehouse'],
                                    stock=item['quantity']
                                )
                            )
                    WareHouseStock.objects.bulk_create(prod_create_temp)
                else:
                    # update good receipt
                    cls.sub_update_good_receipt(new_product_list_ids, prod_check, instance)

        except Exception as err:
            print('update stock for warehouse Stock is error---\n', err)
            raise serializers.ValidationError(
                {
                    'products': _(
                        'Sync stock product failure. please contact support'
                    )
                }
            )

    @staticmethod
    def create_update_product_list(product_list, instance):
        """
        step 1: kiểm tra ds theo good_receipt ko có thì delete đi
        step 2: tạo objs mới gọi func before_save add thêm field_data cho các Foreign key
        step 3: sau đó save bulk_create (do bulk_create ko chạy qua hàm before_save
        """
        if product_list and isinstance(product_list, list):
            check_pro_list = GoodReceiptProduct.objects.filter(good_receipt=instance)
            ProductListUtil.handle_product_stock(instance, product_list, check_pro_list)
            if check_pro_list.count():
                check_pro_list.delete()
            objs = []
            for prod in product_list:
                obj = GoodReceiptProduct(**prod, good_receipt=instance)
                obj.before_save()
                objs.append(obj)

            GoodReceiptProduct.objects.bulk_create(objs)


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
