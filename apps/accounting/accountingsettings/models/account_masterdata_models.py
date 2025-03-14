from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from apps.core.company.models import Company
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'ChartOfAccounts',
    'DefaultAccountDetermination'
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

DEFAULT_ACCOUNT_DETERMINATION_TYPE = [
    (0, _('Sale')),
    (1, _('Purchasing')),
    (2, _('Inventory')),
    (3, _('Fixed, Assets')),
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
    is_default = models.BooleanField(default=False)
    is_added = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Chart Of Accounts'
        verbose_name_plural = 'Chart Of Accounts'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def add_account(cls, parent_acc_type, parent_acc_code, new_acc_code, new_acc_name, new_foreign_acc_name):
        for company in Company.objects.all():
            print(f'Add for {company.title}')
            # get parent account
            parent_account_obj = ChartOfAccounts.objects.filter(
                acc_type=parent_acc_type, acc_code=parent_acc_code, company=company
            ).first()
            existed_account = ChartOfAccounts.objects.filter(
                acc_type=parent_acc_type, acc_code=new_acc_code, company=company
            ).exists()
            if parent_account_obj and not existed_account:
                ChartOfAccounts.objects.filter(order__gt=parent_account_obj.order).update(order=F('order') + 1)
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
                    is_default=False,
                    is_added=True
                )
                print('Done :))')
            else:
                print('Can not found parent account || existed account')


class DefaultAccountDetermination(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    foreign_title = models.CharField(max_length=100, blank=True)
    default_account_determination_type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False)
    is_changed = models.BooleanField(default=False, help_text='True if user has change default account determination')

    @classmethod
    def get_default_account_deter_sub_data(cls, tenant_id, company_id, foreign_title):
        account_deter = DefaultAccountDetermination.objects.filter(
            tenant_id=tenant_id,
            company_id=company_id,
            foreign_title=foreign_title
        ).first()
        if account_deter:
            return account_deter.default_acc_deter_sub.all()
        return []

    class Meta:
        verbose_name = 'Default Account Determination'
        verbose_name_plural = 'Default Account Determination'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class DefaultAccountDeterminationSub(SimpleAbstractModel):
    default_acc_deter = models.ForeignKey(
        DefaultAccountDetermination,
        on_delete=models.CASCADE,
        related_name='default_acc_deter_sub'
    )
    account_mapped = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.CASCADE,
        related_name='default_acc_deter_account_mapped'
    )
    account_mapped_data = models.JSONField(default=dict)
    # {'id', 'acc_code', 'acc_name', 'foreign_acc_name'}

    class Meta:
        verbose_name = 'Default Account Determination Sub'
        verbose_name_plural = 'Default Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
