import logging
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import Periods, Currency
from apps.shared import DataAbstractModel, SimpleAbstractModel, AutoDocumentAbstractModel, MasterDataAbstractModel


logger = logging.getLogger(__name__)


JE_ALLOWED_APP = {
    'delivery.orderdeliverysub': _('Delivery'),
    'inventory.goodsreceipt': _('Goods Receipt'),
    'arinvoice.arinvoice': _('AR Invoice'),
    'apinvoice.apinvoice': _('AP Invoice'),
    'financialcashflow.cashinflow': _('Cash Inflow'),
    'financialcashflow.cashoutflow': _('Cash Outflow'),
}


class JournalEntry(DataAbstractModel, AutoDocumentAbstractModel):
    je_transaction_app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}',
        null = True
    )
    je_transaction_id = models.UUIDField(verbose_name='Document that has foreign key to JE', null=True)
    je_transaction_data = models.JSONField(default=dict)
    je_posting_date = models.DateTimeField(null=True)
    je_document_date = models.DateTimeField(null=True)
    je_state = models.SmallIntegerField(default=0, choices=[(0, _('Draft')), (1, _('Posted')), (2, _('Reversed'))])
    total_debit = models.FloatField(default=0)
    total_credit = models.FloatField(default=0)
    # reversed_by là bút toán đảo ngược để map ngược lại vào bút toán gốc khi có bút toán sai
    reversed_by = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='je_reversed_by', null=True)
    period_mapped = models.ForeignKey(
        'saledata.Periods', on_delete=models.SET_NULL, related_name='je_period_mapped', null=True
    )
    sub_period_order = models.IntegerField()
    sub_period = models.ForeignKey(
        'saledata.SubPeriods', on_delete=models.SET_NULL, related_name='je_sub_period', null=True
    )

    class Meta:
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @staticmethod
    def valid_je_data(**kwargs):
        """ Valid JE data trước khi tạo phiếu tự động """
        # valid je fields
        required_fields = ['je_transaction_app_code', 'je_transaction_id', 'je_transaction_data', 'je_line_data']
        missing_fields = [field for field in required_fields if field not in kwargs or kwargs[field] is None]
        if missing_fields:
            print(f'[JE] Missing required fields: {missing_fields}')
            logger.error(msg=f'[JE] Missing required fields: {missing_fields}')
            return False
        je_line_data = kwargs.pop('je_line_data', {})
        # valid je lines
        debit_rows = je_line_data.get('debit_rows', [])
        credit_rows = je_line_data.get('credit_rows', [])
        if len(debit_rows) == 0 or len(credit_rows) == 0:
            logger.error(msg='[JE] Debit list length != Credit list length => can not create.')
            return False
        return True

    @classmethod
    def auto_create_journal_entry(cls, doc_obj, **kwargs):
        """
        Hàm tạo JE từ data truyền vào, nếu tạo thành công return JE_obj else return None
        Required kwargs:
        - je_transaction_app_code: app code của phiếu
        - je_transaction_id: id của phiếu
        - je_transaction_data: data json của phiếu
        - je_line_data: dữ liệu để tạo JE items
        """
        is_valid = cls.valid_je_data(**kwargs)
        if is_valid is False:
            return None
        try:
            tenant = doc_obj.tenant
            company = doc_obj.company
            doc_date = doc_obj.date_approved or doc_obj.date_created
            je_line_data = kwargs.pop('je_line_data', {})
            with transaction.atomic():
                period_obj = Periods.get_period_by_doc_date(tenant.id, company.id, doc_date)
                if period_obj:
                    sub_period_obj = Periods.get_sub_period_by_doc_date(period_obj, doc_date)
                    if sub_period_obj:
                        sub_period_order = Periods.get_sub_period_by_doc_date(period_obj, doc_date).order
                        je_obj = cls.objects.create(
                            **kwargs,
                            je_posting_date=timezone.now(),
                            je_document_date=timezone.now(),
                            je_state=1, # Posted
                            total_debit=0, # Updated below
                            total_credit=0, # Updated below
                            reversed_by=None,
                            period_mapped=period_obj,
                            sub_period_order=sub_period_order,
                            sub_period=sub_period_obj,
                            # system fields
                            system_status=3,
                            system_auto_create=True,
                            tenant=tenant,
                            company=company,
                            employee_created_id=doc_obj.employee_created_id,
                            employee_inherit_id=doc_obj.employee_inherit_id,
                            date_created=str(doc_obj.date_created),
                            date_approved=str(doc_obj.date_approved)
                        )
                        # duyệt tự động
                        CompanyFunctionNumber.auto_gen_code_based_on_config('journalentry', True, je_obj)
                        je_obj.system_status = 3
                        je_obj.save(update_fields=['code', 'system_status'])
                        total_debit, total_credit = JournalEntryLine.create_je_line_mapped(je_obj, je_line_data)
                        # cập nhập lại total value vào phiếu gốc
                        je_obj.total_debit = total_debit
                        je_obj.total_credit = total_credit
                        je_obj.save(update_fields=['total_debit', 'total_credit'])
                        print(f'# [JE] JE created successfully ({je_obj.code})!\n')
                        return je_obj
                    raise serializers.ValidationError({'sub_period_obj': 'Sub period order obj does not exist.'})
                raise serializers.ValidationError({'period_obj': f'Fiscal year {doc_date.year} does not exist.'})
        except Exception as err:
            print(err)
            return None


