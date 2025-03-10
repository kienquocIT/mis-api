from rest_framework import serializers
from apps.masterdata.saledata.models.price import (
    TaxCategory, Tax, Currency
)
from apps.shared import PriceMsg


# Tax Category
class TaxCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = TaxCategory
        fields = ('id', 'code', 'title', 'description', 'is_default')


class TaxCategoryCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=100)

    class Meta:
        model = TaxCategory
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_title(cls, value):
        if TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": PriceMsg.TITLE_EXIST})
        return value

    @classmethod
    def validate_code(cls, value):
        if TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError({"code": PriceMsg.CODE_EXIST})
        return value


class TaxCategoryDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = TaxCategory
        fields = ('id', 'code', 'title', 'description', 'is_default')


class TaxCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=100)

    class Meta:
        model = TaxCategory
        fields = ('code', 'title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": PriceMsg.TITLE_EXIST})
        return value

    def validate_code(self, value):
        if TaxCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(PriceMsg.CODE_EXIST)
        return value


# Tax
class TaxListSerializer(serializers.ModelSerializer):  # noqa
    category = serializers.SerializerMethodField()

    class Meta:
        model = Tax
        fields = ('id', 'code', 'title', 'rate', 'category', 'tax_type', 'is_default')

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
        fields = ('title', 'code', 'rate', 'category', 'tax_type')

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
    category = serializers.SerializerMethodField()

    class Meta:
        model = Tax
        fields = ('id', 'code', 'title', 'rate', 'category', 'tax_type', 'is_default')

    @classmethod
    def get_category(cls, obj):
        if obj.category:
            return {
                'id': obj.category_id,
                'title': obj.category.title,
            }
        return {}


class TaxUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Tax
        fields = ('title', 'rate', 'category', 'tax_type')


# Currency
class CurrencyListSerializer(serializers.ModelSerializer):  # noqa
    currency = serializers.SerializerMethodField()

    @classmethod
    def get_currency(cls, obj):
        return {
            "id": "",
            "title": obj.title,
            "code": obj.abbreviation
        }

    class Meta:
        model = Currency
        fields = ('id', 'abbreviation', 'title', 'rate', 'is_default', 'is_primary', 'currency')


class CurrencyCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Currency
        fields = ('abbreviation', 'title', 'rate', 'currency')

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
        fields = ('id', 'abbreviation', 'title', 'rate', 'is_default', 'is_primary', 'currency')


class CurrencyUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Currency
        fields = ()

    def update(self, instance, validated_data):
        instance.delete()
        return True


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
