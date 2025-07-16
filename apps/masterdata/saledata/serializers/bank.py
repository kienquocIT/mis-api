from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.base.models import Country, District, City, Ward, NProvince, NWard
from apps.masterdata.saledata.models import Bank, BankAccount, Currency

__all__ = [
    'BankListSerializer',
    'BankCreateSerializer',
    'BankDetailSerializer',
    'BankAccountListSerializer',
    'BankAccountCreateSerializer',
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
        province_obj = NProvince.objects.filter(id=head_office_address_data.get('province_id')).first()
        ward_obj = NWard.objects.filter(id=head_office_address_data.get('ward_id')).first()
        return {
            'country_data': {'id': str(country_obj.id), 'title': country_obj.title} if country_obj else {},
            'province_data': {'id': str(province_obj.id), 'fullname': province_obj.fullname} if province_obj else {},
            'ward_data': {'id': str(ward_obj.id), 'fullname': ward_obj.fullname} if ward_obj else {},
            'address': head_office_address_data.get('address', '')
        }

    def validate(self, validate_data):
        head_office_address_data = validate_data.get('head_office_address_data', {})
        validate_data['head_office_address'] = ', '.join(
            filter(None, [
                head_office_address_data.get('address', ''),
                head_office_address_data.get('ward_data', {}).get('fullname'),
                head_office_address_data.get('province_data', {}).get('fullname'),
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
    title = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = (
            'id',
            'title',
            'bank_mapped_data',
            'bank_account_number',
            'bank_account_owner',
            'brand_name',
            'brand_address'
        )

    @classmethod
    def get_title(cls, obj):
        return (f"{obj.bank_account_number} ({obj.bank_account_owner}) - "
                f"{obj.bank_mapped.bank_name} ({obj.bank_mapped.bank_abbreviation})")


class BankAccountCreateSerializer(serializers.ModelSerializer):
    bank_mapped = serializers.UUIDField()
    currency = serializers.UUIDField()
    brand_address_data = serializers.JSONField(default=dict)

    class Meta:
        model = BankAccount
        fields = (
            'bank_mapped',
            'bank_account_number',
            'bank_account_owner',
            'currency',
            'is_brand',
            'brand_name',
            'brand_address_data',
        )

    @classmethod
    def validate_bank_mapped(cls, value):
        if value:
            try:
                return Bank.objects.get(id=value)
            except Bank.DoesNotExist:
                raise serializers.ValidationError({"bank_mapped": _('Bank must not null')})
        raise serializers.ValidationError({"bank_mapped": _('Bank must not null')})

    @classmethod
    def validate_currency(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({"currency": _('Currency must not null')})
        raise serializers.ValidationError({"currency": _('Currency must not null')})

    @classmethod
    def validate_brand_address_data(cls, brand_address_data):
        country_obj = Country.objects.filter(id=brand_address_data.get('country_id')).first()
        province_obj = NProvince.objects.filter(id=brand_address_data.get('province_id')).first()
        ward_obj = NWard.objects.filter(id=brand_address_data.get('ward_id')).first()
        return {
            'country_data': {'id': str(country_obj.id), 'title': country_obj.title} if country_obj else {},
            'province_data': {'id': str(province_obj.id), 'fullname': province_obj.fullname} if province_obj else {},
            'ward_data': {'id': str(ward_obj.id), 'fullname': ward_obj.fullname} if ward_obj else {},
            'address': brand_address_data.get('address', '')
        }

    def validate(self, validate_data):
        if validate_data.get('is_brand', False):
            if not validate_data.get('brand_name', ''):
                raise serializers.ValidationError({"brand_name": _('Brand name must not null')})
            brand_address_data = validate_data.get('brand_address_data', {})
            brand_address_data_concat = ', '.join(
                filter(None, [
                    brand_address_data.get('address', ''),
                    brand_address_data.get('ward_data', {}).get('fullname'),
                    brand_address_data.get('province_data', {}).get('fullname'),
                    brand_address_data.get('country_data', {}).get('title'),
                ])
            )
            if not brand_address_data_concat:
                raise serializers.ValidationError({"brand_address_data": _('Brand address must not null')})
            validate_data['brand_address'] = brand_address_data_concat

        bank_mapped = validate_data.get('bank_mapped')
        validate_data['bank_mapped_data'] = {
            'id': str(bank_mapped.id),
            'bank_abbreviation': bank_mapped.bank_abbreviation,
            'bank_name': bank_mapped.bank_name,
            'bank_foreign_name': bank_mapped.bank_foreign_name,
            'head_office_address': bank_mapped.head_office_address
        } if bank_mapped else {}

        currency = validate_data.get('currency')
        validate_data['currency_data'] = {'id': str(currency.id), 'title': currency.title} if currency else {}
        return validate_data


class BankAccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = (
            'id',
            'bank_mapped_data',
            'bank_account_number',
            'bank_account_owner',
            'currency_data',
            'is_brand',
            'brand_name',
            'brand_address',
            'brand_address_data'
        )
