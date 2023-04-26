from rest_framework import serializers
from apps.sale.saledata.models.product import (
    Expense, UnitOfMeasureGroup, UnitOfMeasure, ExpenseGeneral, ExpensePrice
)
from apps.sale.saledata.models.price import Tax, Currency
from apps.sale.saledata.models.product import ExpenseType
from apps.shared.translations.expense import ExpenseMsg


class ExpenseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = (
            'id',
            'code',
            'title',
            'general_information',
        )


class ExpenseGeneralCreateSerializer(serializers.ModelSerializer):
    expense_type = serializers.UUIDField(required=True, allow_null=False)
    uom_group = serializers.UUIDField(allow_null=False, required=True)
    uom = serializers.UUIDField(allow_null=False, required=True)
    tax_code = serializers.UUIDField(allow_null=True, required=False)
    price_list = serializers.ListField()
    currency_using = serializers.UUIDField()

    class Meta:
        model = ExpenseGeneral
        fields = (
            'expense_type',
            'uom_group',
            'uom',
            'tax_code',
            'price_list',
            'currency_using',
        )

    @classmethod
    def validate_expense_type(cls, value):
        try:
            if value is not None:
                expense_type = ExpenseType.objects.get(
                    id=value
                )
            return {'id': str(expense_type.id), 'title': expense_type.title}
        except ExpenseType.DoesNotExist:
            raise serializers.ValidationError({'expense_type': ExpenseMsg.EXPENSE_TYPE_NOT_EXIST})
        return None

    @classmethod
    def validate_uom_group(cls, value):
        try:
            if value is not None:
                uom_group = UnitOfMeasureGroup.objects.get(
                    id=value
                )
                return {'id': str(uom_group.id), 'title': uom_group.title}
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'uom_group': ExpenseMsg.UOM_GROUP_NOT_EXIST})
        return None

    @classmethod
    def validate_uom(cls, value):
        try:
            if value is not None:
                uom = UnitOfMeasure.objects.get(
                    id=value
                )
                return {'id': str(uom.id), 'title': uom.title, 'group': str(uom.group_id)}
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': ExpenseMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_tax_code(cls, value):
        try:
            if value is not None:
                tax = Tax.objects.get(
                    id=value
                )
                return {'id': str(tax.id), 'title': tax.title, 'code': tax.code}
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax_code': ExpenseMsg.TAX_CODE_NOT_EXIST})
        return None

    @classmethod
    def validate_currency_using(cls, value):
        try:
            if value is not None:
                currency = Currency.objects.get(
                    id=value
                )
            return {'id': str(currency.id), 'title': currency.title, 'code': currency.code}
        except ExpenseType.DoesNotExist:
            raise serializers.ValidationError({'expense_type': ExpenseMsg.EXPENSE_TYPE_NOT_EXIST})
        return None

    def validate(self, validate_data):
        uom = validate_data['uom']
        uom_group = validate_data['uom_group']
        if uom['group'] != uom_group['id']:
            raise serializers.ValidationError({'expense_type': ExpenseMsg.UOM_NOT_MAP_UOM_GROUP})
        return validate_data


class ExpenseCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    general_information = ExpenseGeneralCreateSerializer(required=False)

    class Meta:
        model = Expense
        fields = (
            'code',
            'title',
            'general_information',
        )

    @classmethod
    def validate_code(cls, value):
        if Expense.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ExpenseMsg.CODE_EXIST)
        return value

    def create(self, validated_data):
        currency_using = validated_data.pop['currency_using']
        expense = Expense.objects.create(**validated_data)
        validated_data['currency_using'] = currency_using
        self.common_create_expense_general(validated_data=validated_data, instance=expense)
        return expense

    @classmethod
    def common_create_expense_general(cls, validated_data, instance):
        if 'general_information' in validated_data:  # noqa
            tax_id = None
            if validated_data['general_information']['tax_code']:
                tax_id = validated_data['general_information']['tax_code']['id']
            expense_general = ExpenseGeneral.objects.create(
                expense=instance,
                expense_type_id=validated_data['general_information']['expense_type']['id'],
                uom_group_id=validated_data['general_information']['uom_group']['id'],
                uom_id=validated_data['general_information']['uom']['id'],
                tax_code_id=tax_id,
            )

            cls.common_create_expense_price(validated_data, expense_general)
        return True

    @staticmethod
    def common_create_expense_price(validated_data, instance):
        if 'general_information' in validated_data:  # noqa
            price_list = validated_data['general_information']['price_list']
            if price_list:
                bulk_data = [
                    ExpensePrice(
                        expense_general=instance,
                        price_id=item['id'],
                        currency_id=validated_data['general_information']['currency_using']['id'],
                        price_value=item['value'],
                        is_auto_update=item['is_auto_update']
                    ) for item in price_list
                ]
                if len(bulk_data) > 0:
                    ExpensePrice.objects.bulk_create(bulk_data)
        return True


class ExpenseDetailSerializer(serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    @classmethod
    def get_general_information(cls, obj):
        price_list = [
            {
                'id': item.price_id,
                'price_value': item.price_value,
                'is_auto_update': item.is_auto_update,
            } for item in ExpensePrice.objects.filter(expense_general=obj.expense)
        ]

        obj.general_information['price_list'] = price_list
        return obj.general_information


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    general_information = ExpenseGeneralCreateSerializer(required=True)

    class Meta:
        model = Expense
        fields = (
            'title',
            'general_information',
        )

    def update(self, instance, validated_data):
        self.common_update_expense_general(validated_data=validated_data, instance=instance)
        del validated_data['general_information']['currency_using']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @staticmethod
    def common_delete_expense_price(instance):
        ExpensePrice.objects.filter(expense_general=instance).delete()
        return True

    @classmethod
    def common_update_expense_general(cls, validated_data, instance):
        if 'general_information' in validated_data:  # noqa
            tax_id = None
            if validated_data['general_information']['tax_code']:
                tax_id = validated_data['general_information']['tax_code']['id']

            expense_general = instance.expense
            expense_general.delete()
            expense_general = ExpenseGeneral.objects.create(
                expense=instance,
                expense_type_id=validated_data['general_information']['expense_type']['id'],
                uom_group_id=validated_data['general_information']['uom_group']['id'],
                uom_id=validated_data['general_information']['uom']['id'],
                tax_code_id=tax_id,
            )
            cls.common_delete_expense_price(expense_general)
            ExpenseCreateSerializer.common_create_expense_price(validated_data, expense_general)
        return True
