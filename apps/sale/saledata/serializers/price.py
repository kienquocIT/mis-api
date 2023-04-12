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
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
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
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
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
            raise serializers.ValidationError(PriceMsg.CODE_EXIST)
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
            raise serializers.ValidationError(PriceMsg.ABBREVIATION_EXIST)
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
        elif obj.price_list_type == 1:
            return {'value': obj.price_list_type, 'name': 'For Purchase'}
        elif obj.price_list_type == 2:
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
                    price=float(p.price)*float(price_list.factor),
                    currency_using=p.currency_using,
                    uom_using=p.uom_using,
                    uom_group_using=p.uom_group_using,
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
        for p in products:
            product_information = {
                'id': p.product_id,
                'code': p.product.code,
                'title': p.product.title,
                'uom_group': {'id': p.uom_group_using_id, 'title': p.uom_group_using.title},
                'uom': {'id': p.uom_using_id, 'title': p.uom_using.title},
                'price': p.price,
                'is_auto_update': p.get_price_from_source,
                'currency_using': {'id': p.currency_using.id, 'abbreviation': p.currency_using.abbreviation}
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
        if 'delete_product_id' in validated_data.keys():  # update price_list
            product_deleted = ProductPriceList.objects.filter(
                price_list=instance,
                product_id=validated_data['delete_product_id']
            ).first()
            product_deleted.is_delete = True
            product_deleted.is_active = False
            product_deleted.save()
        else:  # update setting
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
                            objs.append(ProductPriceList(
                                price_list=instance,
                                product=product,
                                price=0.0,
                                currency_using=product_price_list.currency_using,
                                uom_using=product_price_list.uom_using,
                                uom_group_using=product_price_list.uom_group_using,
                            ))
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
        for price in self.initial_data['list_price']:
            for item in self.initial_data['list_item']:
                product_price_list_obj = ProductPriceList.objects.filter(
                    product_id=item['product_id'],
                    price_list_id=price['id']
                ).first()
                if product_price_list_obj:
                    product_price_list_obj.delete()
                objs.append(
                    ProductPriceList(
                        price_list_id=price['id'],
                        product_id=item['product_id'],
                        price=float(item['price']) * float(price['factor']),
                        currency_using_id=item['currency'],
                        uom_using_id=item['uom_id'],
                        uom_group_using_id=item['uom_group_id'],
                        get_price_from_source=item['is_auto_update']
                    )
                )
        if len(objs) > 0:
            ProductPriceList.objects.bulk_create(objs)
        return instance
