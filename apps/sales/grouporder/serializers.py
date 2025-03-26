import logging

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import (
    ProductPriceList,
    Account,
    Tax,
    UnitOfMeasure,
    ExpenseItem,
)
from apps.masterdata.saledata.models.product import Product
from apps.sales.grouporder.models import (
    GroupOrder,
    GroupOrderCustomer,
    GroupOrderCost,
    GroupOrderCustomerSelectedPriceList,
    GroupOrderExpense,
)

logger = logging.getLogger(__name__)


class GroupOrderProductListSerializer(serializers.ModelSerializer):
    bom_product = serializers.SerializerMethodField()
    general_price = serializers.SerializerMethodField()
    product_price_list_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'standard_price',
            'bom_product',
            'general_price',
            'product_price_list_data'
        )

    @classmethod
    def get_bom_product(cls, obj):
        return {
            'id': obj.bom_data.id,
            'title': obj.bom_data.title,
            'sum_price': obj.bom_data.sum_price,
        } if obj.bom_data else {}

    @classmethod
    def get_general_price(cls, obj):
        general_product_price_obj = obj.product_price_product.filter(price_list__is_default=True).first()
        return {
            'id': general_product_price_obj.id,
            'price': general_product_price_obj.price,
        } if general_product_price_obj else {}

    @classmethod
    def get_product_price_list_data(cls, obj):
        product_price_list = obj.product_price_product.all()
        sale_product_price_list = []
        for item in product_price_list:
            if item.uom_using_id == obj.sale_default_uom_id and item.price_list.valid_time_end > timezone.now():
                sale_product_price_list.append({
                    'id': item.id,
                    'price': item.price,
                    'title': _(item.price_list.title),
                    'is_default': item.price_list.is_default,
                })
        return sale_product_price_list


class GroupOrderProductPriceListListSerializer(serializers.ModelSerializer):
    price_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductPriceList
        fields = (
            'id',
            'price',
            'price_data'
        )

    @classmethod
    def get_price_data(cls, obj):
        return {
            'id': obj.price_list.id,
            'title': _(obj.price_list.title)
        } if obj.price_list else {}


class GroupOrderCustomerSerializer(serializers.ModelSerializer):
    customer_id = serializers.UUIDField(required=False, allow_null=True)
    price_list_select = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = GroupOrderCustomer
        fields = (
            'customer_id',
            'customer_code',
            'customer_name',
            'email',
            'phone',
            'register_code',
            'service_name',
            'quantity',
            'unit_price',
            'sub_total',
            'payment_status',
            'note',
            'order',
            'price_list_select',
            'register_date',
            'is_individual'
        )

    @classmethod
    def validate_customer_id(cls, value):
        if value:
            try:
                return Account.objects.get(id=value).id
            except Account.DoesNotExist:
                raise serializers.ValidationError({"account": _('Account does not exist')})
        raise serializers.ValidationError({"account": _('Account is required')})

    @classmethod
    def validate_price_list_select(cls, value):
        for item in value:
            product_price_list_uuid = item.pop('product_price_list')
            try:
                product_price_list = ProductPriceList.objects.get(id=product_price_list_uuid)
                item['product_price_list'] = product_price_list.id
            except ProductPriceList.DoesNotExist:
                raise serializers.ValidationError({"price_list_select": _("Product Price List does not exist")})
        return value


class GroupOrderCostSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GroupOrderCost
        fields = (
            'product',
            'quantity',
            'guest_quantity',
            'is_using_guest_quantity',
            'unit_cost',
            'sub_total',
            'order',
            'note'
        )

    @classmethod
    def validate_product(cls, value):
        if value:
            try:
                return Product.objects.get(id=value)
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": _('Product does not exist')})
        raise serializers.ValidationError({"product": _('Product is required')})


class GroupOrderExpenseSerializer(serializers.ModelSerializer):
    expense = serializers.UUIDField(required=False, allow_null=True)
    expense_uom = serializers.UUIDField(required=False, allow_null=True)
    expense_tax = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GroupOrderExpense
        fields = (
            'expense',
            'expense_name',
            'expense_uom',
            'quantity',
            'cost',
            'expense_tax',
            'sub_total',
            'order'
        )

    @classmethod
    def validate_expense(cls, value):
        if value:
            try:
                return ExpenseItem.objects.get(id=value)
            except ExpenseItem.DoesNotExist:
                raise serializers.ValidationError({"expense": _('Expense does not exist')})
        raise serializers.ValidationError({"expense": _('Expense is required')})

    @classmethod
    def validate_expense_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({"expense_uom": _('UnitOfMeasure does not exist')})
        raise serializers.ValidationError({"expense_uom": _('UnitOfMeasure is required')})

    @classmethod
    def validate_expense_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({"expense_tax": _('Tax does not exist')})
        raise serializers.ValidationError({"expense_tax": _('Tax is required')})


