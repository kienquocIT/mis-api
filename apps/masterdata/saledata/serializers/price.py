from django.utils import timezone
from rest_framework import serializers
from apps.masterdata.saledata.models.price import (
    TaxCategory, Tax, Currency, Price, ProductPriceList, PriceListCurrency
)
from apps.masterdata.saledata.models.product import ExpensePrice
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


class TaxUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Tax
        fields = ('title', 'rate', 'category', 'type')


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


class PriceListSerializer(serializers.ModelSerializer):  # noqa
    price_list_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

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
            'status',
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

    @classmethod
    def get_status(cls, obj):
        if (not obj.valid_time_start >= timezone.now()) and (obj.valid_time_end >= timezone.now()):
            return 'Valid'
        if obj.valid_time_end < timezone.now():
            return 'Expired'
        if obj.valid_time_start >= timezone.now():
            return 'Invalid'
        return 'Undefined'


class PriceCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)
    valid_time_start = serializers.DateTimeField(required=True)
    valid_time_end = serializers.DateTimeField(required=True)
    price_list_mapped = serializers.UUIDField(required=False)

    class Meta:
        model = Price
        fields = (
            'title',
            'auto_update',
            'can_delete',
            'factor',
            'currency',
            'price_list_type',
            'price_list_mapped',
            'valid_time_start',
            'valid_time_end'
        )

    @classmethod
    def validate_price_list_mapped(cls, value):
        try:  # noqa
            if value is not None:
                obj = Price.objects.get_current(
                    id=value,
                    fill__company=True,
                    fill__tenant=True,
                )
                return obj
        except Price.DoesNotExist:
            raise serializers.ValidationError({'stage': PriceMsg.PRICE_SOURCE_NOT_EXIST})
        return None

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

    def validate(self, validate_data):
        if 'price_list_mapped' in validate_data:
            price_source = validate_data['price_list_mapped']
            price_type = validate_data['price_list_type']

            if price_source.price_list_type != price_type:
                raise serializers.ValidationError(PriceMsg.DIFFERENT_PRICE_LIST_TYPE)
            if validate_data.get('auto_update') is False and validate_data.get('can_delete') is True:
                raise serializers.ValidationError(PriceMsg.AUTO_UPDATE_CONFLICT_CAN_DELETE)
        else:
            if validate_data.get('auto_update') is True and validate_data.get('can_delete') is True:
                raise serializers.ValidationError(PriceMsg.AUTO_UPDATE_CAN_DELETE_ARE_FALSE)
        return validate_data

    @classmethod
    def common_create_currency(cls, data, instance):
        bulk_data = []
        for currency in data:
            bulk_data.append(
                PriceListCurrency(
                    currency_id=currency,
                    price=instance,
                )
            )
        PriceListCurrency.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def create_item_for_child_price_sale(cls, price):
        items_source = ProductPriceList.objects.filter(price_list=price.price_list_mapped)
        objs = [
            ProductPriceList(
                price_list=price,
                product=p.product,
                price=float(p.price) * float(price.factor),
                currency_using=p.currency_using,
                uom_using=p.uom_using,
                uom_group_using=p.uom_group_using,
                get_price_from_source=True
            ) for p in items_source
        ]
        ProductPriceList.objects.bulk_create(objs)
        return True

    @classmethod
    def create_item_for_child_price_expense(cls, price):
        items_source = ExpensePrice.objects.filter(price=price.price_list_mapped)
        objs = [
            ExpensePrice(
                price=price,
                expense=item.expense,
                price_value=float(item.price_value) * float(price.factor),
                currency=item.currency,
                uom=item.uom,
                is_auto_update=True,
            ) for item in items_source
        ]
        ExpensePrice.objects.bulk_create(objs)

        return True

    def create(self, validated_data):
        price_list = Price.objects.create(**validated_data)
        if 'auto_update' in validated_data.keys() and 'price_list_mapped' in validated_data.keys():
            if price_list.price_list_type == 0:
                self.create_item_for_child_price_sale(price_list)
            else:
                self.create_item_for_child_price_expense(price_list)

        if 'currency' in validated_data:
            self.common_create_currency(validated_data['currency'], price_list)
        return price_list


