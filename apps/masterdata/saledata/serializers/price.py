from datetime import datetime

from rest_framework import serializers

from apps.masterdata.saledata.models import Product, UnitOfMeasure, UnitOfMeasureGroup
from apps.masterdata.saledata.models.price import (
    Currency, Price, ProductPriceList, PriceListCurrency
)
from apps.masterdata.saledata.models.product import ExpensePrice, Expense
from apps.shared import PriceMsg, ProductMsg


# Price list config
class PriceListSerializer(serializers.ModelSerializer):
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
            'valid_time_start',
            'valid_time_end',
            'status',
        )

    @classmethod
    def get_price_list_type(cls, obj):
        if obj.price_list_type == 0:
            return {
                'value': obj.price_list_type,
                'name': 'For Sale'
            }
        if obj.price_list_type == 1:
            return {
                'value': obj.price_list_type,
                'name': 'For Purchase'
            }
        if obj.price_list_type == 2:
            return {
                'value': obj.price_list_type,
                'name': 'For Expense'
            }
        return {}

    @classmethod
    def get_status(cls, obj):
        if obj.valid_time_start.date() <= datetime.now().date() and obj.valid_time_end.date() >= datetime.now().date():
            return 'Valid'
        if obj.valid_time_end.date() < datetime.now().date():
            return 'Expired'
        if obj.valid_time_start.date() >= datetime.now().date():
            return 'Invalid'
        return 'Undefined'


class PriceCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)
    valid_time_start = serializers.DateTimeField(required=True)
    valid_time_end = serializers.DateTimeField(required=True)
    price_list_mapped = serializers.UUIDField(required=False, allow_null=True)

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
        if Price.objects.filter_current(fill__tenant=True, fill__company=True, title=value).exists():
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
        return value

    @classmethod
    def validate_factor(cls, value):
        if value is not None:
            if value > 0:
                return value
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return 1

    def validate(self, validate_data):
        if 'price_list_mapped' in validate_data and validate_data.get('price_list_mapped') is not None:
            price_list_mapped_obj = Price.objects.filter(id=validate_data['price_list_mapped']).first()
            if price_list_mapped_obj:
                validate_data['price_list_mapped'] = price_list_mapped_obj
                if price_list_mapped_obj.price_list_type != validate_data['price_list_type']:
                    raise serializers.ValidationError({'detail': PriceMsg.DIFFERENT_PRICE_LIST_TYPE})
                if validate_data.get('auto_update') is False and validate_data.get('can_delete') is True:
                    raise serializers.ValidationError({'detail': PriceMsg.AUTO_UPDATE_CONFLICT_CAN_DELETE})
            else:
                raise serializers.ValidationError({'price_list_mapped_obj': PriceMsg.PRICE_LIST_NOT_EXIST})
        else:
            if validate_data.get('auto_update') and validate_data.get('can_delete'):
                raise serializers.ValidationError({'detail': PriceMsg.AUTO_UPDATE_CAN_DELETE_ARE_FALSE})

        currency_data = Currency.objects.filter(id__in=validate_data.get('currency', []))
        if currency_data.count() != len(validate_data.get('currency', [])):
            raise serializers.ValidationError({'detail': PriceMsg.CURRENCY_NOT_EXIST})
        validate_data['currency'] = [str(item) for item in currency_data.values_list('id', flat=True)]
        return validate_data

    @classmethod
    def create_items_from_root(cls, price_list_obj):
        if price_list_obj.price_list_type == 0:
            bulk_info = []
            for item in ProductPriceList.objects.filter(price_list=price_list_obj.price_list_mapped):
                bulk_info.append(ProductPriceList(
                    price_list=price_list_obj,
                    product=item.product,
                    price=float(item.price) * float(price_list_obj.factor),
                    currency_using=item.currency_using,
                    uom_using=item.uom_using,
                    uom_group_using=item.uom_group_using,
                    get_price_from_source=True
                ))
            ProductPriceList.objects.bulk_create(bulk_info)
        else:
            bulk_info = []
            for item in ExpensePrice.objects.filter(price=price_list_obj.price_list_mapped):
                bulk_info.append(ExpensePrice(
                    price=price_list_obj,
                    expense=item.expense,
                    price_value=float(item.price_value) * float(price_list_obj.factor),
                    currency=item.currency,
                    uom=item.uom,
                    is_auto_update=True,
                ))
            ExpensePrice.objects.bulk_create(bulk_info)
        return True

    def create(self, validated_data):
        price_list_obj = Price.objects.create(**validated_data)
        if 'auto_update' in validated_data and 'price_list_mapped' in validated_data:
            self.create_items_from_root(price_list_obj)
        if 'currency' in validated_data:
            bulk_data = []
            for item in validated_data['currency']:
                bulk_data.append(PriceListCurrency(currency_id=item, price=price_list_obj))
            PriceListCurrency.objects.bulk_create(bulk_data)
        return price_list_obj


