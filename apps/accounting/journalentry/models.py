import logging
from django.db import models
from django.utils import timezone
from apps.masterdata.saledata.models import Account
from apps.shared import DataAbstractModel, SimpleAbstractModel, AutoDocumentAbstractModel


logger = logging.getLogger(__name__)


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

    class Meta:
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def auto_create_journal_entry(cls, **kwargs):
        """
        Hàm tạo JE từ data truyền vào, nếu tạo thành công return JE_obj else return None
        Required kwargs:
        - je_transaction_app_code: app code của phiếu
        - je_transaction_id: id của phiếu
        - je_transaction_data: data json của phiếu
        - je_item_data: dữ liệu để tạo JE items
        - tenant_id, company_id, employee_created_id: dữ liệu mặc định để tạo JE
        """
        required_fields = [
            'je_transaction_app_code', 'je_transaction_id', 'je_transaction_data', 'je_item_data',
            'tenant_id', 'company_id', 'employee_created_id'
        ]
        missing_fields = [
            field for field in required_fields if field not in kwargs or kwargs[field] is None
        ]
        if missing_fields:
            print(f'[JE] Missing required fields: {missing_fields}')
            logger.error(msg=f'[JE] Missing required fields: {missing_fields}')
            return None

        je_item_data = kwargs.pop('je_item_data', {})
        je_obj = cls.objects.create(
            **kwargs,
            code='JE00' + str(
                JournalEntry.objects.filter(
                    tenant_id=kwargs.get('tenant_id'),
                    company_id=kwargs.get('company_id'),
                    system_status=3
                ).count() + 1
            ),
            je_posting_date=timezone.now(),
            je_document_date=timezone.now(),
            system_status=3,
            system_auto_create=True
        )
        state = JournalEntryItem.create_je_item_mapped(je_obj, je_item_data)
        if not state:
            logger.error(msg='[JE] Failed to create Journal Entry Items.')
            return None
        print('# Journal Entry created successfully!')
        return je_obj


class JournalEntryItem(SimpleAbstractModel):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='je_items'
    )
    order = models.IntegerField(default=0)
    account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        null=True,
        related_name='je_item_account'
    )
    account_data = models.JSONField(default=dict)
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        null=True,
        related_name='je_item_product_mapped'
    )
    product_mapped_data = models.JSONField(default=dict)
    business_partner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        related_name='je_item_business_partner'
    )
    business_partner_data = models.JSONField(default=dict)
    debit = models.FloatField(default=0)
    credit = models.FloatField(default=0)
    is_fc = models.BooleanField(default=False)
    je_item_type = models.SmallIntegerField(choices=[(0, 'Debit'), (1, 'Credit')], default=0)
    taxable_value = models.FloatField(default=0)
    use_for_recon = models.BooleanField(default=False)
    # 'use_for_recon' để biết đc là dòng bút toán này dùng để cấn trừ
    use_for_recon_type = models.CharField(max_length=100, blank=True)
    # 'use_for_recon_type' để biết đc cặp bút toán làm cấn trừ.

    class Meta:
        verbose_name = 'Journal Entry Item'
        verbose_name_plural = 'Journal Entry Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create_je_item_mapped_sub(cls, je_obj, order, item, je_item_type=0):
        je_item_obj = cls(
            journal_entry=je_obj,
            order=order,
            account=item.get('account'),
            account_data={
                'id': str(item.get('account').id),
                'acc_code': item.get('account').acc_code,
                'acc_name': item.get('account').acc_name,
                'foreign_acc_name': item.get('account').foreign_acc_name
            } if item.get('account') else {},
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
            } if item.get('business_partner') else {},
            debit=item.get('debit', 0) if je_item_type == 0 else 0,
            credit=item.get('credit', 0) if je_item_type == 1 else 0,
            is_fc=item.get('is_fc', False),
            je_item_type=je_item_type,
            taxable_value=item.get('taxable_value', 0),
            use_for_recon=item.get('use_for_recon', False),
            use_for_recon_type=item.get('use_for_recon_type', '')
        )
        return je_item_obj

    @classmethod
    def create_je_item_mapped(cls, je_obj, je_item_data=None):
        """
        je_item_data format:
        {
            'debit_rows': [{
                'account': obj,
                'business_partner': obj,
                'tax': obj,
                'debit': float,
                'credit': float,
                'is_fc': bool,
                'taxable_value': float,
            }, ...],
            'credit_rows': [{
                'account': obj,
                'business_partner': obj,
                'tax': obj,
                'debit': float,
                'credit': float,
                'is_fc': bool,
                'taxable_value': float,
            }, ...]
        }
        """
        if je_item_data is None:
            je_item_data = {}
        debit_rows = je_item_data.get('debit_rows', [])
        credit_rows = je_item_data.get('credit_rows', [])
        if len(debit_rows) == 0 or len(credit_rows) == 0:
            logger.error(msg='[JE] Debit list length != Credit list length => can not create.')
            return False

        je_item_info = []
        # get debit row
        debit_value = 0
        for order, item in enumerate(debit_rows):
            je_item_info.append(cls.create_je_item_mapped_sub(je_obj, order, item, 0))
            debit_value += item.get('debit', 0)
        # get credit row
        credit_value = 0
        for order, item in enumerate(credit_rows):
            je_item_info.append(cls.create_je_item_mapped_sub(je_obj, order, item, 1))
            credit_value += item.get('credit', 0)

        cls.objects.bulk_create(je_item_info)
        return True
