from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.masterdata.saledata.models import (
    Periods, Currency, Product, WareHouse
)
from apps.accounting.accountingsettings.models.initial_balance import (
    InitialBalance, InitialBalanceLine
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
        )


class InitialBalanceCreateSerializer(serializers.ModelSerializer):

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
    tab_fixed_assets_data = serializers.SerializerMethodField()
    tab_expenses_data = serializers.SerializerMethodField()
    tab_owner_equity_data = serializers.SerializerMethodField()

    class Meta:
        model = InitialBalance
        fields = (
            'id',
            'code',
            'title',
            'description',
            'period_mapped_data',
            # tab detail
            'tab_money_data',
            'tab_goods_data',
            'tab_customer_receivable_data',
            'tab_supplier_payable_data',
            'tab_employee_payable_data',
            'tab_fixed_assets_data',
            'tab_expenses_data',
            'tab_owner_equity_data',
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
            'account_data': item.account_data,
            'is_fc': item.is_fc,
            'currency_mapped_data': item.currency_mapped_data,
        } if item else {}

    def get_tab_money_data(self, obj):
        return [{
            # added fields
            # ...
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
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 2)]

    def get_tab_supplier_payable_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 3)]

    def get_tab_employee_payable_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 4)]

    def get_tab_fixed_assets_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 5)]

    def get_tab_expenses_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 6)]

    def get_tab_owner_equity_data(self, obj):
        return [{
            # added fields
            # ...
            # common fields
            **self.parse_common_fields(item)
        } for item in self.filter_lines_by_type(obj, 7)]


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
    tab_fixed_assets_data = serializers.JSONField(default=list)
    tab_expenses_data = serializers.JSONField(default=list)
    tab_owner_equity_data = serializers.JSONField(default=list)

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
            'tab_fixed_assets_data',
            'tab_expenses_data',
            'tab_owner_equity_data',
        )

    @staticmethod
    def validate_common_fields(tab_data):
        for item in tab_data:
            debit_value = item.get('debit_value', 0)
            credit_value = item.get('credit_value', 0)
            account_obj = ChartOfAccounts.objects.filter_on_company(id=item.get('account')).first()
            currency_mapped_obj = Currency.objects.filter_on_company(id=item.get('currency_mapped')).first()
            primary_currency_obj = Currency.objects.filter_on_company(is_primary=True).first()
            if debit_value < 0 or credit_value < 0:
                raise serializers.ValidationError({'primary_currency': _('Debit/Credit value can not smaller than 0.')})
            if not account_obj:
                raise serializers.ValidationError({'account': _('Account is required.')})
            if not primary_currency_obj:
                raise serializers.ValidationError({'primary_currency': _('Primary currency does not exist')})
            if not currency_mapped_obj:
                currency_mapped_obj = primary_currency_obj

            tab_data['debit_value'] = debit_value
            tab_data['credit_value'] = credit_value

            tab_data['account'] = account_obj
            tab_data['account_data'] = {
                'id': str(account_obj.id),
                'acc_code': account_obj.acc_code,
                'acc_name': account_obj.acc_name,
                'foreign_acc_name': account_obj.foreign_acc_name
            }

            tab_data['is_fc'] = str(primary_currency_obj.id) != str(currency_mapped_obj.id)
            tab_data['currency_mapped'] = currency_mapped_obj
            tab_data['currency_mapped_data'] = {
                'id': str(currency_mapped_obj.id),
                'abbreviation': currency_mapped_obj.abbreviation,
                'title': currency_mapped_obj.title,
                'rate': currency_mapped_obj.rate
            }
        return tab_data

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

    def validate_tab_fixed_assets_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_fixed_assets_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_expenses_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_expenses_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate_tab_owner_equity_data(self, tab_data):
        tab_data = self.validate_common_fields(tab_data)
        # validate more
        tab_data = InitialBalanceCommonFunction.validate_more_tab_owner_equity_data(
            tab_data, self.instance.period_mapped, self.context
        )
        return tab_data

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        # pop tab_data ra
        tabs_data = {
            'tab_money_data': validated_data.pop('tab_money_data'),
            'tab_goods_data': validated_data.pop('tab_goods_data'),
            'tab_customer_receivable_data': validated_data.pop('tab_customer_receivable_data'),
            'tab_supplier_payable_data': validated_data.pop('tab_supplier_payable_data'),
            'tab_employee_payable_data': validated_data.pop('tab_employee_payable_data'),
            'tab_fixed_assets_data': validated_data.pop('tab_fixed_assets_data'),
            'tab_expenses_data': validated_data.pop('tab_expenses_data'),
            'tab_owner_equity_data': validated_data.pop('tab_owner_equity_data'),
        }

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update tab data
        for tab_name, tab_data in tabs_data.items():
            if len(tab_data) > 0:  # Chỉ update nếu có data
                InitialBalanceCommonFunction.common_update_tab(tab_name, tab_data)

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
        return tab_data

    @staticmethod
    def validate_more_tab_goods_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})

            sub_period_obj = period_mapped_obj.sub_periods_period_mapped.filter(order=1).first()
            if not sub_period_obj:
                raise serializers.ValidationError({"this_sub_period": 'This sub period is not found.'})

            prd_obj = InitialBalanceCommonFunction.get_product_from_detail_data(detail_data, tenant_obj, company_obj)
            if not prd_obj:
                raise serializers.ValidationError({'prd_obj': 'Product is not found.'})

            if not prd_obj.inventory_uom:
                raise serializers.ValidationError({'inventory_uom': 'Inventory UOM is not found.'})

            wh_obj = InitialBalanceCommonFunction.get_warehouse_from_detail_data(detail_data, tenant_obj, company_obj)
            if not wh_obj:
                raise serializers.ValidationError({'wh_obj': 'Warehouse is not found.'})

            if InitialBalanceLine.objects.filter(product=prd_obj, warehouse=wh_obj).exists():
                raise serializers.ValidationError(
                    {"Existed": f"{prd_obj.title}'s initial balance has been created in {wh_obj.title}."}
                )

            if prd_obj.is_used_in_inventory_activities(warehouse_obj=wh_obj):
                raise serializers.ValidationError(
                    {"Has trans": f'{prd_obj.title} transactions are existed in {wh_obj.title}.'}
                )

            item['product'] = prd_obj
            item['uom'] = prd_obj.inventory_uom
            item['warehouse'] = wh_obj
            item['period_obj'] = period_mapped_obj
            item['sub_period_obj'] = sub_period_obj
            item['quantity'] = float(item.get('quantity', 0))
            item['value'] = float(item.get('value', 0))
            item['data_lot'] = item.get('data_lot', [])
            item['data_sn'] = item.get('data_sn', [])

        return tab_data

    @staticmethod
    def validate_more_tab_customer_receivable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_supplier_payable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_employee_payable_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_fixed_assets_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_expenses_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    @staticmethod
    def validate_more_tab_owner_equity_data(tab_data, period_mapped_obj, context):
        tenant_obj = context.get('tenant_current')
        company_obj = context.get('company_current')
        if not tenant_obj or not company_obj or not period_mapped_obj:
            raise serializers.ValidationError({"error": "Tenant or Company or Period is missing."})

        for item in tab_data:
            detail_data = item.pop('detail_data', {})
            # logic here
        return tab_data

    # for update
    @classmethod
    def common_update_tab(cls, tab_name, tab_data):
        to_create = []
        to_update = []
        for item in tab_data:
            item_id = item.pop('id', None)
            if item_id:
                to_update.append((item_id, item))
            else:
                to_create.append(InitialBalanceLine(**item))

        with transaction.atomic():
            created_instances = []
            if to_create:
                created_instances = InitialBalanceLine.objects.bulk_create(to_create)
            for item_id, data in to_update:
                InitialBalanceLine.objects.filter(id=item_id).update(**data)
        print(f"Updated tab '{tab_name}': created {len(created_instances)}, updated {len(to_update)}")

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
            'tab_expenses_data': cls.handle_expenses_tab,
            'tab_owner_equity_data': cls.handle_owner_equity_tab,
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
        pass

    @staticmethod
    def handle_goods_tab(created_instances, updated_items):
        """Xử lý tab goods"""
        pass

    @staticmethod
    def handle_customer_receivable_tab(created_instances, updated_items):
        """Xử lý tab customer receivable"""
        pass

    @staticmethod
    def handle_supplier_payable_tab(created_instances, updated_items):
        """Xử lý tab supplier payable"""
        pass

    @staticmethod
    def handle_employee_payable_tab(created_instances, updated_items):
        """Xử lý tab employee payable"""
        pass

    @staticmethod
    def handle_fixed_assets_tab(created_instances, updated_items):
        """Xử lý tab fixed assets"""
        pass

    @staticmethod
    def handle_expenses_tab(created_instances, updated_items):
        """Xử lý tab expenses"""
        pass

    @staticmethod
    def handle_owner_equity_tab(created_instances, updated_items):
        """Xử lý tab owner equity"""
        pass

    # tab goods common function
    @staticmethod
    def get_product_from_detail_data(detail_data, tenant_current, company_current):
        if 'product_id' not in detail_data and 'product_code' not in detail_data:
            raise serializers.ValidationError({"error": "Balance data is missing product information."})

        prd_obj = None
        if 'product_id' in detail_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, id=detail_data.get('product_id')
            ).first()
        if 'product_code' in detail_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, code=detail_data.get('product_code')
            ).first()
        return prd_obj

    @staticmethod
    def get_warehouse_from_detail_data(detail_data, tenant_current, company_current):
        if 'warehouse_id' not in detail_data and 'warehouse_code' not in detail_data:
            raise serializers.ValidationError({"error": "Balance data is missing warehouse information."})

        wh_obj = None
        if 'warehouse_id' in detail_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, id=detail_data.get('warehouse_id')
            ).first()
        if 'warehouse_code' in detail_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, code=detail_data.get('warehouse_code')
            ).first()
        return wh_obj
