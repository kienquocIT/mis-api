from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'JEDocumentType',
    'JEPostingRule',
    'JEPostingGroup',
    'JEGLAccountMapping',
    'JEGroupAssignment',
    'JEDocData',
    'JE_DOCUMENT_TYPE_APP',
    'DOCUMENT_TYPE_CHOICES',
    'SIDE_CHOICES',
    'RULE_LEVEL_CHOICES',
    'AMOUNT_SOURCE_CHOICES',
    'ROLE_KEY_CHOICES',
    'ACCOUNT_SOURCE_TYPE_CHOICES',
    'GROUP_TYPE_CHOICES',
    'ASSIGNMENT_APP_CHOICES',
]

JE_DOCUMENT_TYPE_APP = [
    ('delivery.orderdeliverysub', _('Delivery')),
    ('inventory.goodsreceipt', _('Goods Receipt')),
    ('arinvoice.arinvoice', _('AR Invoice')),
    ('apinvoice.apinvoice', _('AP Invoice')),
    ('financialcashflow.cashinflow', _('Cash Inflow')),
    ('financialcashflow.cashoutflow', _('Cash Outflow')),
]

DOCUMENT_TYPE_CHOICES = [
    (0, _('Sale')),
    (1, _('Purchasing')),
    (2, _('Inventory')),
    (3, _('Fixed Assets')),
]

SIDE_CHOICES = [
    ('DEBIT', _('Bên nợ')),
    ('CREDIT', _('Bên có')),
]

RULE_LEVEL_CHOICES = [
    ('HEADER', _('Cả phiếu')),
    ('LINE', _('Từng dòng')),
]

AMOUNT_SOURCE_CHOICES = [
    ('TOTAL', _('Tổng thanh toán')),
    ('COST', _('Giá vốn')),
    ('SALES', _('Giá bán')),
    ('TAX', _('Tiền thuế')),
    ('DISCOUNT', _('Chiết khấu')),
    ('CASH', _('Số tiền mặt')),
    ('BANK', _('Số tiền ngân hàng'))
]

ROLE_KEY_CHOICES = [
    # Nhóm Tài sản/Kho
    ('ASSET', _('Tài sản/Kho (156, 152...)')),
    ('COGS', _('Giá vốn hàng bán (632)')),
    # Nhóm Doanh thu
    ('REVENUE', _('Doanh thu (511)')),
    ('DONI', _('Doanh thu tạm tính/Chưa hóa đơn (1388)')),  # Delivery Order Not Invoiced
    # Nhóm Công nợ Mua
    ('PAYABLE', _('Phải trả người bán (331)')),
    ('GRNI', _('Hàng về chưa hóa đơn (3388)')),  # Goods Received Not Invoiced
    # Nhóm Công nợ Bán
    ('RECEIVABLE', _('Phải thu khách hàng (131)')),
    # Nhóm Thuế
    ('TAX_IN', _('Thuế đầu vào (133)')),
    ('TAX_OUT', _('Thuế đầu ra (333)')),
    # Nhóm Tiền
    ('CASH', _('Tiền mặt (111)')),
    ('BANK', _('Tiền gửi ngân hàng (112)')),
]

ACCOUNT_SOURCE_TYPE_CHOICES = [
    ('FIXED', _('Cố định (Chọn cứng TK)')),
    ('LOOKUP', _('Động (Theo Role/Nhóm)')),
    ('CONDITIONAL', _('Theo điều kiện')),
]

GROUP_TYPE_CHOICES = [
    ('ITEM_GROUP', _('Item group')),
    ('PARTNER_GROUP', _('Partner group')),
]

ASSIGNMENT_APP_CHOICES = [
    # ITEM_GROUP
    ('saledata.producttype', _('Product Type')),
    ('saledata.product', _('Product')),
    # PARTNER_GROUP
    ('saledata.accounttype', _('Account Type')),
    ('saledata.account', _('Account')),
]


class JEDocumentType(MasterDataAbstractModel):
    module = models.SmallIntegerField(choices=DOCUMENT_TYPE_CHOICES)
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    is_auto_je = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'JE Document Type'
        verbose_name_plural = 'JE Document Types'
        ordering = ('-module', '-app_code')
        unique_together = ('company', 'module', 'code')

    @classmethod
    def check_app_state(cls, app_code):
        """ Kiểm tra trạng thái cấu hình """
        if not app_code:
            return False
        config = cls.objects.filter_on_company(app_code=app_code).first()
        return config.is_auto_je if config else False


