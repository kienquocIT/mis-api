from django.utils import timezone
from rest_framework import serializers
from apps.masterdata.saledata.models.price import (
    TaxCategory, Tax, Currency, Price, ProductPriceList
)
from apps.masterdata.saledata.models.product import ExpensePrice, Expense
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
            price_list_mapped = Price.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=validate_data['price_list_mapped']
            ).first()
            if price_list_mapped:
                if price_list_mapped.price_list_type != validate_data.get('price_list_type', None):
                    raise serializers.ValidationError(PriceMsg.DIFFERENT_PRICE_LIST_TYPE)
            else:
                raise serializers.ValidationError(PriceMsg.PRICE_LIST_NOT_EXIST)
        return validate_data

    def create(self, validated_data):
        price_list = Price.objects.create(**validated_data)
        if 'auto_update' in validated_data.keys() and 'price_list_mapped' in validated_data.keys():
            products_source = ProductPriceList.objects.filter(price_list_id=validated_data['price_list_mapped'])
            objs = [
                ProductPriceList(
                    price_list=price_list,
                    product=p.product,
                    price=float(p.price) * float(price_list.factor),
                    currency_using=p.currency_using,
                    uom_using=p.uom_using,
                    uom_group_using=p.uom_group_using,
                    get_price_from_source=True
                ) for p in products_source
            ]
            ProductPriceList.objects.bulk_create(objs)
        return price_list


class PriceDetailSerializer(serializers.ModelSerializer):  # noqa
    products_mapped = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()
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
            ).select_related('expense_general', 'currency', 'uom')
            for expense in expenses:
                uom_data = {}
                if expense.uom:
                    uom_data = {'id': expense.uom.id, 'title': expense.uom.title}
                expense_information = {
                    'id': expense.expense_general.expense.id,
                    'code': expense.expense_general.expense.code,
                    'title': expense.expense_general.expense.title,
                    'uom_group': {
                        'id': expense.expense_general.uom_group.id,
                        'title': expense.expense_general.uom_group.title
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

    @classmethod
    def get_status(cls, obj):
        if (not obj.valid_time_start >= timezone.now()) and (obj.valid_time_end >= timezone.now()):
            return 'Valid'
        if obj.valid_time_end < timezone.now():
            return 'Expired'
        if obj.valid_time_start >= timezone.now():
            return 'Invalid'
        return 'Undefined'


def check_expired_price_list(price_list):
    if not price_list.valid_time_end < timezone.now():
        return True
    return False


def get_product_when_turn_on_auto_update(instance):
    # get all products of instance
    items_id_of_instance = list(
        ProductPriceList.objects.filter(price_list=instance).values_list('product', flat=True)
    )
    # get all products of source
    items_of_source = ProductPriceList.objects.filter(price_list_id=instance.price_list_mapped)

    new_list = []
    for item in items_of_source:
        if item.product_id in items_id_of_instance:
            new_list.append(
                ProductPriceList(
                    price_list=instance,
                    product=item.product,
                    price=float(item.price) * float(instance.factor),
                    currency_using=item.currency_using,
                    uom_using=item.uom_using,
                    uom_group_using=item.uom_group_using,
                    get_price_from_source=True
                )
            )
            ProductPriceList.objects.filter(product=item.product, price_list=instance).delete()
    if len(new_list) > 0:
        ProductPriceList.objects.bulk_create(new_list)
    return True


class PriceUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = (
            'auto_update',
            'can_delete',
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
        if check_expired_price_list(instance):  # not expired
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            if instance.auto_update:
                get_product_when_turn_on_auto_update(instance)
            else:
                ProductPriceList.objects.filter(price_list=instance).update(get_price_from_source=False)
            return instance
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)


class PriceDeleteSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = ()

    def update(self, instance, validated_data):
        if ProductPriceList.objects.filter(price_list=instance).exists():
            raise serializers.ValidationError(PriceMsg.NON_EMPTY_PRICE_LIST_CANT_BE_DELETE)
        if not Price.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                price_list_mapped=instance.id
        ).exists():
            ProductPriceList.objects.filter(price_list=instance).delete()  # delete all item in M2M table
            instance.delete()  # delete price list
            return True
        raise serializers.ValidationError(PriceMsg.PARENT_PRICE_LIST_CANT_BE_DELETE)


class PriceListUpdateItemsSerializer(serializers.ModelSerializer):  # noqa
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
        if check_expired_price_list(instance):  # not expired
            if instance.price_list_type == 0:
                self.update_price_value_product(instance, validated_data)
            else:
                self.update_price_value_expense(instance, validated_data)
            return instance
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)

    @classmethod
    def update_price_value_product(cls, instance, validated_data):
        objs = []
        list_price_list_delete = []
        for price in validated_data['list_price']:
            for item in validated_data['list_item']:
                found = True # noqa
                value_price = 0
                is_auto_update = True

                product_price_list_obj = ProductPriceList.objects.filter(
                    product_id=item['product_id'],
                    price_list_id=price['id'],
                    currency_using_id=item['currency'],
                    uom_using_id=item['uom_id']
                ).first()
                if product_price_list_obj:
                    is_auto_update = product_price_list_obj.get_price_from_source
                    value_price = product_price_list_obj.price
                    list_price_list_delete.append(product_price_list_obj)
                else:
                    product_price_list_old = ProductPriceList.objects.filter(
                        product_id=item['product_id'],
                        price_list_id=price['id'],
                    ).first()
                    if product_price_list_old:
                        is_auto_update = product_price_list_old.get_price_from_source
                        value_price = 0
                    else:
                        found = False

                result_price = float(item['price']) * float(price['factor'])
                if price['id'] != str(instance.id):
                    if is_auto_update is False:
                        result_price = value_price
                if found:
                    objs.append(
                        ProductPriceList(
                            price_list_id=price['id'],
                            product_id=item['product_id'],
                            price=result_price,
                            currency_using_id=item['currency'],
                            uom_using_id=item['uom_id'],
                            uom_group_using_id=item['uom_group_id'],
                            get_price_from_source=is_auto_update
                        )
                    )
        for item in list_price_list_delete:
            item.delete()
        if len(objs) > 0:
            ProductPriceList.objects.bulk_create(objs)
        return True

    @classmethod
    def update_price_value_expense(cls, instance, validated_data):
        objs = [] # noqa
        list_price_list_delete = []
        for price in validated_data['list_price']:
            for item in validated_data['list_item']:
                found = True # noqa
                value_price = 0
                is_auto_update = True

                expense_price_list_obj = ExpensePrice.objects.filter(
                    expense_general__expense__id=item['product_id'],
                    price_id=price['id'],
                    currency_id=item['currency'],
                    uom_id=item['uom_id']
                ).first()
                if expense_price_list_obj:
                    is_auto_update = expense_price_list_obj.is_auto_update
                    value_price = expense_price_list_obj.price_value
                    list_price_list_delete.append(expense_price_list_obj)
                else:
                    expense_price_list_old = ExpensePrice.objects.filter(
                        expense_general__expense__id=item['product_id'],
                        price_id=price['id'],
                    ).first()
                    if expense_price_list_old:
                        is_auto_update = expense_price_list_old.is_auto_update
                        value_price = 0
                    else:
                        found = False

                result_price = float(item['price']) * float(price['factor'])
                if price['id'] != str(instance.id):
                    if is_auto_update is False:
                        result_price = value_price
                if found:
                    expense_general = Expense.objects.filter(id=item['product_id']).first().expense
                    objs.append(
                        ExpensePrice(
                            price_id=price['id'],
                            expense_general=expense_general,
                            price_value=result_price,
                            currency_id=item['currency'],
                            uom_id=item['uom_id'],
                            is_auto_update=is_auto_update
                        )
                    )
        for item in list_price_list_delete:
            item.delete()
        if len(objs) > 0:
            ExpensePrice.objects.bulk_create(objs)
        return True


class PriceListDeleteItemSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Price
        fields = ()

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):  # not expired
            list_price = self.initial_data.get('list_price', None)
            if list_price:
                if instance.price_list_type == 0:
                    for item in list_price:
                        obj = ProductPriceList.objects.filter(
                            product_id=self.initial_data.get('product_id', None),
                            price_list_id=item.get('id', None),
                            uom_using_id=self.initial_data.get('uom_id', None)
                        )
                        if obj:
                            obj.delete()
                else:
                    for item in list_price:
                        obj = ExpensePrice.objects.filter(
                            expense_general__expense__id=self.initial_data.get('product_id', None),
                            price_id=item.get('id', None),
                            uom_id=self.initial_data.get('uom_id', None)
                        )
                        if obj:
                            obj.delete()
            return True
        raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)


class CreateItemInPriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ()

    def update(self, instance, validated_data):
        if check_expired_price_list(instance):  # not expired
            price_list_information = self.initial_data['list_price_list']
            product = self.initial_data['product']
            objs = []
            if price_list_information and product:
                for item in price_list_information:
                    get_price_from_source = False
                    if item.get('is_auto_update', None) == '1':
                        get_price_from_source = True
                    if instance.price_list_type == 0:
                        obj = self.add_product_for_price_list(
                                item=item,
                                product=product,
                                instance=instance,
                                is_auto_update=get_price_from_source
                            )
                        if not obj:
                            raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                        objs.append(obj)
                    else:
                        obj = self.add_expense_for_price_list(
                                item=item,
                                expense=product,
                                instance=instance,
                                is_auto_update=get_price_from_source
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
    def add_product_for_price_list(cls, item, product, instance, is_auto_update):
        if not ProductPriceList.objects.filter(
                price_list_id=item['price_list_id'],
                product_id=product['id'],
                uom_using_id=product['uom']
        ).exists():
            obj = (
                ProductPriceList(
                    price_list_id=item.get('price_list_id', None),
                    product_id=product['id'],
                    price=0,
                    currency_using_id=instance.currency[0],
                    uom_using_id=product['uom'],
                    uom_group_using_id=product['uom_group'],
                    get_price_from_source=is_auto_update
                )
            )
            return obj
        return None

    @classmethod
    def add_expense_for_price_list(cls, item, expense, instance, is_auto_update):
        if not ExpensePrice.objects.filter(  # noqa
                price_id=item['price_list_id'],
                expense_general__expense__id=expense['id'],
                uom_id=expense['uom']
        ).exists():
            expense_general = Expense.objects.filter(id=expense['id']).first().expense
            obj = (
                ExpensePrice(
                    price_id=item.get('price_list_id', None),
                    expense_general=expense_general,
                    price_value=0,
                    currency_id=instance.currency[0],
                    uom_id=expense['uom'],
                    is_auto_update=is_auto_update
                )
            )
            return obj
        return None
