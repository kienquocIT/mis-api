from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.base.models import Country, District, City, Ward
from apps.masterdata.saledata.models import Bank, BankAccount, Currency
from apps.shared import BaseMsg

__all__ = [
    'BankListSerializer',
    'BankCreateSerializer',
    'BankDetailSerializer',
    'BankAccountListSerializer',
    'BankAccountCreateSerializer',
    'BankAccountUpdateSerializer',
    'BankAccountDetailSerializer'
]


# Bank
class BankListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = (
            'id',
            'bank_abbreviation',
            'bank_name',
            'bank_foreign_name',
            'is_default',
            'head_office_address',
            'vietqr_json_data'
        )


class BankCreateSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.CharField(max_length=150, allow_blank=True)
    bank_name = serializers.CharField(max_length=150, allow_blank=True)
    bank_foreign_name = serializers.CharField(max_length=150, allow_blank=True, allow_null=True)
    head_office_address_data = serializers.JSONField(default=dict)

    class Meta:
        model = Bank
        fields = (
            'bank_abbreviation',
            'bank_name',
            'bank_foreign_name',
            'head_office_address_data',
            'vietqr_json_data'
        )

    @classmethod
    def validate_bank_abbreviation(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"bank_abbreviation": _('Bank abbreviation must not null')})

    @classmethod
    def validate_bank_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"bank_name": _('Bank name must not null')})

    @classmethod
    def validate_bank_foreign_name(cls, value):
        if value:
            return value
        return ''

    @classmethod
    def validate_head_office_address_data(cls, head_office_address_data):
        country_obj = Country.objects.filter(id=head_office_address_data.get('country_id')).first()
        city_obj = City.objects.filter(id=head_office_address_data.get('city_id')).first()
        district_obj = District.objects.filter(id=head_office_address_data.get('district_id')).first()
        ward_obj = Ward.objects.filter(id=head_office_address_data.get('ward_id')).first()
        return {
            'country_data': {'id': str(country_obj.id), 'title': country_obj.title} if country_obj else {},
            'city_data': {'id': str(city_obj.id), 'title': city_obj.title} if city_obj else {},
            'district_data': {'id': str(district_obj.id), 'title': district_obj.title} if district_obj else {},
            'ward_data': {'id': str(ward_obj.id), 'title': ward_obj.title} if ward_obj else {},
            'address': head_office_address_data.get('address', '')
        }

    def validate(self, validate_data):
        head_office_address_data = validate_data.get('head_office_address_data', {})
        validate_data['head_office_address'] = ', '.join(
            filter(None, [
                head_office_address_data.get('address', ''),
                head_office_address_data.get('ward_data', {}).get('title'),
                head_office_address_data.get('district_data', {}).get('title'),
                head_office_address_data.get('city_data', {}).get('title'),
                head_office_address_data.get('country_data', {}).get('title'),
            ])
        )
        return validate_data


class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = (
            'id',
            'bank_abbreviation',
            'bank_name',
            'bank_foreign_name',
            'head_office_address',
            'head_office_address_data'
        )


# Bank Account
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
    currency = serializers.UUIDField(required=False)
    brand_name = serializers.CharField(required=False, allow_blank=True)
    brand_country = serializers.UUIDField(required=False)
    brand_district = serializers.UUIDField(required=False)
    brand_city = serializers.UUIDField(required=False)
    brand_ward = serializers.UUIDField(required=False)

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
            'currency'
        )

    @classmethod
    def validate_currency(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({"currency": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"currency": BaseMsg.REQUIRED})

    @classmethod
    def validate_bank_abbreviation(cls, value):
        if value:
            try:
                return Bank.objects.get(id = value)
            except Bank.DoesNotExist:
                raise serializers.ValidationError({"bank_abbreviation": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"bank_abbreviation": BaseMsg.REQUIRED})

    @classmethod
    def validate_brand_country(cls, value):
        if value:
            try:
                return Country.objects.get(id=value)
            except Country.DoesNotExist:
                raise serializers.ValidationError({"brand_country": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_district(cls, value):
        if value:
            try:
                return District.objects.get(id=value)
            except District.DoesNotExist:
                raise serializers.ValidationError({"brand_district": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_city(cls, value):
        if value:
            try:
                return City.objects.get(id=value)
            except City.DoesNotExist:
                raise serializers.ValidationError({"brand_city": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_ward(cls, value):
        if value:
            try:
                return Ward.objects.get(id=value)
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"brand_ward": BaseMsg.NOT_EXIST})
        return value

    def validate(self, validate_data):
        if validate_data.get('is_brand', False):
            if not validate_data.get('brand_name', None):
                raise serializers.ValidationError({"brand_name": BaseMsg.REQUIRED})
            if not validate_data.get('brand_full_address', None):
                raise serializers.ValidationError({"brand_full_address": BaseMsg.REQUIRED})
        return validate_data


class BankAccountUpdateSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.UUIDField(required=False)
    currency = serializers.UUIDField(required=False)
    brand_name = serializers.CharField(required=False, allow_blank=True)
    brand_country = serializers.UUIDField(required=False)
    brand_district = serializers.UUIDField(required=False)
    brand_city = serializers.UUIDField(required=False)
    brand_ward = serializers.UUIDField(required=False)
    brand_full_address = serializers.CharField(required=False, allow_blank=True)
    brand_address = serializers.CharField(required=False, allow_blank=True)

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
            'currency'
        )

    @classmethod
    def validate_currency(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({"currency": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"currency": BaseMsg.REQUIRED})

    @classmethod
    def validate_bank_abbreviation(cls, value):
        if value:
            try:
                return Bank.objects.get(id=value)
            except Bank.DoesNotExist:
                raise serializers.ValidationError({"bank_abbreviation": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"bank_abbreviation": BaseMsg.REQUIRED})

    @classmethod
    def validate_brand_country(cls, value):
        if value:
            try:
                return Country.objects.get(id=value)
            except Country.DoesNotExist:
                raise serializers.ValidationError({"brand_country": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_district(cls, value):
        if value:
            try:
                return District.objects.get(id=value)
            except District.DoesNotExist:
                raise serializers.ValidationError({"brand_district": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_city(cls, value):
        if value:
            try:
                return City.objects.get(id=value)
            except City.DoesNotExist:
                raise serializers.ValidationError({"brand_city": BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_brand_ward(cls, value):
        if value:
            try:
                return Ward.objects.get(id=value)
            except Ward.DoesNotExist:
                raise serializers.ValidationError({"brand_ward": BaseMsg.NOT_EXIST})
        return value

    def validate(self, validate_data):
        if validate_data.get('is_brand', False):
            if not validate_data.get('brand_name', None):
                raise serializers.ValidationError({"brand_name": BaseMsg.REQUIRED})
            if not validate_data.get('brand_full_address', None):
                raise serializers.ValidationError({"brand_full_address": BaseMsg.REQUIRED})
        return validate_data


class BankAccountDetailSerializer(serializers.ModelSerializer):
    bank_abbreviation = serializers.SerializerMethodField()
    brand_country = serializers.SerializerMethodField()
    brand_city = serializers.SerializerMethodField()
    brand_district = serializers.SerializerMethodField()
    brand_ward = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

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
            'currency'
        )

    @classmethod
    def get_bank_abbreviation(cls, obj):
        return {
            'id': obj.bank_abbreviation.id,
            'abbreviation': obj.bank_abbreviation.abbreviation
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

    @classmethod
    def get_currency(cls, obj):
        return {
            'id': obj.currency.id,
            'title': obj.currency.title,
        } if obj.currency else {}