class JEPostingGroup(MasterDataAbstractModel):
    """Bảng quản lý chung tất cả các nhóm định khoản. Phân loại bằng field 'type'"""

    posting_group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES)

    class Meta:
        verbose_name = 'JE Posting Group'
        verbose_name_plural = 'JE Posting Groups'
        ordering = ('posting_group_type', 'code')
        unique_together = ('company', 'posting_group_type', 'code')


class JEGroupAssignment(MasterDataAbstractModel):
    """Bảng duy nhất quản lý việc: Đối tượng nào thuộc Nhóm định khoản nào"""

    item_app = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    item_id = models.UUIDField()
    item_app_data = models.JSONField(default=dict)
    posting_group = models.ForeignKey(JEPostingGroup, on_delete=models.CASCADE, related_name='assignment_posting_group')

    class Meta:
        verbose_name = 'GL Group Assignment'
        verbose_name_plural = 'GL Group Assignments'
        ordering = ('posting_group__posting_group_type', 'posting_group__code', 'item_app')
        unique_together = ('company', 'item_app', 'item_id')


class JEGLAccountMapping(MasterDataAbstractModel):
    """Bảng tra cứu: posting_group + role_key => Tài khoản"""

    # Input 1: Posting group
    posting_group = models.ForeignKey(
        JEPostingGroup, on_delete=models.CASCADE, related_name='gl_mappings'
    )

    # Input 2: Role Key
    role_key = models.CharField(max_length=50)

    # Output: Account
    account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='gl_account_mapping_account',
    )

    class Meta:
        verbose_name = 'JE GL Account Mapping'
        verbose_name_plural = 'JE GL Accounts Mapping'
        ordering = ('posting_group__code', 'role_key')
        unique_together = ('company', 'posting_group', 'role_key')


class JEPostingRule(MasterDataAbstractModel):
    je_document_type = models.ForeignKey(JEDocumentType, on_delete=models.CASCADE, related_name='je_posting_rules')
    # Ghi cho tổng phiếu (HEADER) hay từng dòng trong phiếu (LINE)
    rule_level = models.CharField(max_length=10, choices=RULE_LEVEL_CHOICES)
    # Ưu tiên
    priority = models.IntegerField()
    # Role là gì
    role_key = models.CharField(max_length=50, blank=True, null=True, choices=ROLE_KEY_CHOICES)
    # Bên Nợ hay Có
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    # Lấy tiền từ nguồn nào (field trong model)
    amount_source = models.CharField(max_length=100)
    # Chọn tài khoản từ đâu (cứng hay động)
    account_source_type = models.CharField(max_length=20, choices=ACCOUNT_SOURCE_TYPE_CHOICES)
    # CASE A: Cứng
    fixed_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='je_posting_rule_fixed_account',
    )
    # Field bổ sung
    description = models.TextField(blank=True, null=True)
    example = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'JE Posting Rule'
        verbose_name_plural = 'JE Posting Rules'
        ordering = ('je_document_type__code', 'rule_level', 'priority')


class JEDocData(SimpleAbstractModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}',
        choices=JE_DOCUMENT_TYPE_APP
    )
    doc_id = models.UUIDField(verbose_name='Document ID')
    # Ghi cho tổng phiếu (HEADER) hay từng dòng trong phiếu (LINE)
    rule_level = models.CharField(max_length=10, choices=RULE_LEVEL_CHOICES)
    amount_source = models.CharField(max_length=20)
    value = models.FloatField(default=0)
    taxable_value = models.FloatField(default=0)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE, null=True)
    currency_mapped_data = models.JSONField(default=dict)
    context_data = models.JSONField(default=dict)
    # context_data = {
    #     'tracking_app': {app_label}.{model},
    #     'tracking_id': UUID,
    # }

    class Meta:
        verbose_name = 'JE Doc Data'
        verbose_name_plural = 'JE Docs Data'
        ordering = ()

    @classmethod
    def get_amount_source_doc_data(cls, doc_id):
        return cls.objects.filter(doc_id=doc_id)

    @classmethod
    def make_doc_data_obj(
            cls, company_id, app_code, doc_id, rule_level, amount_source, value, taxable_value, currency_mapped,
            context_data=None
    ):
        return cls(
            company_id=str(company_id),
            app_code=app_code,
            doc_id=str(doc_id),
            rule_level=rule_level,
            amount_source=amount_source,
            value=value,
            taxable_value=taxable_value,
            currency_mapped=currency_mapped,
            currency_mapped_data={
                "id": str(currency_mapped.id),
                "abbreviation": currency_mapped.abbreviation,
                "title": currency_mapped.title,
                "rate": currency_mapped.rate
            },
            context_data=context_data or {}
        )