class JournalEntryLine(MasterDataAbstractModel):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='je_lines'
    )
    order = models.IntegerField(default=0)
    account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        null=True,
        related_name='je_line_account'
    )
    account_data = models.JSONField(default=dict)
    je_line_type = models.SmallIntegerField(choices=[(0, 'Debit'), (1, 'Credit')], default=0)
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        null=True,
        related_name='je_line_product_mapped'
    )
    product_mapped_data = models.JSONField(default=dict)
    business_partner = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='je_line_business_partner'
    )
    business_partner_data = models.JSONField(default=dict)
    business_employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='je_line_business_employee'
    )
    business_employee_data = models.JSONField(default=dict)
    debit = models.FloatField(default=0)
    credit = models.FloatField(default=0)
    is_fc = models.BooleanField(default=False)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.SET_NULL, null=True)
    currency_mapped_data = models.JSONField(default=dict) # {id, title, abbreviation, rate}
    taxable_value = models.FloatField(default=0)
    use_for_recon = models.BooleanField(default=False) # để biết đc là dòng bút toán này dùng để cấn trừ
    use_for_recon_type = models.CharField(max_length=100, blank=True) # để biết đc cặp bút toán làm cấn trừ.

    class Meta:
        verbose_name = 'Journal Entry Line'
        verbose_name_plural = 'Journal Entry Lines'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def parse_obj_je_line_mapped(cls, je_obj, order, item, je_line_type=0):
        # Nếu không truyền Currency vào, sẽ tự động lấy theo đồng tiền mặc định của công ty
        currency_mapped = item.get('currency_mapped')
        if not currency_mapped:
            currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()

        return cls(
            journal_entry=je_obj,
            order=order,
            account=item.get('account'),
            account_data={
                'id': str(item.get('account').id),
                'acc_code': item.get('account').acc_code,
                'acc_name': item.get('account').acc_name,
                'foreign_acc_name': item.get('account').foreign_acc_name
            } if item.get('account') else {},
            je_line_type=je_line_type,
            product_mapped=item.get('product_mapped'),
            product_mapped_data={
                'id': str(item.get('product_mapped').id),
                'code': item.get('product_mapped').code,
                'title': item.get('product_mapped').title,
            } if item.get('product_mapped') else {},
            business_partner=item.get('business_partner'),
            business_partner_data={
                'id': str(item.get('business_partner').id),
                'code': item.get('business_partner').code,
                'name': item.get('business_partner').name,
                'tax_code': item.get('business_partner').tax_code,
            } if item.get('business_partner') else {},
            business_employee=item.get('business_employee'),
            business_employee_data=item.get('business_employee').get_detail_with_group() if item.get(
                'business_employee'
            ) else {},
            debit=item.get('debit', 0) if je_line_type == 0 else 0,
            credit=item.get('credit', 0) if je_line_type == 1 else 0,
            is_fc=item.get('is_fc', False),
            currency_mapped=currency_mapped,
            currency_mapped_data={
                'id': str(currency_mapped.id),
                "abbreviation": currency_mapped.abbreviation,
                "title": currency_mapped.title,
                "rate": currency_mapped.rate
            } if currency_mapped else {},
            taxable_value=item.get('taxable_value', 0),
            use_for_recon=item.get('use_for_recon', False),
            use_for_recon_type=item.get('use_for_recon_type', '')
        )

    @classmethod
    def create_je_line_mapped(cls, je_obj, je_line_data=None):
        """
        je_line_data format:
        {
            'debit_rows' || 'credit_rows': [{
                'account': obj,
                'business_partner': obj,
                'business_employee': obj,
                'tax': obj,
                'debit': float,
                'credit': float,
                'is_fc': bool,
                'taxable_value': float,
            }, ...]
        }
        """
        print('# [JE] Creating JE lines...')
        if je_line_data is None:
            je_line_data = {}
        debit_rows = je_line_data.get('debit_rows', [])
        credit_rows = je_line_data.get('credit_rows', [])

        je_line_info = []
        total_debit = 0
        for order, item in enumerate(debit_rows): # get debit row
            debit_je_line_obj = cls.parse_obj_je_line_mapped(je_obj, order, item, 0)
            je_line_info.append(debit_je_line_obj)
            total_debit += item.get('debit', 0)
        total_credit = 0
        for order, item in enumerate(credit_rows): # get credit row
            credit_je_line_obj = cls.parse_obj_je_line_mapped(je_obj, order, item, 1)
            je_line_info.append(credit_je_line_obj)
            total_credit += item.get('credit', 0)
        cls.objects.bulk_create(je_line_info)
        return total_debit, total_credit
