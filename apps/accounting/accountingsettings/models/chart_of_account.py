from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models.price import Currency
from apps.shared import MasterDataAbstractModel


__all__ = [
    'ChartOfAccounts',
    'ChartOfAccountsSummarize',
    'CHART_OF_ACCOUNT_TYPE'
]


CHART_OF_ACCOUNT_TYPE = [
    (0, _("Off-table accounts")),
    (1, _("Assets")),
    (2, _("Liabilities")),
    (3, _("Owner's equity")),
    (4, _("Revenue")),
    (5, _("Costs of production, business")),
    (6, _("Other incomes")),
    (7, _("Other expenses")),
    (8, _("Income summary")),
]


class ChartOfAccounts(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    acc_code = models.CharField(max_length=100)
    acc_name = models.CharField(max_length=100)
    foreign_acc_name = models.CharField(max_length=100)
    acc_status = models.BooleanField(default=True)
    acc_type = models.SmallIntegerField(choices=CHART_OF_ACCOUNT_TYPE)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    has_child = models.BooleanField(default=False)
    level = models.IntegerField(default=1)
    is_account = models.BooleanField(default=False)
    control_account = models.BooleanField(default=False)
    is_all_currency = models.BooleanField(default=True)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE, null=True)
    currency_mapped_data = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    is_added = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Chart Of Accounts'
        verbose_name_plural = 'Chart Of Accounts'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_acc(cls, company_id, code):
        return cls.objects.filter(company_id=company_id, acc_code=code).first()

    @classmethod
    def add_account(cls, company, parent_acc_type, parent_acc_code, new_acc_code, new_acc_name, new_foreign_acc_name):
        # get parent account
        parent_account_obj = ChartOfAccounts.objects.filter(
            acc_type=parent_acc_type, acc_code=parent_acc_code, company=company
        ).first()
        existed_account = ChartOfAccounts.objects.filter(
            acc_type=parent_acc_type, acc_code=new_acc_code, company=company
        ).exists()
        if parent_account_obj and not existed_account:
            primary_currency_obj = Currency.objects.filter_on_company(is_primary=True).first()
            ChartOfAccounts.objects.filter(
                order__gt=parent_account_obj.order, company=company
            ).update(order=F('order') + 1)
            ChartOfAccounts.objects.create(
                order=parent_account_obj.order + 1,
                parent_account=parent_account_obj,
                acc_code=new_acc_code,
                acc_name=new_acc_name,
                foreign_acc_name=new_foreign_acc_name,
                acc_type=parent_account_obj.acc_type,
                company=company,
                tenant=company.tenant,
                level=parent_account_obj.level + 1,
                is_account=True,
                currency_mapped=primary_currency_obj,
                currency_mapped_data={
                    'id': str(primary_currency_obj.id),
                    'abbreviation': primary_currency_obj.abbreviation,
                    'title': primary_currency_obj.title,
                    'rate': primary_currency_obj.rate
                } if primary_currency_obj else {},
                is_default=False,
                is_added=True
            )
            print(f'Added account {new_acc_code}')
        else:
            print('Can not found parent account || existed account')
        return True


class ChartOfAccountsSummarize(MasterDataAbstractModel):
    account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        null=True,
        related_name='summarize_account'
    )
    # đầu kì
    opening_debit = models.FloatField(default=0)
    opening_credit = models.FloatField(default=0)
    # trong kì
    total_debit = models.FloatField(default=0)
    total_credit = models.FloatField(default=0)
    # cuối kì
    closing_debit = models.FloatField(default=0)
    closing_credit = models.FloatField(default=0)

    class Meta:
        verbose_name = 'ChartOfAccountsSummarize'
        verbose_name_plural = 'ChartOfAccountsSummarize'

    @classmethod
    def update_summarize(cls, je_obj):
        je_line_list = je_obj.je_lines.all()
        for line in je_line_list:
            chart_of_accounts_summarize_obj = cls.objects.filter_on_company(account_id=line.account_id).first()
            if not chart_of_accounts_summarize_obj:
                chart_of_accounts_summarize_obj = cls.objects.create(
                    account=line.account,
                    tenant=je_obj.tenant,
                    company=je_obj.company,
                )
            chart_of_accounts_summarize_obj.total_debit += line.debit
            chart_of_accounts_summarize_obj.total_credit += line.credit
            chart_of_accounts_summarize_obj.closing_debit = (
                    chart_of_accounts_summarize_obj.opening_debit + chart_of_accounts_summarize_obj.total_debit
            )
            chart_of_accounts_summarize_obj.closing_credit = (
                    chart_of_accounts_summarize_obj.opening_credit + chart_of_accounts_summarize_obj.total_credit
            )
            chart_of_accounts_summarize_obj.save(
                update_fields=['total_debit', 'total_credit', 'closing_debit', 'closing_credit']
            )
            if chart_of_accounts_summarize_obj:
                chart_of_accounts_summarize_obj.total_debit += line.debit
                chart_of_accounts_summarize_obj.total_credit += line.credit
                chart_of_accounts_summarize_obj.closing_debit = (
                        chart_of_accounts_summarize_obj.opening_debit + chart_of_accounts_summarize_obj.total_debit
                )
                chart_of_accounts_summarize_obj.closing_credit = (
                        chart_of_accounts_summarize_obj.opening_credit + chart_of_accounts_summarize_obj.total_credit
                )
                chart_of_accounts_summarize_obj.save(update_fields=['total_debit', 'total_credit', 'closing_debit', 'closing_credit'])
        return True
