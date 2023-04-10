from rest_framework import serializers
from apps.sale.saledata.models.price import (
    TaxCategory, Tax, Currency, Price, ProductPriceList
)
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
                    price=p.price,
                    currency_using=p.currency_using,
                    uom_using=p.uom_using,
                    uom_group_using=p.uom_group_using,
                ) for p in products_source
            ]
            ProductPriceList.objects.bulk_create(objs)
        return price_list


class PriceDetailSerializer(serializers.ModelSerializer):  # noqa
    products_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = (
            'id',
            'title',
            'auto_update',
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
            price_list_id=obj.id
        ).select_related('product', 'currency_using', 'uom_using', 'uom_group_using')
        all_products = []
        for p in products:
            product_information = {
                'id': p.product_id,
                'code': p.product.code,
                'title': p.product.title,
                'uom_group': p.uom_group_using.title,
                'uom': p.uom_using.title,
                'price': p.price,
                'currency_using': p.currency_using.abbreviation
            }
            all_products.append(product_information)
        return all_products


class PriceUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = (
            'auto_update',
        )

    @classmethod
    def validate_rate(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return None

    def update(self, instance, validated_data):
        if 'auto_update' not in validated_data.keys():
            instance.auto_update = False
            instance.price_list_mapped = None
        instance.save()
        return instance
