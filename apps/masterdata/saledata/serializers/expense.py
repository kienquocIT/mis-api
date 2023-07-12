from rest_framework import serializers
from apps.masterdata.saledata.models.product import (
    Expense, UnitOfMeasureGroup, UnitOfMeasure, ExpensePrice, ExpenseRole
)
from apps.masterdata.saledata.models.price import Currency
from apps.masterdata.saledata.models.product import ExpenseType
from apps.shared.translations.expense import ExpenseMsg


class ExpenseListSerializer(serializers.ModelSerializer):
    expense_type = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = (
            'id',
            'code',
            'title',
            'expense_type',
            'uom_group',
            'uom',
        )

    @classmethod
    def get_expense_type(cls, obj):
        if obj.expense_type:
            return {
                'id': obj.expense_type_id,
                'title': obj.expense_type.title,
            }
        return {}


class ExpenseCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    code = serializers.CharField(max_length=150)

    expense_type = serializers.UUIDField(required=True, allow_null=False)
    uom_group = serializers.UUIDField(allow_null=False, required=True)
    uom = serializers.UUIDField(allow_null=False, required=True)
    data_price_list = serializers.ListField()
    currency_using = serializers.UUIDField()
    role = serializers.ListField(child=serializers.UUIDField())

    class Meta:
        model = Expense
        fields = (
            'code',
            'title',
            'expense_type',
            'uom_group',
            'uom',
            'data_price_list',
            'currency_using',
            'role'
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

    @classmethod
    def validate_expense_type(cls, value):
        try:
            if value is not None:
                expense_type = ExpenseType.objects.get(
                    id=value
                )
                return expense_type
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
                return uom_group
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
                return uom
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': ExpenseMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_currency_using(cls, value):
        try:
            if value is not None:
                currency = Currency.objects.get(
                    id=value
                )
                return currency.id
        except Currency.DoesNotExist:
            raise serializers.ValidationError({'expense_type': ExpenseMsg.CURRENCY_NOT_EXIST})
        return None

    def create(self, validated_data):
        data_price_list = validated_data.pop('data_price_list')
        currency_using = validated_data.pop('currency_using')
        data_role = validated_data.pop('role', [])
        expense = Expense.objects.create(**validated_data)
        self.common_create_expense_price(data_price_list, currency_using, validated_data['uom'], expense)
        self.common_create_expense_role(data_role, expense)
        return expense

    @staticmethod
    def common_create_expense_role(data, instance):
        data_bulk = []
        for role_id in data:
            expense_role = ExpenseRole(
                role_id=role_id,
                expense=instance
            )
            data_bulk.append(expense_role)
        ExpenseRole.objects.bulk_create(data_bulk)

    @staticmethod
    def common_create_expense_price(data_price_list, currency_using, uom, instance):
        price_list = data_price_list
        if price_list:
            bulk_data = [
                ExpensePrice(
                    expense=instance,
                    price_id=item['id'],
                    currency_id=currency_using,
                    price_value=item['value'],
                    is_auto_update=item['is_auto_update'],
                    uom=uom
                ) for item in price_list
            ]
            if len(bulk_data) > 0:
                ExpensePrice.objects.bulk_create(bulk_data)
        return True


class ExpenseDetailSerializer(serializers.ModelSerializer):
    price_list = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    @classmethod
    def get_price_list(cls, obj):
        price_list = [
            {
                'id': item.price_id,
                'title': item.price.title,
                'price_value': item.price_value,
                'is_auto_update': item.is_auto_update,
                'currency': item.currency_id,
                'is_primary': item.currency.is_primary,
                'abbreviation': item.currency.abbreviation
            } for item in obj.expense.all()
        ]
        return price_list


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=False, allow_null=False)
    expense_type = serializers.UUIDField(required=False)
    uom = serializers.UUIDField(required=False)
    uom_group = serializers.UUIDField(required=False)
    data_price_list = serializers.ListField(required=False)
    currency_using = serializers.UUIDField(required=False)
    role = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = Expense
        fields = (
            'title',
            'expense_type',
            'uom_group',
            'uom',
            'data_price_list',
            'currency_using',
            'role'
        )

    @classmethod
    def validate_expense_type(cls, value):
        try:
            if value is not None:
                expense_type = ExpenseType.objects.get(
                    id=value
                )
                return expense_type
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
                return uom_group
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
                return uom
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': ExpenseMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_currency_using(cls, value):
        try:
            if value is not None:
                currency = Currency.objects.get(
                    id=value
                )
                return currency.id
        except Currency.DoesNotExist:
            raise serializers.ValidationError({'expense_type': ExpenseMsg.CURRENCY_NOT_EXIST})
        return None

    def update(self, instance, validated_data):
        self.common_update_expense_general(validated_data=validated_data, instance=instance)
        del validated_data['currency_using']
        del validated_data['data_price_list']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @classmethod
    def common_update_expense_role(cls, instance, data):
        ExpenseRole.objects.filter(expense=instance).delete()
        ExpenseCreateSerializer.common_create_expense_role(data, instance)
        return True

    @classmethod
    def common_delete_expense_price(cls, instance, validate_data):
        expense_price_delete = ExpensePrice.objects.filter(
            expense=instance,
        )
        currency_using = validate_data['currency_using']
        price_list = validate_data['data_price_list']
        for item in expense_price_delete:
            if str(item.price_id) not in [obj["id"] for obj in price_list]:
                item.delete()
            else:
                if item.currency_id == currency_using:
                    item.delete()
        return True

    @classmethod
    def common_update_expense_general(cls, validated_data, instance):
        cls.common_delete_expense_price(instance=instance, validate_data=validated_data)
        data_role = validated_data.pop('role', [])
        cls.common_update_expense_role(instance=instance, data=data_role)
        ExpenseCreateSerializer.common_create_expense_price(
            validated_data['data_price_list'],
            validated_data['currency_using'],
            validated_data['uom'],
            instance
        )
        return True


class ExpenseForSaleListSerializer(serializers.ModelSerializer):
    expense_type = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = (
            'id',
            'code',
            'title',
            # 'price_list',
            'expense_type',
            'uom',
        )

    @classmethod
    def get_expense_type(cls, obj):
        if obj.expense_type:
            return {
                'id': obj.expense_type_id,
                'title': obj.expense_type.title,
                'code': obj.expense_type.code,
            }
        return {}

    @classmethod
    def get_uom(cls, obj):
        if obj.uom:
            return {
                'id': obj.uom_id,
                'title': obj.uom.title,
                'code': obj.uom.code,
            }
        return {}