class GroupOrderCreateSerializer(serializers.ModelSerializer):
    customer_detail_list = GroupOrderCustomerSerializer(many=True)
    cost_list = GroupOrderCostSerializer(many=True)
    expense_list = GroupOrderExpenseSerializer(many=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    tax = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GroupOrder
        fields = (
            'employee_inherit_id',
            'title',
            'order_number',
            'service_start_date',
            'service_end_date',
            'service_created_date',
            'max_guest',
            'registered_guest',
            'order_status',
            'payment_term',
            'cost_per_guest',
            'cost_per_registered_guest',
            'planned_revenue',
            'actual_revenue',
            'total_amount',
            'tax',
            'total_amount_including_VAT',
            'total_general_price',
            'total_cost',
            'customer_detail_list',
            'data_selected_price_list',
            'cost_list',
            'data_product_list',
            'expense_list'
        )

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({"tax": _('Tax does not exist')})
        raise serializers.ValidationError({"tax": _('Tax is required')})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if value:
            try:
                return Employee.objects.get(id=value).id
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"employee_inherit_id": _('Employee does not exist')})
        raise serializers.ValidationError({"employee_inherit_id": _('Employee is required')})

    def create(self, validated_data):# pylint: disable=R0914
        customer_detail_list = validated_data.pop('customer_detail_list',[])
        cost_list = validated_data.pop('cost_list', [])
        expense_list = validated_data.pop('expense_list', [])

        try:
            with transaction.atomic():
                instance = GroupOrder.objects.create(**validated_data)

                for customer in customer_detail_list:
                    selected_price_list = customer.pop('price_list_select', [])
                    selected_price_list_bulk_data = []
                    group_order_customer = GroupOrderCustomer.objects.create(
                        group_order=instance,
                        customer_id=customer.get('customer_id', None),
                        customer_code=customer.get('customer_code', None),
                        customer_name=customer.get('customer_name', None),
                        email=customer.get('email', None),
                        phone=customer.get('phone', None),
                        register_code=customer.get('register_code', None),
                        service_name=customer.get('service_name', None),
                        register_date=customer.get('register_date', None),
                        quantity=customer.get('quantity'),
                        payment_status=customer.get('payment_status'),
                        unit_price=customer.get('unit_price', None),
                        sub_total=customer.get('sub_total', None),
                        order=customer.get('order', None),
                        note=customer.get('note', None),
                        is_individual=customer.get('is_individual', None),
                        tenant=instance.tenant,
                        company=instance.company,
                        employee_created= instance.employee_created,
                    )
                    for price_list in selected_price_list:
                        selected_price_list_bulk_data.append(
                            GroupOrderCustomerSelectedPriceList(
                                group_order_customer = group_order_customer,
                                product_price_list_id = price_list.get('product_price_list', None),
                                value = price_list.get('value', 0)
                            )
                        )
                    if len(selected_price_list_bulk_data) > 0:
                        GroupOrderCustomerSelectedPriceList.objects.bulk_create(selected_price_list_bulk_data)

                cost_list_bulk_data = []
                for cost in cost_list:
                    cost_list_bulk_data.append(
                        GroupOrderCost(
                            group_order = instance,
                            product = cost.get('product', None),
                            quantity = cost.get('quantity', None),
                            guest_quantity = cost.get('guest_quantity', None),
                            is_using_guest_quantity = cost.get('is_using_guest_quantity', None),
                            unit_cost = cost.get('unit_cost', None),
                            sub_total = cost.get('sub_total', None),
                            order = cost.get('order', None),
                            note = cost.get('note', None),
                            tenant=instance.tenant,
                            company=instance.company,
                            employee_created=instance.employee_created,
                        )
                    )
                if len(cost_list_bulk_data) > 0:
                    GroupOrderCost.objects.bulk_create(cost_list_bulk_data)

                expense_list_bulk_data = []
                for expense in expense_list:
                    expense_list_bulk_data.append(
                        GroupOrderExpense(
                            group_order = instance,
                            expense = expense.get('expense', None),
                            expense_name = expense.get('expense_name', None),
                            expense_uom = expense.get('expense_uom', None),
                            quantity = expense.get('quantity', None),
                            cost = expense.get('cost', None),
                            expense_tax = expense.get('expense_tax', None),
                            sub_total = expense.get('sub_total', None),
                            order = expense.get('order', None),
                            tenant=instance.tenant,
                            company=instance.company,
                            employee_created=instance.employee_created,
                        )
                    )
                if len(expense_list_bulk_data) > 0:
                    GroupOrderExpense.objects.bulk_create(expense_list_bulk_data)

        except Exception as err:
            logger.error(msg=f'Create group order errors: {str(err)}')
            raise serializers.ValidationError({'group_order': _('Error create group order')})
        return instance


