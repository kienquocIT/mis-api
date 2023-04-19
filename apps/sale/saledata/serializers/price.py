from rest_framework import serializers
from apps.sale.saledata.models.price import (
    TaxCategory, Tax, Currency, Price, ProductPriceList
)
from apps.sale.saledata.models.product import Product
from apps.shared import PriceMsg


# Tax Category
class TaxCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = TaxCategory
        fields = ('id', 'title', 'description', 'is_default')


class TaxCategoryCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = TaxCategory
        fields = ('title', 'description')

    @classmethod
    def validate_title(cls, value):
        if TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": PriceMsg.TITLE_EXIST})
        return value


class TaxCategoryDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = TaxCategory
        fields = ('id', 'title', 'description', 'is_default')


class TaxCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = TaxCategory
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": PriceMsg.TITLE_EXIST})
        return value


# Tax
class TaxListSerializer(serializers.ModelSerializer):  # noqa
    category = serializers.SerializerMethodField()

    class Meta:
        model = Tax
        fields = ('id', 'code', 'title', 'rate', 'category', 'type')

    @classmethod
    def get_category(cls, obj):
        if obj.category:
            return {
                'id': obj.category_id,
                'title': obj.category.title,
            }
        return {}


class TaxCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=150)

    class Meta:
        model = Tax
        fields = ('title', 'code', 'rate', 'category', 'type')

    @classmethod
    def validate_code(cls, value):
        if Tax.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError({"code": PriceMsg.CODE_EXIST})
        return value


class TaxDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Tax
        fields = ('id', 'code', 'title', 'rate', 'category', 'type')


class TaxUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Tax
        fields = ('title', 'rate', 'category', 'type')


# Currency
class CurrencyListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Currency
        fields = ('id', 'abbreviation', 'title', 'rate', 'is_default', 'is_primary')


class CurrencyCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Currency
        fields = ('abbreviation', 'title', 'rate')

    @classmethod
    def validate_abbreviation(cls, value):
        if Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                abbreviation=value
        ).exists():
            raise serializers.ValidationError({"abbreviation": PriceMsg.ABBREVIATION_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
        return value

    @classmethod
    def validate_rate(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)
        return None


class CurrencyDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Currency
        fields = ('id', 'abbreviation', 'title', 'rate', 'is_default', 'is_primary')


class CurrencyUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Currency
        fields = ('abbreviation', 'title', 'rate', 'is_primary')

    def validate_abbreviation(self, value):
        if value != self.instance.abbreviation and Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                abbreviation=value
        ).exists():
            raise serializers.ValidationError(PriceMsg.ABBREVIATION_EXIST)
        return value

    def validate_title(self, value):
        if value != self.instance.title and TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
        return value

    @classmethod
    def validate_rate(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)
        return None

    def update(self, instance, validated_data):
        if 'is_primary' in validated_data.keys():
            is_primary = validated_data['is_primary']
            if is_primary:
                old_primary = Currency.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    is_primary=True
                )
                old_primary.is_primary = False
                old_primary.rate = None
                old_primary.save()

                Currency.objects.filter_current(fill__tenant=True, fill__company=True).update(rate=None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class CurrencySyncWithVCBSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Currency
        fields = ('rate',)

    @classmethod
    def validate_rate(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)
        return None


class PriceListSerializer(serializers.ModelSerializer):  # noqa
    price_list_type = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = (
            'id',
            'title',
            'auto_update',
            'can_delete',
            'factor',
            'currency',
            'price_list_type',
            'price_list_mapped',
            'is_default',
        )

    @classmethod
    def get_price_list_type(cls, obj):
        if obj.price_list_type == 0:
            return {'value': obj.price_list_type, 'name': 'For Sale'}
        if obj.price_list_type == 1:
            return {'value': obj.price_list_type, 'name': 'For Purchase'}
        if obj.price_list_type == 2:
            return {'value': obj.price_list_type, 'name': 'For Expense'}
        return {}


class PriceCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Price
        fields = (
            'title',
            'auto_update',
            'can_delete',
            'factor',
            'currency',
            'price_list_type',
            'price_list_mapped'
        )

    @classmethod
    def validate_title(cls, value):
        if Price.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
        return value

    @classmethod
    def validate_factor(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return None

    @classmethod
    def validate_price(cls, attrs):
        attrs = float(attrs)
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.PRICE_MUST_BE_GREATER_THAN_ZERO)
        return None

    def create(self, validated_data):
        price_list = Price.objects.create(**validated_data)
        if 'auto_update' in validated_data.keys() and 'price_list_mapped' in validated_data.keys():
            products_source = ProductPriceList.objects.filter(price_list_id=validated_data['price_list_mapped'])
            objs = [
                ProductPriceList(
                    price_list=price_list,
                    product=p.product,
                    price=float(p.price) * float(price_list.factor),
                    currency_using=p.currency_using,
                    uom_using=p.uom_using,
                    uom_group_using=p.uom_group_using,
                    get_price_from_source=True
                ) for p in products_source
            ]
            ProductPriceList.objects.bulk_create(objs)
        return price_list


class PriceDetailSerializer(serializers.ModelSerializer):  # noqa
    products_mapped = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = (
            'id',
            'title',
            'auto_update',
            'can_delete',
            'factor',
            'currency',
            'price_list_type',
            'price_list_mapped',
            'is_default',
            'products_mapped'
        )

    @classmethod
    def get_products_mapped(cls, obj):
        products = ProductPriceList.objects.filter(
            price_list_id=obj.id,
            is_delete=False
        ).select_related('product', 'currency_using', 'uom_using', 'uom_group_using')
        all_products = []
        for product in products:
            product_information = {
                'id': product.product_id,
                'code': product.product.code,
                'title': product.product.title,
                'uom_group': {'id': product.uom_group_using_id, 'title': product.uom_group_using.title},
                'uom': {'id': product.uom_using_id, 'title': product.uom_using.title},
                'price': product.price,
                'is_auto_update': product.get_price_from_source,
                'currency_using': {'id': product.currency_using.id, 'abbreviation': product.currency_using.abbreviation}
            }
            all_products.append(product_information)
        return all_products

    @classmethod
    def get_price_list_mapped(cls, obj):
        price_list_mapped = Price.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=obj.price_list_mapped,
        ).first()
        if price_list_mapped:
            return {
                'id': obj.price_list_mapped,
                'title': price_list_mapped.title
            }
        return {}


class PriceUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = (
            'auto_update',
            'can_delete',
            'price_list_type',
            'factor',
            'currency'
        )

    @classmethod
    def validate_factor(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return None

    def update(self, instance, validated_data):
        if 'auto_update' not in validated_data.keys():  # update auto_update
            instance.auto_update = False
        else:
            instance.auto_update = True
        if 'can_delete' not in validated_data.keys():  # update can_delete
            instance.can_delete = False
        else:
            instance.can_delete = True

        instance.price_list_type = validated_data['price_list_type']  # update price_list_type

        old_factor = instance.factor
        instance.factor = validated_data['factor']  # update factor

        all_items = ProductPriceList.objects.filter(
            price_list=instance,
            get_price_from_source=1
        )
        for item in all_items:  # update lại giá đã map theo factor mới
            item.price = float(item.price) * float(instance.factor) / float(old_factor)
            item.save()
        instance.currency = validated_data['currency']  # update currency
        instance.save()
        if not instance.auto_update and 'apply_for' in self.initial_data.keys():
            products_of_category = Product.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                general_information__product_category=self.initial_data['apply_for']
            )
            current_general_price_list = Price.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_default=True
            ).first()
            products_of_this_price_list = ProductPriceList.objects.filter(price_list=instance)
            objs = []
            for product in products_of_category:
                if product not in products_of_this_price_list:
                    product_price_list = ProductPriceList.objects.filter(
                        product=product,
                        price_list=current_general_price_list
                    ).select_related('currency_using', 'uom_using', 'uom_group_using').first()
                    if product_price_list:
                        objs.append(
                            ProductPriceList(
                                price_list=instance,
                                product=product,
                                price=0.0,
                                currency_using=product_price_list.currency_using,
                                uom_using=product_price_list.uom_using,
                                uom_group_using=product_price_list.uom_group_using,
                            )
                        )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
        return instance