class PriceDetailSerializer(serializers.ModelSerializer):
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
            for item in ProductPriceList.objects.filter(
                    price_list=obj, currency_using_id__in=obj.currency
            ).select_related('product', 'currency_using', 'uom_using', 'uom_group_using'):
                if item.product:
                    all_products.append({
                        'id': item.product_id,
                        'code': item.product.code,
                        'title': item.product.title,
                        'uom_group': {
                            'id': item.uom_group_using_id,
                            'code': item.uom_group_using.code,
                            'title': item.uom_group_using.title
                        } if item.uom_group_using else {},
                        'uom': {
                            'id': item.uom_using_id,
                            'code': item.uom_using.code,
                            'title': item.uom_using.title
                        } if item.uom_using else {},
                        'price': item.price,
                        'is_auto_update': item.get_price_from_source,
                        'currency_using': {
                            'id': item.currency_using_id,
                            'abbreviation': item.currency_using.abbreviation
                        } if item.currency_using else {},
                    })
        elif obj.price_list_type == 2:
            for item in ExpensePrice.objects.filter(price=obj, currency_id__in=obj.currency).select_related(
                    'expense', 'currency', 'uom__group'
            ):
                if item.expense:
                    all_products.append({
                        'id': item.expense_id,
                        'code': item.expense.code,
                        'title': item.expense.title,
                        'uom_group': {
                            'id': item.uom.group_id,
                            'code': item.uom.group.code,
                            'title': item.uom.group.title
                        } if item.uom.group else {},
                        'uom': {
                            'id': item.uom_id,
                            'code': item.uom.code,
                            'title': item.uom.title
                        } if item.uom else {},
                        'price': item.price_value,
                        'is_auto_update': item.is_auto_update,
                        'currency_using': {
                            'id': item.currency_id,
                            'abbreviation': item.currency.abbreviation
                        } if item.currency else {},
                    })
        return all_products

    @classmethod
    def get_price_list_mapped(cls, obj):
        return {
            'id': obj.price_list_mapped_id,
            'title': obj.price_list_mapped.title
        } if obj.price_list_mapped else {}

    @classmethod
    def get_status(cls, obj):
        if obj.valid_time_start.date() <= datetime.now().date() and obj.valid_time_end.date() >= datetime.now().date():
            return 'Valid'
        if obj.valid_time_end.date() < datetime.now().date():
            return 'Expired'
        if obj.valid_time_start.date() >= datetime.now().date():
            return 'Invalid'
        return 'Undefined'

    @classmethod
    def get_currency(cls, obj):
        return [{
            'id': currency.id,
            'title': currency.title,
            'abbreviation': currency.abbreviation,
        } for currency in obj.currency_current.all()] if obj.currency_current else []


class PriceUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)
    factor = serializers.FloatField(required=False)
    currency = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = Price
        fields = (
            'title',
            'auto_update',
            'can_delete',
            'factor',
            'currency',
        )

    def validate_title(self, value):
        if Price.objects.filter_current(
                fill__tenant=True, fill__company=True, title=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(PriceMsg.TITLE_EXIST)
        return value

    @classmethod
    def validate_factor(cls, attrs):
        if attrs is not None:
            if attrs > 0:
                return attrs
            raise serializers.ValidationError(PriceMsg.FACTOR_MUST_BE_GREATER_THAN_ZERO)
        return 1

    @classmethod
    def validate_currency(cls, value):
        currency_list = Currency.objects.filter(id__in=value)
        if currency_list.count() != len(value):
            raise serializers.ValidationError({'currency': PriceMsg.CURRENCY_NOT_EXIST})
        return [str(item) for item in currency_list.values_list('id', flat=True)]

    def validate(self, validate_data):
        if self.instance.is_expired(self.instance):
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)
        return validate_data

    @classmethod
    def update_price_list_item(cls, price_list_obj):
        if price_list_obj.price_list_type == 0:
            root_price_list_item = ProductPriceList.objects.filter(
                price_list=price_list_obj.price_list_mapped
            ).select_related('product', 'uom_using', 'currency_using')
            for item in ProductPriceList.objects.filter(price_list=price_list_obj, get_price_from_source=True):
                root_item = root_price_list_item.filter(
                    product=item.product, uom_using=item.uom_using, currency_using=item.currency_using
                ).first()
                if root_item:
                    item.price = root_item.price * price_list_obj.factor
                    item.save(update_fields=['price'])
            cls.update_child_price_list_for_sale(price_list_obj)
        else:
            root_price_list_item = ExpensePrice.objects.filter(
                price=price_list_obj.price_list_mapped
            ).select_related('expense', 'uom', 'currency')
            for item in ExpensePrice.objects.filter(price=price_list_obj, is_auto_update=True):
                root_item = root_price_list_item.filter(
                    expense=item.expense, uom=item.uom, currency=item.currency
                ).first()
                if root_item:
                    item.price_value = root_item.price_value * price_list_obj.factor
                    item.save(update_fields=['price_value'])
            cls.update_child_price_list_for_expense(price_list_obj)
        return True

    @classmethod
    def update_child_price_list_for_sale(cls, price_list_obj):
        bulk_data = []
        for child_obj, child_factor in Price.get_children(price_list_obj):
            if child_obj != price_list_obj and child_obj.auto_update:
                ProductPriceList.objects.filter(price_list=child_obj).delete()
                for item in ProductPriceList.objects.filter(price_list=price_list_obj):
                    bulk_data.append(ProductPriceList(
                        price_list=child_obj,
                        product=item.product,
                        uom_using=item.uom_using,
                        uom_group_using=item.uom_group_using,
                        currency_using=item.currency_using,
                        get_price_from_source=child_obj.auto_update,
                        price=item.price * child_factor
                    ))
        ProductPriceList.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_child_price_list_for_expense(cls, price_list_obj):
        bulk_data = []
        for child_obj, child_factor in Price.get_children(price_list_obj):
            if child_obj != price_list_obj and child_obj.auto_update:
                ExpensePrice.objects.filter(price=child_obj).delete()
                for item in ExpensePrice.objects.filter(price=price_list_obj):
                    bulk_data.append(ExpensePrice(
                        price=child_obj,
                        expense=item.expense,
                        uom=item.uom,
                        currency=item.currency,
                        is_auto_update=child_obj.auto_update,
                        price_value=item.price_value * child_factor
                    ))
        ExpensePrice.objects.bulk_create(bulk_data)
        return True

    def update(self, instance, validated_data):
        old_factor = instance.factor
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if 'factor' in validated_data:
            if instance.auto_update:
                self.update_price_list_item(instance)
            else:
                instance.factor = old_factor
                instance.save(update_fields=['factor'])
        if 'currency' in validated_data:
            children = Price.get_children(instance)
            bulk_data = []
            for child_obj, _ in children:
                PriceListCurrency.objects.filter(price=child_obj).delete()
                for item in instance.currency:
                    bulk_data.append(PriceListCurrency(currency_id=item, price=child_obj))
            PriceListCurrency.objects.bulk_create(bulk_data)
        return instance


class PriceDeleteSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Price
        fields = ()

    def validate(self, validate_data):
        if self.instance.is_default:
            raise serializers.ValidationError(PriceMsg.CANT_DELETE_GENERAL_PRICE_LIST)

        if Price.objects.filter(price_list_mapped=self.instance).exists():
            raise serializers.ValidationError(PriceMsg.PARENT_PRICE_LIST_CANT_BE_DELETE)

        if self.instance.price_list_type == 0:
            if ProductPriceList.objects.filter(
                    price_list=self.instance, currency_using_id__in=self.instance.currency
            ).exists():
                raise serializers.ValidationError(PriceMsg.NON_EMPTY_PRICE_LIST_CANT_BE_DELETE)
        else:
            if ExpensePrice.objects.filter(price=self.instance, currency_id__in=self.instance.currency).exists():
                raise serializers.ValidationError(PriceMsg.NON_EMPTY_PRICE_LIST_CANT_BE_DELETE)
        return validate_data

    def update(self, instance, validated_data):
        instance.delete()
        return True


