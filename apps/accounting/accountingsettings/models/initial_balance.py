from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import SimpleAbstractModel, DataAbstractModel


__all__ = [
    'InitialBalance',
    'InitialBalanceLine',
    'InitialBalanceGoodsLot',
    'InitialBalanceGoodsSerial',
]


INITIAL_BALANCE_TYPE = [
    (0, _('Money')),
    (1, _('Goods')),
    (2, _('Customer receivable')),
    (3, _('Supplier payable')),
    (4, _('Employee payable')),
    (5, _('Fixed assets')),
    (6, _('Expenses')),
    (7, _('Owner equity')),
]


class InitialBalance(DataAbstractModel):
    description = models.TextField(blank=True, null=True)
    period_mapped = models.ForeignKey(
        'saledata.Periods', on_delete=models.CASCADE, related_name='ib_period_mapped'
    )
    period_mapped_data = models.JSONField(default=dict)
    tab_account_balance_data = models.JSONField(default=list)
    # tab_account_balance_data = [{'tab_name': '', 'tab_value': 0, 'currency_data': {}}, ...]

    class Meta:
        verbose_name = 'Initial Balance'
        verbose_name_plural = 'Initial Balances'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class InitialBalanceLine(DataAbstractModel):
    initial_balance = models.ForeignKey(
        InitialBalance,
        on_delete=models.CASCADE,
        related_name='ib_line_initial_balance'
    )
    initial_balance_type = models.SmallIntegerField(choices=INITIAL_BALANCE_TYPE)
    debit_value = models.FloatField(default=0)
    credit_value = models.FloatField(default=0)
    account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        null=True,
        related_name='ib_line_account'
    )
    account_data = models.JSONField(default=dict)
    is_fc = models.BooleanField(default=False)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.SET_NULL, null=True)
    currency_mapped_data = models.JSONField(default=dict)  # {id, title, abbreviation, rate}

    # for tab money
    money_type = models.SmallIntegerField(choices=[(0, _('Cash')), (1, _('Bank deposit'))], default=0)
    money_value = models.FloatField(default=0)
    money_value_exchange = models.FloatField(default=0)
    money_detail_data = models.JSONField(default=dict)

    # for tab goods
    goods_value = models.FloatField(default=0)
    goods_quantity = models.FloatField(default=0)
    goods_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    goods_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)
    goods_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    goods_data_lot = models.JSONField(default=list)
    goods_data_sn = models.JSONField(default=list)

    # for tab customer receivable
    customer_receivable_value = models.FloatField(default=0)
    customer_receivable_customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ib_line_customer_receivable_customer'
    )
    customer_receivable_customer_data = models.JSONField(default=dict)
    customer_receivable_detail_data = models.JSONField(default=dict)

    # for tab supplier payable
    supplier_payable_value = models.FloatField(default=0)
    supplier_payable_supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ib_line_supplier_payable_supplier'
    )
    supplier_payable_supplier_data = models.JSONField(default=dict)
    supplier_payable_detail_data = models.JSONField(default=dict)

    # for tab employee payable
    employee_payable_value = models.FloatField(default=0)
    employee_payable_type = models.SmallIntegerField(
        choices=[(0, _('Advance payment')), (1, _('Payment')), (2, _('Advance salary'))], default=0
    )
    employee_payable_employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ib_line_employee_payable_employee'
    )
    employee_payable_employee_data = models.JSONField(default=dict)
    employee_payable_detail_data = models.JSONField(default=dict)

    # for tab tools
    tools_value = models.FloatField(default=0)
    tools_detail_data = models.JSONField(default=dict)

    # for tab account
    account_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Initial Balance Line'
        verbose_name_plural = 'Initial Balance Lines'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class InitialBalanceGoodsLot(SimpleAbstractModel):
    """
    Ghi lại Lot khi nhập SDDK cho tab Hàng hóa
    """
    initial_balance_line = models.ForeignKey(InitialBalanceLine, on_delete=models.CASCADE)
    lot_mapped = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Initial Balance Goods Lot'
        verbose_name_plural = 'Initial Balance Goods Lots'
        ordering = ('lot_mapped__lot_number',)
        default_permissions = ()
        permissions = ()


class InitialBalanceGoodsSerial(SimpleAbstractModel):
    """
    Ghi lại Serial khi nhập SDDK cho tab Hàng hóa
    """
    initial_balance_line = models.ForeignKey(InitialBalanceLine, on_delete=models.CASCADE)
    serial_mapped = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE)
    specific_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Initial Balance Goods Serial'
        verbose_name_plural = 'Initial Balance Goods Serials'
        ordering = ('serial_mapped__serial_number',)
        default_permissions = ()
        permissions = ()