class PriceDetailSerializer(serializers.ModelSerializer):  # noqa
    products_mapped = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

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
            'products_mapped',
            'valid_time_start',
            'valid_time_end',
            'status'
        )

    @classmethod
    def get_products_mapped(cls, obj):
        all_products = []
        if obj.price_list_type == 0:
            products = ProductPriceList.objects.filter(
                price_list_id=obj.id,
                is_delete=False
            ).select_related('product', 'currency_using', 'uom_using', 'uom_group_using')
            for product in products:
                product_information = {
                    'id': product.product_id,
                    'code': product.product.code,
                    'title': product.product.title,
                    'uom_group': {'id': product.uom_group_using_id, 'title': product.uom_group_using.title},
                    'uom': {'id': product.uom_using_id, 'title': product.uom_using.title},
                    'price': product.price,
                    'is_auto_update': product.get_price_from_source,
                    'currency_using': {
                        'id': product.currency_using.id,
                        'abbreviation': product.currency_using.abbreviation
                    }
                }
                all_products.append(product_information)
        elif obj.price_list_type == 2:
            expenses = ExpensePrice.objects.filter(  # noqa
                price_id=obj.id,
            ).select_related('expense', 'currency', 'uom')
            for expense in expenses:
                uom_data = {}
                if expense.uom:
                    uom_data = {'id': expense.uom.id, 'title': expense.uom.title}
                expense_information = {
                    'id': expense.expense.id,
                    'code': expense.expense.code,
                    'title': expense.expense.title,
                    'uom_group': {
                        'id': expense.expense.uom_group.id,
                        'title': expense.expense.uom_group.title
                    },
                    'uom': uom_data,
                    'price': expense.price_value,
                    'is_auto_update': expense.is_auto_update,
                    'currency_using': {
                        'id': expense.currency.id, 'abbreviation': expense.currency.abbreviation
                    }
                }
                all_products.append(expense_information)
        return all_products

    @classmethod
    def get_price_list_mapped(cls, obj):
        if obj.price_list_mapped:
            return {
                'id': obj.price_list_mapped_id,
                'title': obj.price_list_mapped.title
            }
        return {}

    @classmethod
    def get_status(cls, obj):
        if (not obj.valid_time_start >= timezone.now()) and (obj.valid_time_end >= timezone.now()):
            return 'Valid'
        if obj.valid_time_end < timezone.now():
            return 'Expired'
        if obj.valid_time_start >= timezone.now():
            return 'Invalid'
        return 'Undefined'

    @classmethod
    def get_currency(cls, obj):
        if obj.currency_current:
            currencies = obj.currency_current.all()
            return [{
                'id': currency.id,
                'title': currency.title,
                'abbreviation': currency.abbreviation,
            } for currency in currencies]
        return []


def check_expired_price_list(price_list):
    if not price_list.valid_time_end < timezone.now():
        return True
    return False