# Price list item
class PriceListUpdateItemSerializer(serializers.ModelSerializer):  # noqa
    list_item = serializers.ListField()

    class Meta:
        model = Price
        fields = (
            'list_item',
        )

    def validate(self, validate_data):
        if self.instance.is_expired(self.instance):
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)
        list_item_data = []
        for item in validate_data.get('list_item', []):
            product_obj = Product.objects.filter(id=item.get('product_id')).first()
            uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
            currency_obj = Currency.objects.filter(id=item.get('currency')).first()
            uom_group_obj = UnitOfMeasureGroup.objects.filter(id=item.get('uom_group_id')).first()
            if not product_obj:
                raise serializers.ValidationError({'product_obj': ProductMsg.PRODUCT_DOES_NOT_EXIST})
            if not uom_obj:
                raise serializers.ValidationError({'uom_obj': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
            if not currency_obj:
                raise serializers.ValidationError({'currency_obj': ProductMsg.CURRENCY_DOES_NOT_EXIST})
            if not uom_group_obj:
                raise serializers.ValidationError({'uom_group_obj': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST})
            if not isinstance(float(item.get('price')), (int, float)):
                price = 0
            else:
                price = float(item.get('price'))
            list_item_data.append({
                'product_obj': product_obj,
                'uom_obj': uom_obj,
                'currency_obj': currency_obj,
                'uom_group_obj': uom_group_obj,
                'price': price
            })
        validate_data['list_item_data'] = list_item_data
        return validate_data

    def update(self, instance, validated_data):
        if instance.price_list_type == 0:
            self.update_price_value_product(instance, validated_data['list_item_data'])
        else:
            self.update_price_value_expense(instance, validated_data['list_item_data'])
        return instance

    @classmethod
    def update_price_value_product(cls, instance, list_item_data):
        children = Price.get_children(instance)
        ProductPriceList.objects.filter(
            price_list__in=[child_obj for child_obj, child_factor in children],
            product__in=[item['product_obj'] for item in list_item_data],
            uom_using__in=[item['uom_obj'] for item in list_item_data],
            currency_using__in=[item['currency_obj'] for item in list_item_data],
            uom_group_using__in=[item['uom_group_obj'] for item in list_item_data]
        ).delete()
        bulk_data = []
        for price_list_obj, price_list_factor in children:
            for item in list_item_data:
                bulk_data.append(ProductPriceList(
                    price_list=price_list_obj,
                    product=item['product_obj'],
                    uom_using=item['uom_obj'],
                    currency_using=item['currency_obj'],
                    uom_group_using=item['uom_group_obj'],
                    get_price_from_source=price_list_obj.auto_update,
                    price=item['price'] * price_list_factor,
                ))
        ProductPriceList.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_price_value_expense(cls, instance, list_item_data):
        children = Price.get_children(instance)
        ExpensePrice.objects.filter(
            price__in=[child_obj for child_obj, child_factor in children],
            expense__in=[item['product_obj'] for item in list_item_data],
            uom__in=[item['uom_obj'] for item in list_item_data],
            currency__in=[item['currency_obj'] for item in list_item_data],
        ).delete()

        bulk_data = []
        for child_obj, child_factor in children:
            for item in list_item_data:
                bulk_data.append(ExpensePrice(
                    price=child_obj,
                    expense=item['product_obj'],
                    uom=item['uom_obj'],
                    currency=item['currency_obj'],
                    is_auto_update=child_obj.auto_update,
                    price_value=item['price'] * child_factor,
                ))
        ExpensePrice.objects.bulk_create(bulk_data)
        return True


class PriceListDeleteItemSerializer(serializers.ModelSerializer):  # noqa
    item = serializers.DictField(required=True)

    class Meta:
        model = Price
        fields = ('item',)

    def validate(self, validate_data):
        if self.instance.is_expired(self.instance):
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)
        if not self.instance.can_delete:
            raise serializers.ValidationError(PriceMsg.CANT_DELETE_ITEM)

        item_data = validate_data.get('item', {})
        if self.instance.price_list_type == 0:
            item_obj = Product.objects.filter(id=item_data.get('id')).first()
        else:
            item_obj = Expense.objects.filter(id=item_data.get('id')).first()

        if not item_obj:
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_ITEM_NOT_EXIST)
        validate_data['item_obj'] = item_obj

        uom_obj = UnitOfMeasure.objects.filter(id=item_data.get('uom_id')).first()
        if uom_obj:
            validate_data['uom_obj'] = uom_obj
        else:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_NOT_EXIST)
        return validate_data

    def update(self, instance, validated_data):
        children = [child_obj for child_obj, _ in Price.get_children(instance)]
        item_obj = validated_data['item_obj']
        uom_obj = validated_data['uom_obj']
        if instance.price_list_type == 0:
            ProductPriceList.objects.filter(product=item_obj, price_list__in=children, uom_using=uom_obj).delete()
        else:
            ExpensePrice.objects.filter(expense=item_obj, price_list__in=children, uom=uom_obj).delete()
        return instance