class GroupOrderListSerializer(serializers.ModelSerializer):
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = GroupOrder
        fields = (
            'title',
            'id',
            'code',
            'service_start_date',
            'service_end_date',
            'order_status',
            'order_number'
        )

    @classmethod
    def get_order_status(cls, obj):
        return obj.get_order_status_display()


class GroupOrderDetailSerializer(serializers.ModelSerializer):
    payment_term = serializers.SerializerMethodField()
    customer_detail_list = serializers.SerializerMethodField()
    cost_list = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    expense_list = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()

    class Meta:
        model = GroupOrder
        fields = (
            'title',
            'order_number',
            'id',
            'employee_inherit',
            'service_start_date',
            'service_end_date',
            'service_created_date',
            'max_guest',
            'registered_guest',
            'order_status',
            'payment_term',
            'cost_per_guest',
            'cost_per_registered_guest',
            'planned_revenue',
            'actual_revenue',
            'total_amount',
            'tax',
            'total_amount_including_VAT',
            'total_general_price',
            'total_cost',
            'customer_detail_list',
            'data_selected_price_list',
            'cost_list',
            'data_product_list',
            'expense_list'
        )

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
        } if obj.tax else None

    @classmethod
    def get_payment_term(cls, obj):
        return {
            'id': obj.payment_term_id,
            'title': obj.payment_term.title,
        } if obj.payment_term else {}

    @classmethod
    def get_customer_detail_list(cls, obj):
        group_order_customer_list = obj.group_order_group_order_customers.all()
        data = []
        for group_order_customer in group_order_customer_list:
            data.append({
                'id': group_order_customer.id,
                'customer_id': group_order_customer.customer_id,
                'customer_code': group_order_customer.customer_code,
                'customer_name': group_order_customer.customer_name,
                'email': group_order_customer.email,
                'phone': group_order_customer.phone,
                'register_code': group_order_customer.register_code,
                'service_name': group_order_customer.service_name,
                'quantity': group_order_customer.quantity,
                # 'tax': {
                #     'id': group_order_customer.tax_id,
                #     'title': group_order_customer.tax.title,
                # },
                'unit_price': group_order_customer.unit_price,
                'sub_total': group_order_customer.sub_total,
                'payment_status': group_order_customer.payment_status,
                'note': group_order_customer.note,
                'register_date': group_order_customer.register_date,
                'is_individual': group_order_customer.is_individual,
            })
        return data

    @classmethod
    def get_cost_list(cls, obj):
        group_order_cost_list = obj.group_order_costs.all()
        data = []
        for group_order_cost in group_order_cost_list:
            data.append({
                'id': group_order_cost.product.id,
                'quantity': group_order_cost.quantity,
                'guest_quantity': group_order_cost.guest_quantity,
                'is_using_guest_quantity': group_order_cost.is_using_guest_quantity,
                'note': group_order_cost.note,
                'unit_cost': group_order_cost.unit_cost,
                'sub_total': group_order_cost.sub_total,
                'title': group_order_cost.product.title,
                'code': group_order_cost.product.code,
            })
        return data

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(),
        }


    @classmethod
    def get_expense_list(cls, obj):
        group_order_expense_list = obj.group_order_expenses.all()
        data = []
        for group_order_expense in group_order_expense_list:
            data.append({
                'id': group_order_expense.id,
                'expense': {
                    'id': group_order_expense.expense_id,
                    'title': group_order_expense.expense.title,
                } if group_order_expense.expense else None,
                'expense_name': group_order_expense.expense_name,
                'expense_uom': {
                    'id': group_order_expense.expense_uom_id,
                    'title': group_order_expense.expense_uom.title,
                } if group_order_expense.expense_uom else None,
                'expense_tax': {
                    'id': group_order_expense.expense_tax_id,
                    'title': group_order_expense.expense_tax.title,
                } if group_order_expense.expense_tax else None,
                'quantity': group_order_expense.quantity,
                'cost': group_order_expense.cost,
                'sub_total': group_order_expense.sub_total,
            })
        return data


