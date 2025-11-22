import itertools
from django.db import models
from django.utils.translation import gettext_lazy as _
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
    transaction_key = models.CharField(max_length=10, db_index=True)
    foreign_title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    account_determination_type = models.SmallIntegerField(choices=ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False, help_text='True if user can change')

    class Meta:
        verbose_name = 'Account Determination'
        verbose_name_plural = 'Account Determination'
        ordering = ('order', 'transaction_key')
        unique_together = ('company', 'transaction_key')


class AccountDeterminationSub(SimpleAbstractModel):
    account_determination = models.ForeignKey(
        AccountDetermination,
        on_delete=models.CASCADE,
        related_name='sub_items'
    )
    transaction_key_sub = models.CharField(max_length=10, blank=True, default='')
    description = models.TextField(blank=True, null=True)

    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='determination_mappings'
    )
    account_mapped_data = models.JSONField(default=dict, blank=True)

    match_criteria = models.JSONField(default=dict, blank=True)
    search_rule = models.CharField(max_length=512, db_index=True)
    priority = models.IntegerField(default=0, db_index=True)

    def save(self, *args, **kwargs):
        criteria = self.match_criteria
        if not isinstance(criteria, dict):
            criteria = {}
        self.match_criteria = criteria

        self.priority = len(criteria)
        self.search_rule = self.generate_key_from_dict(criteria)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key_from_dict(criteria_dict):
        """
        Tạo search_rule chuẩn hóa từ dict
        Input: {'b': 2, 'a': 1} -> Output: "a:1|b:2"
        """
        if not criteria_dict:
            return "default"
        sorted_keys = sorted(criteria_dict.keys())
        parts = [f"{k}:{str(criteria_dict[k])}" for k in sorted_keys]
        return "|".join(parts)

    @classmethod
    def generate_candidate_keys(cls, context_dict):
        """
        Sinh ra danh sách các key cần tìm kiếm
        Input: {'wh': 1, 'prd_type': 2}
        Output: ['prd_type:2|wh:1', 'prd_type:2', 'wh:1', 'default']
        """
        if not context_dict:
            return ["default"]
        keys = sorted(context_dict.keys())
        candidates = []
        # Sinh tổ hợp từ dài xuống ngắn (để tìm rule cụ thể trước)
        for r in range(len(keys), 0, -1):
            for combination in itertools.combinations(keys, r):
                subset_dict = {k: context_dict[k] for k in combination}
                key_string = cls.generate_key_from_dict(subset_dict)
                candidates.append(key_string)
        candidates.append("default")
        return candidates

    @classmethod
    def get_gl_account(cls, company_id, transaction_key, context_dict, modifier=''):
        """
        Hàm tìm tài khoản tối ưu nhất
        """
        candidate_keys = cls.generate_candidate_keys(context_dict)
        best_rule = cls.objects.filter(
            account_determination__company_id=company_id,
            account_determination__transaction_key=transaction_key,
            transaction_key_sub=modifier,
            search_rule__in=candidate_keys
        ).order_by('-priority').first()
        return best_rule.account_mapped if best_rule else None

    class Meta:
        verbose_name = 'Account Determination Sub'
        verbose_name_plural = 'Account Determination Sub'
        ordering = ('-priority',)
        unique_together = ('account_determination', 'transaction_key_sub', 'search_rule')