class PriceListUpdateProductsSerializer(serializers.ModelSerializer):  # noqa
    list_price = serializers.ListField(required=True)
    list_item = serializers.ListField(required=True)

    class Meta:
        model = Price
        fields = (
            'list_price',
            'list_item',
        )

    @classmethod
    def validate_list_price(cls, value):
        for item in value:
            if item['factor'] < 0:
                raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return value

    def update(self, instance, validated_data):
        objs = []
        list_price_list_delete = []
        for price in validated_data['list_price']:
            for item in validated_data['list_item']:
                found = True
                value_price = 0
                is_auto_update = True

                product_price_list_obj = ProductPriceList.objects.filter(
                    product_id=item['product_id'],
                    price_list_id=price['id'],
                    currency_using_id=item['currency'],
                ).first()
                if product_price_list_obj:
                    is_auto_update = product_price_list_obj.get_price_from_source
                    value_price = product_price_list_obj.price
                    list_price_list_delete.append(product_price_list_obj)
                else:
                    product_price_list_old = ProductPriceList.objects.filter(
                        product_id=item['product_id'],
                        price_list_id=price['id'],
                    ).first()
                    if product_price_list_old:
                        is_auto_update = product_price_list_old.get_price_from_source
                        value_price = 0
                    else:
                        found = False

                result_price = float(item['price']) * float(price['factor'])
                if price['id'] != str(instance.id):
                    if is_auto_update is False:
                        result_price = value_price
                if found:
                    objs.append(
                        ProductPriceList(
                            price_list_id=price['id'],
                            product_id=item['product_id'],
                            price=result_price,
                            currency_using_id=item['currency'],
                            uom_using_id=item['uom_id'],
                            uom_group_using_id=item['uom_group_id'],
                            get_price_from_source=is_auto_update
                        )
                    )
        for item in list_price_list_delete:
            item.delete()
        if len(objs) > 0:
            ProductPriceList.objects.bulk_create(objs)
        return instance


class PriceListDeleteProductsSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Price
        fields = ()

    def update(self, instance, validated_data):
        obj = ProductPriceList.objects.filter(
            product_id=self.initial_data.get('product_id', None),
            price_list=instance
        )
        if obj:
            obj.delete()
        else:
            raise serializers.ValidationError(PriceMsg.PRODUCT_NOT_EXIST_IN_THIS_PRICE_LIST)
        return instance


class ProductCreateInPriceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ()

    def update(self, instance, validated_data):
        price_list_information = self.initial_data['list_price_list']
        product = self.initial_data['product']
        objs = []
        if price_list_information and product:
            for item in price_list_information:
                get_price_from_source = False
                if item.get('is_auto_update', None) == '1':
                    get_price_from_source = True
                if not ProductPriceList.objects.filter(
                        price_list_id=item['price_list_id'],
                        product_id=product['id']
                ).exists():
                    objs.append(
                        ProductPriceList(
                            price_list_id=item.get('price_list_id', None),
                            product_id=product['id'],
                            price=float(item.get('price_value', None)),
                            currency_using_id=item.get('currency_using', None),
                            uom_using_id=product['uom'],
                            uom_group_using_id=product['uom_group'],
                            get_price_from_source=get_price_from_source
                        )
                    )
        if len(objs) > 0:
            ProductPriceList.objects.bulk_create(objs)
        return instance