class GroupOrderUpdateSerializer(serializers.ModelSerializer):
    customer_detail_list = GroupOrderCustomerSerializer(many=True)
    cost_list = GroupOrderCostSerializer(many=True)
    expense_list = GroupOrderExpenseSerializer(many=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    tax = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GroupOrder
        fields = (
            'employee_inherit_id',
            'title',
            'order_number',
            'service_start_date',
            'service_end_date',
            'service_created_date',
            'max_guest',
            'registered_guest',
            'order_status',
            'payment_term',
            'cost_per_guest',
            'cost_per_registered_guest',
            'planned_revenue',
            'actual_revenue',
            'total_amount',
            'tax',
            'total_amount_including_VAT',
            'total_general_price',
            'total_cost',
            'customer_detail_list',
            'data_selected_price_list',
            'cost_list',
            'data_product_list',
            'expense_list'
        )

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({"tax": _('Tax does not exist')})
        raise serializers.ValidationError({"tax": _('Tax is required')})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if value:
            try:
                return Employee.objects.get(id=value).id
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"employee_inherit_id": _('Employee does not exist')})
        raise serializers.ValidationError({"employee_inherit_id": _('Employee is required')})

    def update(self, instance, validated_data):# pylint: disable=R0914
        customer_detail_list = validated_data.pop('customer_detail_list', [])
        cost_list = validated_data.pop('cost_list', [])
        expense_list = validated_data.pop('expense_list', [])

        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()
                instance.group_order_group_order_customers.all().delete()
                instance.group_order_costs.all().delete()
                instance.group_order_expenses.all().delete()

                for customer in customer_detail_list:
                    selected_price_list = customer.pop('price_list_select', [])
                    selected_price_list_bulk_data = []
                    group_order_customer = GroupOrderCustomer.objects.create(
                        group_order=instance,
                        customer_id=customer.get('customer_id', None),
                        customer_code=customer.get('customer_code', None),
                        customer_name=customer.get('customer_name', None),
                        email=customer.get('email', None),
                        phone=customer.get('phone', None),
                        register_code=customer.get('register_code', None),
                        service_name=customer.get('service_name', None),
                        register_date=customer.get('register_date', None),
                        quantity=customer.get('quantity'),
                        payment_status=customer.get('payment_status'),
                        unit_price=customer.get('unit_price', None),
                        sub_total=customer.get('sub_total', None),
                        order=customer.get('order', None),
                        note=customer.get('note', None),
                        is_individual=customer.get('is_individual', None),
                        tenant=instance.tenant,
                        company=instance.company,
                        employee_created=instance.employee_created,
                    )
                    for price_list in selected_price_list:
                        selected_price_list_bulk_data.append(
                            GroupOrderCustomerSelectedPriceList(
                                group_order_customer = group_order_customer,
                                product_price_list_id = price_list.get('product_price_list', None),
                                value = price_list.get('value', 0)
                            )
                        )
                    if len(selected_price_list_bulk_data) > 0:
                        GroupOrderCustomerSelectedPriceList.objects.bulk_create(selected_price_list_bulk_data)

                cost_list_bulk_data = []
                for cost in cost_list:
                    cost_list_bulk_data.append(
                        GroupOrderCost(
                            group_order = instance,
                            product = cost.get('product', None),
                            quantity = cost.get('quantity', None),
                            guest_quantity = cost.get('guest_quantity', None),
                            is_using_guest_quantity = cost.get('is_using_guest_quantity', None),
                            unit_cost = cost.get('unit_cost', None),
                            sub_total = cost.get('sub_total', None),
                            order = cost.get('order', None),
                            note=cost.get('note', None),
                            tenant=instance.tenant,
                            company=instance.company,
                            employee_created=instance.employee_created,
                        )
                    )
                if len(cost_list_bulk_data) > 0:
                    GroupOrderCost.objects.bulk_create(cost_list_bulk_data)

                expense_list_bulk_data = []
                for expense in expense_list:
                    expense_list_bulk_data.append(
                        GroupOrderExpense(
                            group_order=instance,
                            expense=expense.get('expense', None),
                            expense_name=expense.get('expense_name', None),
                            expense_uom=expense.get('expense_uom', None),
                            quantity=expense.get('quantity', None),
                            cost=expense.get('cost', None),
                            expense_tax=expense.get('expense_tax', None),
                            sub_total=expense.get('sub_total', None),
                            order=expense.get('order', None),
                            tenant=instance.tenant,
                            company=instance.company,
                            employee_created=instance.employee_created,
                        )
                    )
                if len(expense_list_bulk_data) > 0:
                    GroupOrderExpense.objects.bulk_create(expense_list_bulk_data)
        except Exception as err:
            logger.error(msg=f'Update group order errors: {str(err)}')
            raise serializers.ValidationError({'group_order': _('Error update group order')})
        return instance
