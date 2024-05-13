from rest_framework import serializers

from apps.core.hr.models import Role
from apps.sales.quotation.models import QuotationAppConfig, ConfigShortSale, ConfigLongSale, ConfigShortSaleRole, \
    ConfigLongSaleRole
from apps.shared import HRMsg, SaleMsg


class ShortConfigSerializer(serializers.ModelSerializer):
    is_choose_price_list = serializers.BooleanField(default=False)
    is_input_price = serializers.BooleanField(default=False)
    is_discount_on_product = serializers.BooleanField(default=False)
    is_discount_on_total = serializers.BooleanField(default=False)

    class Meta:
        model = ConfigShortSale
        fields = (
            'is_choose_price_list',
            'is_input_price',
            'is_discount_on_product',
            'is_discount_on_total'
        )


class LongConfigSerializer(serializers.ModelSerializer):
    is_not_input_price = serializers.BooleanField(default=False)
    is_not_discount_on_product = serializers.BooleanField(default=False)
    is_not_discount_on_total = serializers.BooleanField(default=False)

    class Meta:
        model = ConfigLongSale
        fields = (
            'is_not_input_price',
            'is_not_discount_on_product',
            'is_not_discount_on_total',
        )


class QuotationConfigUpdateSerializer(serializers.ModelSerializer):
    short_sale_config = ShortConfigSerializer()
    long_sale_config = LongConfigSerializer()
    ss_role = serializers.ListField(child=serializers.UUIDField(), required=False)
    ls_role = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = QuotationAppConfig
        fields = (
            'short_sale_config',
            'long_sale_config',
            'is_require_payment',
            'ss_role',
            'ls_role',
        )

    @classmethod
    def validate_role(cls, value):
        if isinstance(value, list):
            if value:
                role_list = Role.objects.filter(id__in=value).count()
                if role_list == len(value):
                    return value
                raise serializers.ValidationError({'detail': HRMsg.ROLES_NOT_EXIST})
            return value
        raise serializers.ValidationError({'detail': HRMsg.ROLE_IS_ARRAY})

    @classmethod
    def validate_ss_role(cls, value):
        return cls.validate_role(value=value)

    @classmethod
    def validate_ls_role(cls, value):
        return cls.validate_role(value=value)

    def validate(self, validate_data):
        ss_role = validate_data.get('ss_role', [])
        ls_role = validate_data.get('ls_role', [])
        if any(role_id in ls_role for role_id in ss_role):
            raise serializers.ValidationError({'detail': SaleMsg.SO_CONFIG_ROLE_CHECK})
        return validate_data

    def update(self, instance, validated_data):
        ss_role = []
        ls_role = []
        if 'ss_role' in validated_data:
            ss_role = validated_data['ss_role']
            del validated_data['ss_role']
        if 'ls_role' in validated_data:
            ls_role = validated_data['ls_role']
            del validated_data['ls_role']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # delete & create new short_sale_config
        instance.quotation_config_short_sale.delete()
        ConfigShortSale.objects.create(
            quotation_config=instance,
            **validated_data['short_sale_config']
        )
        # delete & create new long_sale_config
        instance.quotation_config_long_sale.delete()
        ConfigLongSale.objects.create(
            quotation_config=instance,
            **validated_data['long_sale_config']
        )
        # delete & create new short sale role
        instance.ss_role_config.all().delete()
        ConfigShortSaleRole.objects.bulk_create([
            ConfigShortSaleRole(quotation_config=instance, role_id=role_id) for role_id in ss_role
        ])
        # delete & create new long sale role
        instance.ls_role_config.all().delete()
        ConfigLongSaleRole.objects.bulk_create([
            ConfigLongSaleRole(quotation_config=instance, role_id=role_id) for role_id in ls_role
        ])
        return instance


class QuotationConfigDetailSerializer(serializers.ModelSerializer):
    short_sale_config = serializers.JSONField()
    long_sale_config = serializers.JSONField()
    ss_role = serializers.SerializerMethodField()
    ls_role = serializers.SerializerMethodField()

    class Meta:
        model = QuotationAppConfig
        fields = (
            'id',
            'short_sale_config',
            'long_sale_config',
            'is_require_payment',
            'ss_role',
            'ls_role',
        )

    @classmethod
    def get_ss_role(cls, obj):
        return [
            {
                'id': role.id,
                'title': role.title,
                'code': role.code,
            }
            for role in obj.ss_role.all()]

    @classmethod
    def get_ls_role(cls, obj):
        return [
            {
                'id': role.id,
                'title': role.title,
                'code': role.code,
            }
            for role in obj.ls_role.all()]
