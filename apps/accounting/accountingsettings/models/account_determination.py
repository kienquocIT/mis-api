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

# 1. Bên Nợ/Có
SIDE_CHOICES = [
    ('DEBIT', _('Bên nợ')),
    ('CREDIT', _('Bên có')),
]

# 2. Nguồn tiền
AMOUNT_SOURCE_CHOICES = (
    ('TOTAL', _('Tổng thanh toán')),
    ('COST', _('Giá vốn (Cost)')),
    ('SALES', _('Doanh thu (Sales)')),
    ('TAX', _('Tiền thuế (Tax)')),
    ('DISCOUNT', _('Chiết khấu')),
)

# 3. Loại nguồn Tài khoản
ACCOUNT_SOURCE_TYPE_CHOICES = (
    ('FIXED', _('Cố định (Chọn cứng TK)')),
    ('DYNAMIC', _('Động (Theo Role/Nhóm)')),
)


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
        ordering = ('account_determination_type', 'transaction_key')
        unique_together = ('company', 'transaction_key')


class AccountDeterminationSub(SimpleAbstractModel):
    ALLOWED_DETERMINATION_KEYS = {
        'warehouse_id',
        'product_type_id',
        'product_id',
    }

    account_determination = models.ForeignKey(AccountDetermination, on_delete=models.CASCADE, related_name='sub_items')
    # Thứ tự hiển thị (1, 2, 3...)
    order = models.IntegerField(default=0, db_index=True)
    # Bên Nợ hay Có
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    # Lấy tiền từ đâu
    amount_source = models.CharField(max_length=20, choices=AMOUNT_SOURCE_CHOICES)
    # Chọn tài khoản từ đâu (cứng hay động)
    account_source_type = models.CharField(max_length=10, choices=ACCOUNT_SOURCE_TYPE_CHOICES)
    # CASE A: Cứng
    fixed_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='determination_fixed_account',
    )
    # CASE B: Động
    role_key = models.CharField(max_length=50, blank=True, null=True)
    # --- LOGIC TÌM KIẾM & NGOẠI LỆ  ---
    match_context = models.JSONField(default=dict, blank=True)
    search_rule = models.CharField(max_length=500, blank=True, null=True, default='default', db_index=True)
    priority = models.IntegerField(default=0, db_index=True)
    is_custom = models.BooleanField(default=False, editable=False)
    # Field bổ sung
    description = models.TextField(blank=True, null=True)
    example = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Account Determination Sub'
        verbose_name_plural = 'Account Determination Subs'
        ordering = ('order', '-priority')
        unique_together = ('account_determination', 'search_rule', 'order', 'side')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @classmethod
    def get_posting_lines(cls, company_id, transaction_key):
        """ Lấy danh sách quy tắc hạch toán theo mã giao dịch """
        posting_lines = cls.objects.filter(
            account_determination__company_id=company_id,
            account_determination__transaction_key=transaction_key
        ).select_related('fixed_account').order_by('order')
        return posting_lines

    @classmethod
    def get_amount_base_on_amount_source(cls, rule, **kwargs):
        """ Helper lấy amount dựa vào amount source """
        return kwargs.get(rule.amount_source, 0)

    @classmethod
    def get_account_mapped(cls, rule):
        """
        Tìm tài khoản dựa trên Rule (Fixed/Dynamic).
        Đây là cầu nối giữa Config và Product thực tế.
        """
        # CASE 1: FIXED
        if rule.account_source_type == 'FIXED':
            return rule.fixed_account
        # CASE 2: DYNAMIC
        # ...
        return None
