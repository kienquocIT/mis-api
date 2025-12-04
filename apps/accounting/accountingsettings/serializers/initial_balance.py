from django.db import transaction
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.masterdata.saledata.models import (
    Periods, Currency, Product, WareHouse, Account,
)
from apps.core.hr.models import Employee
from apps.accounting.accountingsettings.models.initial_balance import (
    InitialBalance, InitialBalanceLine, INITIAL_BALANCE_TYPE
)


class InitialBalanceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = InitialBalance
        fields = (
            'id',
            'code',
            'title',
            'date_created',
            'period_mapped_data',
            'tab_account_balance_data'
        )


class InitialBalanceCreateSerializer(serializers.ModelSerializer):
    period_mapped = serializers.UUIDField()

    class Meta:
        model = InitialBalance
        fields = (
            'period_mapped',
        )

    @classmethod
    def validate_period_mapped(cls, value):
        try:
            period_obj = Periods.objects.get(id=value)
            if period_obj.ib_period_mapped.exists():
                raise serializers.ValidationError({"error": "This Period is already initialized."})
            return period_obj
        except Periods.DoesNotExist:
            raise serializers.ValidationError({'period': 'Periods obj does not exist.'})

    def validate(self, validate_data):
        period_obj = validate_data.get('period_mapped')
        validate_data['period_mapped_data'] = {
            'id': str(period_obj.id),
            'code': period_obj.code,
            'title': period_obj.title,
            'fiscal_year': str(period_obj.fiscal_year),
            'start_date': str(period_obj.start_date),
        }
        validate_data['code'] = f"IB-{period_obj.code}"
        validate_data['title'] = f"Initial balance for {period_obj.code} - {period_obj.fiscal_year}"
        primary_currency_obj = Currency.objects.filter_on_company(is_primary=True).first()
        validate_data['tab_account_balance_data'] = [{
            'tab_type': item[0],
            'tab_name': force_str(item[1]),
            'tab_value': 0,
            'currency_data': {
                'id': str(primary_currency_obj.id),
                'abbreviation': primary_currency_obj.abbreviation,
                'title': primary_currency_obj.title,
                'rate': primary_currency_obj.rate
            } if primary_currency_obj else {}
        } for item in INITIAL_BALANCE_TYPE]
        return validate_data

    def create(self, validated_data):
        ib_obj = InitialBalance.objects.create(**validated_data)
        return ib_obj


class InitialBalanceDetailSerializer(serializers.ModelSerializer):
    all_initial_balance_lines = None
    # tab data
    tab_money_data = serializers.SerializerMethodField()
    tab_goods_data = serializers.SerializerMethodField()
    tab_customer_receivable_data = serializers.SerializerMethodField()
    tab_supplier_payable_data = serializers.SerializerMethodField()
    tab_employee_payable_data = serializers.SerializerMethodField()
    tab_tools_data = serializers.SerializerMethodField()
    tab_fixed_assets_data = serializers.SerializerMethodField()
    tab_accounts_data = serializers.SerializerMethodField()

    class Meta:
        model = InitialBalance
        fields = (
            'id',
            'code',
            'title',
            'description',
            'tab_account_balance_data',
            'period_mapped_data',
            # tab detail
            'tab_money_data',
            'tab_goods_data',
            'tab_customer_receivable_data',
            'tab_supplier_payable_data',
            'tab_employee_payable_data',
            'tab_tools_data',
            'tab_fixed_assets_data',
            'tab_accounts_data',
        )

    def get_all_initial_balance_lines(self, obj):
        if self.all_initial_balance_lines is None:
            self.all_initial_balance_lines = obj.ib_line_initial_balance.all()
        return self.all_initial_balance_lines

    def filter_lines_by_type(self, obj, initial_balance_type):
        all_lines = self.get_all_initial_balance_lines(obj)
        return all_lines.filter(initial_balance_type=initial_balance_type)

    @staticmethod
    def parse_common_fields(item):
        return {
            'id': str(item.id),
            'debit_value': item.debit_value,
            'credit_value': item.credit_value,
            'tab_amount': item.tab_amount,
            'account_data': item.account_data,
            'is_fc': item.is_fc,
            'currency_mapped_data': item.currency_mapped_data,
        } if item else {}

    def get_tab_money_data(self, obj):
        return [{
            # added fields
            "money_type": item.money_type,
            "money_value": item.money_value,
            "money_value_exchange": item.money_value_exchange,
            "money_detail_data": item.money_detail_data,
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 0)]

    def get_tab_goods_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 1)]

    def get_tab_customer_receivable_data(self, obj):
        return [{
            # added fields
            "customer_receivable_value": item.customer_receivable_value,
            # "customer_receivable_customer": item.customer_receivable_value,
            "customer_receivable_customer_data": item.customer_receivable_customer_data,
            "customer_receivable_detail_data": item.customer_receivable_detail_data,
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 2)]

    def get_tab_supplier_payable_data(self, obj):
        return [{
            # added fields
            "supplier_payable_value": item.supplier_payable_value,
            # "supplier_payable_supplier": item.supplier_payable_supplier.id,
            "supplier_payable_supplier_data": item.supplier_payable_supplier_data,
            "supplier_payable_detail_data": item.supplier_payable_detail_data,
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 3)]

    def get_tab_employee_payable_data(self, obj):
        return [{
            # added fields
            "employee_payable_value": item.employee_payable_value,
            "employee_payable_type": item.employee_payable_type,
            "employee_payable_employee_data": item.employee_payable_employee_data,
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 4)]

    def get_tab_tools_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 5)]

    def get_tab_fixed_assets_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 6)]

    def get_tab_accounts_data(self, obj):
        return [{**self.parse_common_fields(item)} for item in self.filter_lines_by_type(obj, 7)]