class PriceUpdateSerializer(serializers.ModelSerializer):  # noqa

    factor = serializers.FloatField(required=False)
    currency = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = Price
        fields = (
            'auto_update',
            'can_delete',
            'factor',
            'currency',
        )

    @classmethod
    def validate_factor(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return None

    @classmethod
    def validate_currency(cls, value):
        list_result = []
        for currency_id in value:
            try:
                currency = Currency.objects.get_current(id=currency_id)
                list_result.append(str(currency.id))
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'currency': PriceMsg.CURRENCY_NOT_EXIST})
        return list_result

    @classmethod
    def update_price_instance(cls, instance, factor):
        if instance.price_list_type == 0:
            list_item = ProductPriceList.objects.filter(price_list=instance)
            for item in list_item:
                item.price = item.price / instance.factor * factor
                item.save(update_fields=['price'])
        else:
            list_item = ExpensePrice.objects.filter(price=instance)
            for item in list_item:
                item.price_value = item.price_value / instance.factor * factor
                item.save(update_fields=['price_value'])

        return list_item

    @classmethod
    def update_child_auto_update_for_sale(cls, instance, list_price, list_item):

        if not list_item:
            list_item = ProductPriceList.objects.filter(price_list=instance)

        bulk_data = []
        for price in list_price:
            if price[0] != instance and price[0].auto_update:
                ProductPriceList.objects.filter(price_list=price[0]).delete()
                for item in list_item:
                    bulk_data.append(
                        ProductPriceList(
                            price_list=price[0],
                            product=item.product,
                            uom_using=item.uom_using,
                            uom_group_using=item.uom_group_using,
                            currency_using=item.currency_using,
                            get_price_from_source=price[0].auto_update,
                            price=item.price * price[0].factor
                        )
                    )
        ProductPriceList.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_child_auto_update_for_expense(cls, instance, list_price, list_item):

        if not list_item:
            list_item = ExpensePrice.objects.filter(price=instance)

        bulk_data = []
        for price in list_price:
            if price[0] != instance and price[0].auto_update:
                ExpensePrice.objects.filter(price=price[0]).delete()
                for item in list_item:
                    bulk_data.append(
                        ExpensePrice(
                            price=price[0],
                            expense=item.expense,
                            uom=item.uom,
                            currency=item.currency,
                            is_auto_update=price[0].auto_update,
                            price_value=item.price_value * price[0].factor
                        )
                    )
        ExpensePrice.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_with_factor(cls, instance, validated_data):
        list_item = None

        if instance.auto_update:
            list_item = cls.update_price_instance(instance, validated_data['factor'])

        list_price = PriceListCommon.get_child_price_list(instance)

        if instance.price_list_type == 0:
            list_item = ProductPriceList.objects.filter(price_list=instance) if not list_item else None
            cls.update_child_auto_update_for_sale(instance, list_price, list_item)
        else:
            list_item = ExpensePrice.objects.filter(price=instance) if not list_item else None
            cls.update_child_auto_update_for_expense(instance, list_price, list_item)
        return list_price

    @classmethod
    def update_with_currency(cls, instance, list_price, validated_data):

        if not list_price:
            list_price = PriceListCommon.get_child_price_list(instance)

        for price in list_price:
            PriceListCurrency.objects.filter(price=price[0]).delete()
            PriceCreateSerializer.common_create_currency(validated_data['currency'], price[0])
        return True

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):
            list_price = None
            # update with factor
            if 'factor' in validated_data:
                list_price = self.update_with_factor(instance, validated_data)

            # update with currency
            if 'currency' in validated_data:
                self.update_with_currency(instance, list_price, validated_data)

            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            return instance
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)


class PriceDeleteSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = ()

    def update(self, instance, validated_data):
        if ProductPriceList.objects.filter(price_list=instance).exists():
            raise serializers.ValidationError(PriceMsg.NON_EMPTY_PRICE_LIST_CANT_BE_DELETE)
        if Price.objects.filter_current(fill__tenant=True, fill__company=True, price_list_mapped=instance.id).exists():
            raise serializers.ValidationError(PriceMsg.PARENT_PRICE_LIST_CANT_BE_DELETE)
        instance.delete()  # delete price list
        return True


class ItemForUpdatePriceSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField(required=True)
    uom_id = serializers.UUIDField(required=True)
    currency = serializers.UUIDField(required=True)
    uom_group_id = serializers.UUIDField(required=False)
    price = serializers.FloatField(required=True)


class PriceListUpdateItemsSerializer(serializers.ModelSerializer):  # noqa
    list_item = serializers.ListField(child=ItemForUpdatePriceSerializer())

    class Meta:
        model = Price
        fields = (
            'list_item',
        )

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):  # not expired
            if instance.price_list_type == 0:
                self.update_price_value_product(instance, validated_data)
            else:
                self.update_price_value_expense(instance, validated_data)
            return instance
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)

    @classmethod
    def update_price_value_product(cls, instance, validated_data):
        list_price = PriceListCommon.get_child_price_list(instance)
        list_item = validated_data['list_item']

        ProductPriceList.objects.filter(
            price_list__in=[item[0] for item in list_price],
            product_id__in=[str(item['product_id']) for item in list_item],
            uom_using_id__in=[str(item['uom_id']) for item in list_item],
            currency_using_id__in=[str(item['currency']) for item in list_item],
            uom_group_using_id__in=[str(item['uom_group_id']) for item in list_item]
        ).delete()

        bulk_data = []
        for price in list_price:
            for item in list_item:
                bulk_data.append(
                    ProductPriceList(
                        price_list=price[0],
                        product_id=str(item['product_id']),
                        uom_using_id=str(item['uom_id']),
                        currency_using_id=str(item['currency']),
                        uom_group_using_id=str(item['uom_group_id']),
                        get_price_from_source=price[0].auto_update,
                        price=item['price'] * price[1],
                    )
                )

        ProductPriceList.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_price_value_expense(cls, instance, validated_data):
        list_price = PriceListCommon.get_child_price_list(instance)
        list_item = validated_data['list_item']

        ExpensePrice.objects.filter(
            price__in=[item[0] for item in list_price],
            expense_id__in=[str(item['product_id']) for item in list_item],
            uom_id__in=[str(item['uom_id']) for item in list_item],
            currency_id__in=[str(item['currency']) for item in list_item],
        ).delete()

        bulk_data = []
        for price in list_price:
            for item in list_item:
                bulk_data.append(
                    ExpensePrice(
                        price=price[0],
                        expense_id=str(item['product_id']),
                        uom_id=str(item['uom_id']),
                        currency_id=str(item['currency']),
                        is_auto_update=price[0].auto_update,
                        price_value=item['price'] * price[1],
                    )
                )
        ExpensePrice.objects.bulk_create(bulk_data)
        return True


class ItemForDeleteSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()
    uom_id = serializers.UUIDField()


class PriceListDeleteItemSerializer(serializers.ModelSerializer):  # noqa
    item = ItemForDeleteSerializer(required=True)

    class Meta:
        model = Price
        fields = (
            'item',
        )

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):  # not expired
            list_price = PriceListCommon.get_child_price_list(instance)
            item = validated_data['item']
            if list_price:
                if instance.price_list_type == 0:
                    ProductPriceList.objects.filter(
                        product_id=str(item['id']),
                        price_list__in=[price[0] for price in list_price],
                        uom_using_id=str(item['uom_id']),
                    ).delete()
                else:
                    ExpensePrice.objects.filter(
                        expense_id=str(item['id']),
                        price_list__in=[price[0] for price in list_price],
                        uom_id=str(item['uom_id']),
                    ).delete()
            return True
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)


class ItemForCreateInPriceListSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()
    uom = serializers.UUIDField()
    uom_group = serializers.UUIDField()


class CreateItemInPriceListSerializer(serializers.ModelSerializer):
    product = ItemForCreateInPriceListSerializer(required=True)

    class Meta:
        model = Price
        fields = (
            'product',
        )

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):  # not expired
            price_list_information = PriceListCommon.get_child_price_list(instance)
            product = self.validated_data['product']
            objs = []
            if price_list_information and product:
                for item in price_list_information:
                    if instance.price_list_type == 0:
                        obj = self.add_product_for_price_list(
                            price=item[0],
                            product=product,
                            instance=instance,
                        )
                        if not obj:
                            raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                        objs.append(obj)
                    else:
                        obj = self.add_expense_for_price_list(
                            price=item[0],
                            expense=product,
                            instance=instance,
                        )
                        if not obj:
                            raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                        objs.append(obj)
            if len(objs) > 0:
                if instance.price_list_type == 0:
                    ProductPriceList.objects.bulk_create(objs)
                else:
                    ExpensePrice.objects.bulk_create(objs)
            return instance
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)

    @classmethod
    def add_product_for_price_list(cls, price, product, instance):
        if not ProductPriceList.objects.filter(
                price_list=price,
                product_id=product['id'],
                uom_using_id=product['uom']
        ).exists():
            obj = (
                ProductPriceList(
                    price_list=price,
                    product_id=product['id'],
                    price=0,
                    currency_using_id=instance.currency[0],
                    uom_using_id=product['uom'],
                    uom_group_using_id=product['uom_group'],
                    get_price_from_source=price.auto_update
                )
            )
            return obj
        return None

    @classmethod
    def add_expense_for_price_list(cls, price, expense, instance):
        if not ExpensePrice.objects.filter(  # noqa
                price=price,
                expense_id=expense['id'],
                uom_id=expense['uom']
        ).exists():
            obj = (
                ExpensePrice(
                    price=price,
                    expense_id=expense['id'],
                    price_value=0,
                    currency_id=instance.currency[0],
                    uom_id=expense['uom'],
                    is_auto_update=price.auto_update,
                )
            )
            return obj
        return None


class PriceListCommon:
    @staticmethod
    def get_child_price_list(price, parent_factor=1):
        if price.valid_time_end is not None and price.valid_time_end < timezone.now():
            return []

        factor = price.factor * parent_factor
        descendants_with_factor = [(price, factor)]

        for child in Price.objects.filter(price_list_mapped=price.id, valid_time_end__gt=timezone.now()):
            child_descendants = PriceListCommon.get_child_price_list(child, parent_factor=factor)
            descendants_with_factor.extend(child_descendants)

        return descendants_with_factor
