import itertools
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounting.accountingsettings.models.chart_of_account import ChartOfAccounts
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'AccountDetermination',
    'AccountDeterminationSub'
]

ACCOUNT_DETERMINATION_TYPE = [
    (0, _('Sale')),
    (1, _('Purchasing')),
    (2, _('Inventory')),
    (3, _('Fixed Assets')),
]


class AccountDetermination(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    foreign_title = models.CharField(max_length=100, blank=True)
    transaction_key = models.CharField(max_length=25, db_index=True)
    description = models.TextField(blank=True, null=True)
    account_determination_type = models.SmallIntegerField(choices=ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False, help_text='True if user can change')

    @classmethod
    def get_sub_items_data(cls, tenant_id, company_id, foreign_title):
        account_deter = AccountDetermination.objects.filter(
            tenant_id=tenant_id, company_id=company_id, foreign_title=foreign_title
        ).first()
        return [item.account_mapped for item in account_deter.account_determination_sub.all()] if account_deter else []

    class Meta:
        verbose_name = 'Account Determination'
        verbose_name_plural = 'Account Determination'
        ordering = ('order', 'transaction_key')
        unique_together = ('company', 'transaction_key')


class AccountDeterminationSub(SimpleAbstractModel):
    # DANH SÁCH CÁC FIELD THAM GIA ĐỊNH KHOẢN
    ALLOWED_DETERMINATION_KEYS = {
        'warehouse_id',
        'product_type_id',
        'product_id',
    }

    account_determination = models.ForeignKey(
        AccountDetermination, on_delete=models.CASCADE, related_name='sub_items'
    )
    transaction_key_sub = models.CharField(max_length=25, blank=True, default='')
    description = models.TextField(blank=True, null=True)

    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts', on_delete=models.CASCADE, related_name='determination_mappings'
    )
    account_mapped_data = models.JSONField(default=dict, blank=True)
    example = models.TextField(blank=True, null=True)

    match_context = models.JSONField(default=dict, blank=True)
    search_rule = models.CharField(max_length=500, blank=True, null=True, default='default', db_index=True)
    priority = models.IntegerField(default=0, db_index=True)
    is_custom = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = 'Account Determination Sub'
        verbose_name_plural = 'Account Determination Sub'
        ordering = ('-priority', 'account_mapped__acc_code')
        unique_together = ('account_determination', 'transaction_key_sub', 'search_rule')

    def save(self, *args, **kwargs):
        context_dict = self.match_context
        if not isinstance(context_dict, dict):
            context_dict = {}
        valid_context_dict = {
            k: v for k, v in context_dict.items()
            if k in self.ALLOWED_DETERMINATION_KEYS and v is not None
        }
        self.match_context = valid_context_dict
        self.priority = len(valid_context_dict)
        self.search_rule = self.generate_search_rule(valid_context_dict)
        self.is_custom = bool(valid_context_dict)
        super().save(*args, **kwargs)

    @classmethod
    def create_specific_rule(
            cls, company_id, transaction_key, account_code, context_dict,
            transaction_key_sub='', description_sub='', example_sub=''
    ):
        try:
            acc_deter_obj = AccountDetermination.objects.get(company_id=company_id, transaction_key=transaction_key)
            acc_obj = ChartOfAccounts.get_acc(company_id, account_code)
            if not acc_obj:
                return False
            search_key = cls.generate_search_rule(context_dict)
            AccountDeterminationSub.objects.update_or_create(
                account_determination=acc_deter_obj,
                transaction_key_sub=transaction_key_sub,
                search_rule=search_key,
                defaults={
                    'description': description_sub,
                    'example': example_sub,
                    'account_mapped_id': str(acc_obj.id),
                    'account_mapped_data': {
                        'id': str(acc_obj.id),
                        'acc_code': acc_obj.acc_code,
                        'acc_name': acc_obj.acc_name,
                        'foreign_acc_name': acc_obj.foreign_acc_name,
                    },
                    'match_context': context_dict
                    # priority và is_custom sẽ tự động tính trong hàm save()
                }
            )
            return True
        except Exception as err:
            print(f"Error: {err}")
            return False

    @classmethod
    def delete_specific_rule(cls, company_id, transaction_key, context_dict):
        key = AccountDeterminationSub.generate_search_rule(context_dict)
        AccountDeterminationSub.objects.filter(
            account_determination__company_id=company_id,
            account_determination__transaction_key=transaction_key,
            search_rule=key
        ).delete()
        return True

    @classmethod
    def generate_search_rule(cls, context_dict):
        """ context_dict = {
            'warehouse_id': xxx,
            'product_type_id': yyy
        } --->  'product_type_id:xxx|warehouse_id:yyy' """
        if not context_dict:
            return "default"
        valid_context_dict = {
            k: v for k, v in context_dict.items()
            if k in cls.ALLOWED_DETERMINATION_KEYS and v is not None
        }
        if not valid_context_dict:
            return "default"
        sorted_keys = sorted(valid_context_dict.keys())
        parts = [f"{k}:{str(valid_context_dict[k])}" for k in sorted_keys]
        return "|".join(parts)

    @classmethod
    def generate_search_rule_list(cls, context_dict):
        """
            context_dict = {
                'warehouse_id': xxx,
                'product_type_id': yyy
            } ---> [
                'product_type_id:xxx|warehouse_id:yyy',  <-- Ưu tiên 1: Khớp cả 2 (Cụ thể nhất)
                'product_type_id:xxx',                  <-- Ưu tiên 2: Chỉ khớp loại SP (Áp dụng mọi kho)
                'warehouse_id:yyy',                    <-- Ưu tiên 2: Chỉ khớp kho (Áp dụng mọi SP)
                'default'                            <-- Ưu tiên 3: Mặc định (Không khớp gì cả)
            ]
        """
        if not context_dict:
            return ["default"]
        clean_context = {
            k: v for k, v in context_dict.items()
            if k in cls.ALLOWED_DETERMINATION_KEYS and v is not None
        }
        keys = sorted(clean_context.keys())
        candidates = []
        for subset_size in range(len(keys), 0, -1):
            for combination in itertools.combinations(keys, subset_size):
                subset_dict = {k: clean_context[k] for k in combination}
                key_string = cls.generate_search_rule(subset_dict)
                candidates.append(key_string)
        candidates.append("default")
        return candidates

    @classmethod
    def get_best_rule(cls, company_id, transaction_key, context_dict, transaction_key_sub=''):
        """ Hàm tìm tài khoản tối ưu nhất """
        search_rule_list = cls.generate_search_rule_list(context_dict)
        best_rule_obj = cls.objects.filter(
            account_determination__company_id=company_id,
            account_determination__transaction_key=transaction_key,
            transaction_key_sub=transaction_key_sub,
            search_rule__in=search_rule_list
        ).select_related('account_mapped').order_by('-priority').first()
        return best_rule_obj