class InitialBalanceUpdateSerializer(serializers.ModelSerializer):
    """
    Hoàn thiện các hàm sau validate_more_tab_<...>_data() ---> handle_<...>_tab()
    """
    title = serializers.CharField(max_length=100)
    # tab data
    tab_money_data = serializers.JSONField(default=list)
    tab_goods_data = serializers.JSONField(default=list)
    tab_customer_receivable_data = serializers.JSONField(default=list)
    tab_supplier_payable_data = serializers.JSONField(default=list)
    tab_employee_payable_data = serializers.JSONField(default=list)
    tab_tools_data = serializers.JSONField(default=list)
    tab_fixed_assets_data = serializers.JSONField(default=list)
    tab_accounts_data = serializers.JSONField(default=list)

    class Meta:
        model = InitialBalance
        fields = (
            'title',
            'description',
            # tab detail
            'tab_money_data',
            'tab_goods_data',
            'tab_customer_receivable_data',
            'tab_supplier_payable_data',
            'tab_employee_payable_data',
            'tab_tools_data',
            'tab_fixed_assets_data',
            'tab_accounts_data',
        )

    @staticmethod
    def validate_common_fields(tab_data):
        parsed_tab_data = []
        for item in tab_data:
            debit_value = item.get('debit_value', 0)
            credit_value = item.get('credit_value', 0)
            account_obj = ChartOfAccounts.objects.filter_on_company(id=item.get('account')).first()
            currency_mapped_obj = Currency.objects.filter_on_company(id=item.get('currency_mapped')).first()
            primary_currency_obj = Currency.objects.filter_on_company(is_primary=True).first()
            if debit_value < 0 or credit_value < 0:
                raise serializers.ValidationError({'value': _('Debit/Credit value cannot smaller than 0.')})
            if debit_value != 0 and credit_value != 0:
                raise serializers.ValidationError({'value': _('Debit/Credit value cannot both be greater than 0.')})
            if not account_obj:
                raise serializers.ValidationError({'account': _('Account is required.')})
            if not primary_currency_obj:
                raise serializers.ValidationError({'primary_currency': _('Primary currency does not exist')})
            if not currency_mapped_obj:
                currency_mapped_obj = primary_currency_obj

            parsed_tab_data.append({
                # id cho row update
                'id': item.get('id'),
                # các fields common
                'debit_value': debit_value,
                'credit_value': credit_value,
                'tab_amount': debit_value + credit_value,
                'account_id': str(account_obj.id),
                'account_data': {
                    'id': str(account_obj.id),
                    'acc_code': account_obj.acc_code,
                    'acc_name': account_obj.acc_name,
                    'foreign_acc_name': account_obj.foreign_acc_name
                },
                'is_fc': str(primary_currency_obj.id) != str(currency_mapped_obj.id),
                'currency_mapped_id': str(currency_mapped_obj.id),
                'currency_mapped_data': {
                    'id': str(currency_mapped_obj.id),
                    'abbreviation': currency_mapped_obj.abbreviation,
                    'title': currency_mapped_obj.title,
                    'rate': currency_mapped_obj.rate
                },
                # các fields theo tab sẽ đặt trong detail_data
                'detail_data': item.pop('detail_data', {})
            })
        return parsed_tab_data

    def validate_tab_money_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_money_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_goods_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_goods_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_customer_receivable_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_customer_receivable_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_supplier_payable_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_supplier_payable_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_employee_payable_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_employee_payable_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_tools_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_tools_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_fixed_assets_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_fixed_assets_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_accounts_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_accounts_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        tabs_data = {
            'tab_money_data': validated_data.pop('tab_money_data'),
            'tab_goods_data': validated_data.pop('tab_goods_data'),
            'tab_customer_receivable_data': validated_data.pop('tab_customer_receivable_data'),
            'tab_supplier_payable_data': validated_data.pop('tab_supplier_payable_data'),
            'tab_employee_payable_data': validated_data.pop('tab_employee_payable_data'),
            'tab_tools_data': validated_data.pop('tab_tools_data'),
            'tab_fixed_assets_data': validated_data.pop('tab_fixed_assets_data'),
            'tab_accounts_data': validated_data.pop('tab_accounts_data'),
        }

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update tab data
        for tab_type, (tab_name, tab_data) in enumerate(tabs_data.items()):
            if len(tab_data) > 0:  # Chỉ update nếu có data
                InitialBalanceCommonFunction.common_update_tab(instance, tab_type, tab_name, tab_data)

        return instance


