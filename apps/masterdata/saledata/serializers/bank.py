from rest_framework import serializers

from apps.core.base.models import Country, District, City, Ward
from apps.masterdata.saledata.models import Bank, BankAccount
from apps.shared import BaseMsg

__all__ = [
    'BankListSerializer',
    'BankCreateSerializer',
    'BankDetailSerializer',
    'BankUpdateSerializer',
    'BankAccountListSerializer',
    'BankAccountCreateSerializer',
    'BankAccountUpdateSerializer',
    'BankAccountDetailSerializer'
]


class BankListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = (
            'id',
            'abbreviation',
            'vietnamese_name',
            'english_name',
            'is_default'
        )


class BankCreateSerializer(serializers.ModelSerializer):
    abbreviation = serializers.CharField(max_length=150, allow_blank=True)
    vietnamese_name = serializers.CharField(max_length=150, allow_blank=True)
    english_name = serializers.CharField(max_length=150, allow_blank=True)
    country = serializers.UUIDField()
    district = serializers.UUIDField()
    city = serializers.UUIDField()
    ward = serializers.UUIDField()

    class Meta:
        model = Bank
        fields = (
            'abbreviation',
            'vietnamese_name',
            'english_name',
            'country',
            'city',
            'district',
            'ward',
            'address',
            'full_address'
        )

    @classmethod
    def validate_abbreviation(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"abbreviation": BaseMsg.REQUIRED})

    @classmethod
    def validate_vietnamese_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"vietnamese_name": BaseMsg.REQUIRED})

    @classmethod
    def validate_english_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"english_name": BaseMsg.REQUIRED})

    @classmethod
    def validate_country(cls, value):
        if value:
            try:
                return Country.objects.get(id = value)
            except Country.DoesNotExist:
                raise serializers.ValidationError({"country": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_district(cls, value):
        if value:
            try:
                return District.objects.get(id=value)
            except District.DoesNotExist:
                raise serializers.ValidationError({"district": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_city(cls, value):
        if value:
            try:
                return City.objects.get(id=value)
            except City.DoesNotExist:
                raise serializers.ValidationError({"city": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_ward(cls, value):
        if value:
            try:
                return Ward.objects.get(id=value)
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"ward": BaseMsg.NOT_EXIST})
        return value


class BankDetailSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()

    class Meta:
        model = Bank
        fields = (
            'id',
            'abbreviation',
            'vietnamese_name',
            'english_name',
            'country',
            'city',
            'district',
            'ward',
            'address',
            'full_address'
        )

    @classmethod
    def get_country(cls, obj):
        return {
            'id': obj.country.id,
            'title': obj.country.title,
        }
    @classmethod
    def get_district(cls, obj):
        return {
            'id': obj.district.id,
            'title': obj.district.title,
        }

    @classmethod
    def get_city(cls, obj):
        return {
            'id': obj.city.id,
            'title': obj.city.title,
        }

    @classmethod
    def get_ward(cls, obj):
        return {
            'id': obj.ward.id,
            'title': obj.ward.title,
        }


class BankUpdateSerializer(serializers.ModelSerializer):
    abbreviation = serializers.CharField(max_length=150, allow_blank=True)
    vietnamese_name = serializers.CharField(max_length=150, allow_blank=True)
    english_name = serializers.CharField(max_length=150, allow_blank=True)
    country = serializers.UUIDField()
    district = serializers.UUIDField()
    city = serializers.UUIDField()
    ward = serializers.UUIDField()

    class Meta:
        model = Bank
        fields = (
            'abbreviation',
            'vietnamese_name',
            'english_name',
            'country',
            'city',
            'district',
            'ward',
            'address',
            'full_address'
        )

    @classmethod
    def validate_abbreviation(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"abbreviation": BaseMsg.REQUIRED})

    @classmethod
    def validate_vietnamese_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"vietnamese_name": BaseMsg.REQUIRED})

    @classmethod
    def validate_english_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"english_name": BaseMsg.REQUIRED})

    @classmethod
    def validate_country(cls, value):
        if value:
            try:
                return Country.objects.get(id=value)
            except Country.DoesNotExist:
                raise serializers.ValidationError({"country": BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_district(cls, value):
        if value:
            try:
                return District.objects.get(id=value)
            except District.DoesNotExist:
                raise serializers.ValidationError({"district": BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_city(cls, value):
        if value:
            try:
                return City.objects.get(id=value)
            except City.DoesNotExist:
                raise serializers.ValidationError({"city": BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_ward(cls, value):
        if value:
            try:
                return Ward.objects.get(id=value)
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"ward": BaseMsg.REQUIRED})
        return value


class BankAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = (
            'id',
            'bank_name',
            'bank_account_number',
            'brand_name',
            'bank_owner'
        )


class BankAccountCreateSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.UUIDField(required=False)

    class Meta:
        model = BankAccount
        fields = (
            'bank_abbreviation',
            'bank_name',
            'bank_account_number',
            'bank_owner',
            'is_brand',
            'brand_name',
            'brand_country',
            'brand_city',
            'brand_district',
            'brand_ward',
            'brand_address',
            'brand_full_address',
            'head_address'
        )

    @classmethod
    def validate_bank_abbreviation(cls, value):
        if value:
            try:
                return Bank.objects.get(id = value)
            except Bank.DoesNotExist:
                raise serializers.ValidationError({"bank_abbreviation": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"bank_abbreviation": BaseMsg.REQUIRED})

    def validate(self, validate_data):
        if validate_data['is_brand']:
            try:
                country = Country.objects.get(id = validate_data['brand_country'])
                validate_data['brand_country'] = country
            except Country.DoesNotExist:
                raise serializers.ValidationError({"brand_country": BaseMsg.NOT_EXIST})

            try:
                city = City.objects.get(id = validate_data['brand_city'])
                validate_data['brand_city'] = city
            except City.DoesNotExist:
                raise serializers.ValidationError({"brand_city": BaseMsg.NOT_EXIST})

            try:
                district = District.objects.get(id = validate_data['brand_district'])
                validate_data['brand_district'] = district
            except District.DoesNotExist:
                raise serializers.ValidationError({"brand_district": BaseMsg.NOT_EXIST})

            try:
                ward = Ward.objects.get(id = validate_data['brand_ward'])
                validate_data['brand_ward'] = ward
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"brand_ward": BaseMsg.NOT_EXIST})


class BankAccountUpdateSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.UUIDField(required=False)

    class Meta:
        model = BankAccount
        fields = (
            'bank_abbreviation',
            'bank_name',
            'bank_account_number',
            'bank_owner',
            'is_brand',
            'brand_name',
            'brand_country',
            'brand_city',
            'brand_district',
            'brand_ward',
            'brand_address',
            'brand_full_address',
            'head_address'
        )

    @classmethod
    def validate_bank_abbreviation(cls, value):
        if value:
            try:
                return Bank.objects.get(id=value)
            except Bank.DoesNotExist:
                raise serializers.ValidationError({"bank_abbreviation": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"bank_abbreviation": BaseMsg.REQUIRED})

    def validate(self, validate_data):
        if validate_data['is_brand']:
            try:
                country = Country.objects.get(id=validate_data['brand_country'])
                validate_data['brand_country'] = country
            except Country.DoesNotExist:
                raise serializers.ValidationError({"brand_country": BaseMsg.NOT_EXIST})

            try:
                city = City.objects.get(id=validate_data['brand_city'])
                validate_data['brand_city'] = city
            except City.DoesNotExist:
                raise serializers.ValidationError({"brand_city": BaseMsg.NOT_EXIST})

            try:
                district = District.objects.get(id=validate_data['brand_district'])
                validate_data['brand_district'] = district
            except District.DoesNotExist:
                raise serializers.ValidationError({"brand_district": BaseMsg.NOT_EXIST})

            try:
                ward = Ward.objects.get(id=validate_data['brand_ward'])
                validate_data['brand_ward'] = ward
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"brand_ward": BaseMsg.NOT_EXIST})


class BankAccountDetailSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.SerializerMethodField()
    brand_country = serializers.SerializerMethodField()
    brand_city = serializers.SerializerMethodField()
    brand_district = serializers.SerializerMethodField()
    brand_ward = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = (
            'id',
            'bank_abbreviation',
            'bank_name',
            'bank_account_number',
            'bank_owner',
            'is_brand',
            'brand_name',
            'brand_country',
            'brand_city',
            'brand_district',
            'brand_ward',
            'brand_address',
            'brand_full_address',
            'head_address'
        )

    @classmethod
    def get_bank_abbreviation(cls, obj):
        return {
            'id': obj.bank_abbreviation.id,
            'vietnamese_name': obj.bank_abbreviation.vietnamese_name,
            'english_name': obj.bank_abbreviation.english_name,
        }

    @classmethod
    def get_brand_country(cls, obj):
        return {
            'id': obj.brand_country.id,
            'title': obj.brand_country.title,
        } if obj.brand_country else {}

    @classmethod
    def get_brand_district(cls, obj):
        return {
            'id': obj.brand_district.id,
            'title': obj.brand_district.title,
        } if obj.brand_district else {}

    @classmethod
    def get_brand_city(cls, obj):
        return {
            'id': obj.brand_city.id,
            'title': obj.brand_city.title,
        } if obj.brand_city else {}

    @classmethod
    def get_brand_ward(cls, obj):
        return {
            'id': obj.brand_ward.id,
            'title': obj.brand_ward.title,
        } if obj.brand_ward else {}