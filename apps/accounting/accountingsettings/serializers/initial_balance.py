from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.masterdata.saledata.models import (
    Periods, Currency
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

    @classmethod
    def validate_tab_money_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_goods_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_customer_receivable_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_supplier_payable_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_employee_payable_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_fixed_assets_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_expenses_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data

    @classmethod
    def validate_tab_owner_equity_data(cls, tab_data):
        tab_data = cls.validate_common_fields(tab_data)
        # validate more
        # ...
        return tab_data