class InitialBalanceCommonFunction:
    # validate more
    @staticmethod
    def validate_more_tab_money_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
            # money type must be in [0, 1]
            if int(detail_data.get('money_type')) not in [0, 1]:
                raise serializers.ValidationError({'money_type': _('Money type is not valid.')})
            # validate amount value must be larger than 0
            if detail_data.get('money_value') < 0:
                raise serializers.ValidationError({'money_value': _('Amount value cannot smaller than 0.')})
            if detail_data.get('money_value_exchange') < 0:
                raise serializers.ValidationError(
                    {'money_value_exchange': _('VND exchange value cannot smaller than 0.')}
                )
            item['money_type'] = detail_data.get('money_type')
            item['money_value'] = detail_data.get('money_value')
            item['money_value_exchange'] = detail_data.get('money_value_exchange')
            item['money_detail_data'] = detail_data.get('money_detail_data')
        return tab_data

    @staticmethod
    def validate_more_tab_goods_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})

            if 'goods_product' not in detail_data:
                raise serializers.ValidationError({"goods_product": "Missing product information."})
            if 'goods_warehouse' not in detail_data:
                raise serializers.ValidationError({"goods_warehouse": "Missing warehouse information."})

            goods_product = Product.objects.filter(id=detail_data.get('goods_product')).first()
            if not goods_product:
                raise serializers.ValidationError({'goods_product': 'Product is not found.'})

            if not goods_product.inventory_uom:
                raise serializers.ValidationError({'inventory_uom': 'Inventory UOM is not found.'})

            goods_warehouse = WareHouse.objects.filter(id=detail_data.get('goods_warehouse')).first()
            if not goods_warehouse:
                raise serializers.ValidationError({'goods_warehouse': 'Warehouse is not found.'})

            if InitialBalanceLine.objects.filter(product=goods_product, warehouse=goods_warehouse).exists():
                raise serializers.ValidationError(
                    {"err": f"{goods_product.title}'s initial balance has been created in {goods_warehouse.title}."}
                )

            if goods_product.is_used_in_inventory_activities(warehouse_obj=goods_warehouse):
                raise serializers.ValidationError(
                    {"err": f"{goods_product.title}'s transactions are existed in {goods_warehouse.title}."}
                )

            # Đây là các field theo từng tab
            item['goods_product'] = goods_product
            item['goods_uom'] = goods_product.inventory_uom
            item['goods_warehouse'] = goods_warehouse
            item['goods_quantity'] = float(item.get('goods_quantity', 0))
            item['goods_value'] = float(item.get('goods_value', 0))
            item['goods_data_lot'] = item.get('goods_data_lot', [])
            item['goods_data_sn'] = item.get('goods_data_sn', [])

        return tab_data

    @staticmethod
    def validate_more_tab_customer_receivable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            # logic here
            detail = item.pop('detail_data', {})
            detail_data = detail.get('customer_receivable_detail_data', {})
            customer_obj = Account.objects.filter(id=detail.get('customer_receivable_customer')).first()
            if not customer_obj:
                raise serializers.ValidationError({'customer_receivable_customer': _('Required customer.')})
            unpaid = detail_data.get('unpaid_amount', 0)
            advance = detail_data.get('advanced_payment', 0)
            if unpaid is not None and unpaid < 0:
                raise serializers.ValidationError({'unpaid_amount': _('Unpaid amount cannot be smaller than 0.')})
            if advance is not None and advance < 0:
                raise serializers.ValidationError({'advanced_payment': _('Advanced payment cannot be smaller than 0.')})
            is_prepay = detail_data.get('is_prepayment')
            if is_prepay:
                if not detail_data.get('note') or detail_data.get('advanced_payment') in (None, 0):
                    raise serializers.ValidationError({
                        'customer_receivable_detail': _('Required advance payment and explanation.')})
            else:
                required_fields = [('invoice_number', ''), ('unpaid_amount', 0), ('expected_payment_date', None),
                                   ('invoice_date', None)]
                for field, invalid_value in required_fields:
                    if detail_data.get(field) in (None, invalid_value):
                        raise serializers.ValidationError(
                            {'customer_receivable_detail': _(
                                'Required Invoice number, Unpaid amount, Expected payment date, and Invoice date.')}
                        )
            # fill data
            item['customer_receivable_value'] = item.get('debit_value', 0) + item.get('credit_value', 0)
            item['customer_receivable_customer'] = customer_obj
            item['customer_receivable_customer_data'] = {
                'id': str(customer_obj.id),
                'code': customer_obj.code,
                'name': customer_obj.name,
                'tax_code': customer_obj.tax_code
            } if customer_obj else {}
            item['customer_receivable_detail_data'] = detail_data
        return tab_data

    @staticmethod
    def validate_more_tab_supplier_payable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            # logic here
            detail = item.pop('detail_data', {})
            detail_data = detail.get('supplier_payable_detail_data', {})
            supplier_obj = Account.objects.filter(id=detail.get('supplier_payable_supplier')).first()
            if not supplier_obj:
                raise serializers.ValidationError({'supplier_payable_supplier': _('Required supplier.')})
            unpaid = detail_data.get('unpaid_amount', 0)
            advance = detail_data.get('advanced_payment', 0)
            if unpaid is not None and unpaid < 0:
                raise serializers.ValidationError({'unpaid_amount': _('Unpaid amount cannot be smaller than 0.')})
            if advance is not None and advance < 0:
                raise serializers.ValidationError({'advanced_payment': _('Advanced payment cannot be smaller than 0.')})
            is_prepay = detail_data.get('is_prepayment')
            if is_prepay:
                if not detail_data.get('note') or detail_data.get('advanced_payment') in (None, 0):
                    raise serializers.ValidationError({
                        'supplier_payable_detail': _('Required advance payment and explanation.')})
            else:
                required_fields = [('invoice_number', ''), ('unpaid_amount', 0), ('expected_payment_date', None),
                                   ('invoice_date', None)]
                for field, invalid_value in required_fields:
                    if detail_data.get(field) in (None, invalid_value):
                        raise serializers.ValidationError(
                            {'supplier_payable_detail': _(
                                'Required Invoice number, Unpaid amount, Expected payment date, and Invoice date.')}
                        )
            # fill data
            item['supplier_payable_value'] = item.get('debit_value', 0) + item.get('credit_value', 0)
            item['supplier_payable_supplier'] = supplier_obj
            item['supplier_payable_supplier_data'] = {
                'id': str(supplier_obj.id),
                'code': supplier_obj.code,
                'name': supplier_obj.name,
                'tax_code': supplier_obj.tax_code
            } if supplier_obj else {}
            item['supplier_payable_detail_data'] = detail_data
        return tab_data

    @staticmethod
    def validate_more_tab_employee_payable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            # logic here
            detail_data = item.pop('detail_data', {})
            employee_obj = Employee.objects.filter(id=detail_data.get('employee_payable_employee')).first()
            if not employee_obj:
                raise serializers.ValidationError({'employee_payable_employee': _('Required employee.')})
            if int(detail_data.get('employee_payable_type')) not in range(0, 3):
                raise serializers.ValidationError({'employee_payable_type': _('Employee payable type is not valid.')})
            if detail_data.get('employee_payable_value') < 0:
                raise serializers.ValidationError({'employee_payable_value': _('Amount value cannot smaller than 0.')})
            item['employee_payable_type'] = detail_data.get('employee_payable_type')
            item['employee_payable_value'] = detail_data.get('employee_payable_value')
            item['employee_payable_employee'] = employee_obj
            item['employee_payable_employee_data'] = {
                'id': str(employee_obj.id),
                'code': employee_obj.code,
                'name': employee_obj.first_name + " " + employee_obj.last_name,
            } if employee_obj else {}
        return tab_data

    @staticmethod
    def validate_more_tab_tools_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            print(detail_data)
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_fixed_assets_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            # logic here
            detail_data = item.pop('detail_data', {})
            print(detail_data)
        return tab_data

    @staticmethod
    def validate_more_tab_accounts_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})
        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            print(detail_data)
            item['account_value'] = item.get('debit_value', 0) + item.get('credit_value', 0)
        return tab_data

    # for update
    @classmethod
    def common_update_tab(cls, ib_obj, tab_type, tab_name, tab_data):
        to_create = []
        to_update = []
        for item in tab_data:
            item_id = item.pop('id', None)
            if item_id:
                to_update.append((item_id, item))
            else:
                to_create.append(InitialBalanceLine(initial_balance=ib_obj, initial_balance_type=tab_type, **item))

        with transaction.atomic():
            created_instances = []
            if to_create:
                created_instances = InitialBalanceLine.objects.bulk_create(to_create)
            for item_id, data in to_update:
                InitialBalanceLine.objects.filter(id=item_id).update(**data)
        print(f"Updated tab '{tab_name}': created {len(created_instances)}, updated {len(to_update)}")

        # Update lại giá trị tổng vô phiếu chính
        sum_tab = sum(
            line.tab_amount
            for line in ib_obj.ib_line_initial_balance.filter(initial_balance_type=tab_type)
        )
        for item in ib_obj.tab_account_balance_data:
            if item.get('tab_type') == tab_type:
                item['tab_value'] = sum_tab
                break
        ib_obj.save(update_fields=['tab_account_balance_data'])

        # Gọi hàm xử lý sau khi update tab
        cls.common_after_update_tab(tab_name, created_instances, to_update)
        return True

    @classmethod
    def common_after_update_tab(cls, tab_name, created_instances=None, updated_items=None):
        """Xử lý sau khi update tab"""
        handlers = {
            'tab_money_data': cls.handle_money_tab,
            'tab_goods_data': cls.handle_goods_tab,
            'tab_customer_receivable_data': cls.handle_customer_receivable_tab,
            'tab_supplier_payable_data': cls.handle_supplier_payable_tab,
            'tab_employee_payable_data': cls.handle_employee_payable_tab,
            'tab_fixed_assets_data': cls.handle_fixed_assets_tab,
            'tab_tools_data': cls.handle_tools_tab,
            'tab_accounts_data': cls.handle_accounts_tab,
        }
        handler = handlers.get(tab_name)
        if handler:
            handler(created_instances, updated_items)
            return True
        print(f'Invalid tab name: {tab_name}')
        return False

    # Handler methods
    @staticmethod
    def handle_money_tab(created_instances, updated_items):
        """Xử lý tab money"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_goods_tab(created_instances, updated_items):
        """Xử lý tab goods"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_customer_receivable_tab(created_instances, updated_items):
        """Xử lý tab customer receivable"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_supplier_payable_tab(created_instances, updated_items):
        """Xử lý tab supplier payable"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_employee_payable_tab(created_instances, updated_items):
        """Xử lý tab employee payable"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_fixed_assets_tab(created_instances, updated_items):
        """Xử lý tab fixed assets"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_tools_tab(created_instances, updated_items):
        """Xử lý tab expenses"""
        print(created_instances, updated_items)
        return True

    @staticmethod
    def handle_accounts_tab(created_instances, updated_items):
        """Xử lý tab owner equity"""
        print(created_instances, updated_items)
        return True