class PriceListCreateItemSerializer(serializers.ModelSerializer):
    product = serializers.DictField(required=True)

    class Meta:
        model = Price
        fields = ('product',)

    def validate(self, validate_data):
        if self.instance.is_expired(self.instance):
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)

        product_data = validate_data.get('product', {})

        if self.instance.price_list_type == 0:
            item_obj = Product.objects.filter(id=product_data.get('id')).first()
        else:
            item_obj = Expense.objects.filter(id=product_data.get('id')).first()

        if not item_obj:
            raise serializers.ValidationError({'product_obj': ProductMsg.PRODUCT_DOES_NOT_EXIST})
        validate_data['item_obj'] = item_obj

        uom_obj = UnitOfMeasure.objects.filter(id=product_data.get('uom')).first()
        if not uom_obj:
            raise serializers.ValidationError({'uom_obj': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
        validate_data['uom_obj'] = uom_obj

        return validate_data

    def update(self, instance, validated_data):
        children = Price.get_children(instance)
        bulk_info = []
        for child_obj, _ in children:
            if instance.price_list_type == 0:
                obj = self.add_product_to_price_list(child_obj, instance, validated_data)
                if not obj:
                    raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                bulk_info.append(obj)
            else:
                obj = self.add_expense_to_price_list(child_obj, instance, validated_data)
                if not obj:
                    raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                bulk_info.append(obj)

        if instance.price_list_type == 0:
            ProductPriceList.objects.bulk_create(bulk_info)
        else:
            ExpensePrice.objects.bulk_create(bulk_info)
        return instance

    @classmethod
    def add_product_to_price_list(cls, child_obj, price_list_obj, validated_data):
        item_obj = validated_data['item_obj']
        uom_obj = validated_data['uom_obj']
        if ProductPriceList.objects.filter(price_list=child_obj, product=item_obj, uom_using=uom_obj).exists():
            return None
        obj = ProductPriceList(
            price_list=child_obj,
            product=item_obj,
            price=0,
            currency_using_id=price_list_obj.currency[0],
            uom_using=uom_obj,
            uom_group_using=uom_obj.group,
            get_price_from_source=child_obj.auto_update
        )
        return obj

    @classmethod
    def add_expense_to_price_list(cls, child_obj, price_list_obj, validated_data):
        item_obj = validated_data['item_obj']
        uom_obj = validated_data['uom_obj']
        if ExpensePrice.objects.filter(price=child_obj, expense=item_obj, uom=uom_obj).exists():
            return None
        obj = ExpensePrice(
            price=child_obj,
            expense=item_obj,
            price_value=0,
            currency_id=price_list_obj.currency[0],
            uom=uom_obj,
            is_auto_update=child_obj.auto_update,
        )
        return obj


class PriceListItemCreateSerializerImportDB(serializers.ModelSerializer):
    product = serializers.DictField(required=True)

    class Meta:
        model = Price
        fields = ('product',)

    @classmethod
    def add_product_to_price_list(cls, child_obj, factor, product_obj, uom_obj, currency_obj, price_number):
        if ProductPriceList.objects.filter(
                price_list=child_obj, product=product_obj, uom_using=uom_obj, currency_using=currency_obj
        ).exists():
            return None
        obj = ProductPriceList(
            price_list=child_obj,
            product=product_obj,
            price=round(float(price_number) * round(factor, 2), 2),
            currency_using=currency_obj,
            uom_using=uom_obj,
            uom_group_using=uom_obj.group,
            get_price_from_source=False
        )
        return obj

    @classmethod
    def add_expense_to_price_list(cls, child_obj, factor, expense_obj, uom_obj, currency_obj, price_number):
        if ExpensePrice.objects.filter(
                price=child_obj, expense=expense_obj, uom=uom_obj, currency=currency_obj
        ).exists():
            return None
        obj = ExpensePrice(
            price=child_obj,
            expense=expense_obj,
            price_value=round(float(price_number) * round(factor, 2), 2),
            currency=currency_obj,
            uom=uom_obj,
            is_auto_update=False
        )
        return obj

    def validate(self, validate_data):
        company_current = self.context.get('company_current', None)
        tenant_current = self.context.get('tenant_current', None)
        product_data = validate_data.get('product', [])

        price_list_obj = Price.objects.filter(id=product_data['price_id']).first()
        if not price_list_obj:
            raise serializers.ValidationError({'price_list_obj': PriceMsg.PRICE_LIST_NOT_EXIST})
        if price_list_obj.is_expired(price_list_obj):
            raise serializers.ValidationError(PriceMsg.PRICE_LIST_EXPIRED)
        if price_list_obj.auto_update:
            raise serializers.ValidationError(PriceMsg.CANT_ADD_ITEM)
        validate_data['price_list_obj'] = price_list_obj

        if not isinstance(float(product_data.get('price')), (int, float)):
            validate_data['price'] = 0
        else:
            validate_data['price'] = float(product_data.get('price'))

        prd_obj = Product.objects.filter(
            code=product_data.get('code'), tenant=tenant_current, company=company_current
        ).first()
        if not prd_obj:
            raise serializers.ValidationError({'prd_obj': ProductMsg.PRODUCT_DOES_NOT_EXIST})
        validate_data['product_obj'] = prd_obj

        uom_obj = UnitOfMeasure.objects.filter(
            code=product_data.get('uom'), tenant=tenant_current, company=company_current
        ).first()
        if not uom_obj:
            raise serializers.ValidationError({'uom_obj': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
        validate_data['uom_obj'] = uom_obj

        currency_obj = Currency.objects.filter(
            abbreviation=product_data.get('currency', '').upper(), tenant=tenant_current, company=company_current
        ).first()
        if not currency_obj:
            raise serializers.ValidationError({'currency_obj': ProductMsg.CURRENCY_DOES_NOT_EXIST})
        validate_data['currency_obj'] = currency_obj

        if prd_obj.general_uom_group_id != uom_obj.group_id:
            raise serializers.ValidationError({'uom_group': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})

        return validate_data

    def create(self, validated_data):
        price_list_obj = validated_data['price_list_obj']
        price = validated_data['price']
        product_obj = validated_data['product_obj']
        uom_obj = validated_data['uom_obj']
        currency_obj = validated_data['currency_obj']

        child_price_list = Price.get_children(price_list_obj)
        bulk_info = []
        for child_obj, child_factor in child_price_list:
            if price_list_obj.price_list_type == 0:
                obj = self.add_product_to_price_list(child_obj, child_factor, product_obj, uom_obj, currency_obj, price)
                if not obj:
                    raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                bulk_info.append(obj)
            else:
                obj = self.add_expense_to_price_list(child_obj, child_factor, product_obj, uom_obj, currency_obj, price)
                if not obj:
                    raise serializers.ValidationError({"item": PriceMsg.ITEM_EXIST})
                bulk_info.append(obj)

        if len(bulk_info) > 0:
            if price_list_obj.price_list_type == 0:
                ProductPriceList.objects.bulk_create(bulk_info)
            else:
                ExpensePrice.objects.bulk_create(bulk_info)
        return price_list_obj


class PriceListItemDetailSerializerImportDB(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('id',)
