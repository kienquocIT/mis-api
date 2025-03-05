import logging
from django.db import models, transaction
from django.utils import timezone
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.masterdata.saledata.models import Account
from apps.shared import DataAbstractModel, SimpleAbstractModel, AccountingAbstractModel


logger = logging.getLogger(__name__)


class JournalEntry(DataAbstractModel, AccountingAbstractModel):
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
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def auto_create_journal_entry(cls, **kwargs):
        """
        Required kwargs:
        - je_transaction_app_code, je_transaction_id, je_transaction_data, je_item_data,
        tenant_id, company_id, employee_created_id
        Optional kwargs:
        - je_posting_date, je_document_date
        """
        required_fields = [
            'je_transaction_app_code', 'je_transaction_id', 'je_transaction_data', 'je_item_data',
            'tenant_id', 'company_id', 'employee_created_id'
        ]
        missing_fields = [
            field for field in required_fields if field not in kwargs or kwargs[field] is None
        ]
        if missing_fields:
            logger.error(msg=f'Missing required fields: {missing_fields}')
            return None
        try:
            with transaction.atomic():
                je_item_data = kwargs.pop('je_item_data', {})
                je_obj = cls.objects.create(
                    **kwargs,
                    code='JE00' + str(
                        JournalEntry.objects.filter(
                            tenant_id=kwargs.get('tenant_id'),
                            company_id=kwargs.get('company_id'),
                            system_status=1
                        ).count() + 1
                    ),
                    je_posting_date=timezone.now(),
                    je_document_date=timezone.now(),
                    system_status=1,
                    system_auto_create=True
                )
                state = JournalEntryItem.create_je_item_mapped(je_obj, je_item_data)
                if not state:
                    logger.error(msg='Failed to create Journal Entry Items.')
                    transaction.set_rollback(True) # rollback thủ công vì không raise lỗi
                    return None
                print('Journal Entry created successfully!')
                return je_obj
        except Exception as err:
            logger.error(msg=f'Error while creating Journal Entry: {err}')
            return None


class JournalEntryItem(SimpleAbstractModel):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='je_items'
    )
    order = models.IntegerField(default=0)
    account = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.SET_NULL,
        null=True,
        related_name='je_item_account'
    )
    account_data = models.JSONField(default=dict)
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

    class Meta:
        verbose_name = 'Journal Entry Item'
        verbose_name_plural = 'Journal Entry Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create_je_item_sub(cls, je_obj, order, item, je_item_type=0):
        account_obj = item.get('account')
        account_data = {
            'acc_code': account_obj.acc_code,
            'acc_name': account_obj.acc_name,
            'foreign_acc_name': account_obj.foreign_acc_name
        } if account_obj else {}
        business_partner_obj = item.get('business_partner')
        business_partner_data = {
            'id': str(business_partner_obj.id),
            'code': business_partner_obj.code,
            'name': business_partner_obj.name,
        } if business_partner_obj else {}

        je_item_obj = cls(
            journal_entry=je_obj,
            order=order,
            account=account_obj,
            account_data=account_data,
            business_partner=business_partner_obj,
            business_partner_data=business_partner_data,
            debit=item.get('debit', 0) if je_item_type == 0 else 0,
            credit=item.get('credit', 0) if je_item_type == 1 else 0,
            is_fc=item.get('is_fc', False),
            je_item_type=je_item_type,
            taxable_value=item.get('taxable_value', 0),
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
            logger.error(msg='Invalid Journal entry item data => can not create.')
            return False

        je_item_info = []
        # get debit row
        debit_value = 0
        for order, item in enumerate(debit_rows):
            je_item_info.append(cls.create_je_item_sub(je_obj, order, item, 0))
            debit_value += item.get('debit', 0)
        # get credit row
        credit_value = 0
        for order, item in enumerate(credit_rows):
            je_item_info.append(cls.create_je_item_sub(je_obj, order, item, 1))
            credit_value += item.get('credit', 0)

        cls.objects.bulk_create(je_item_info)
        return True
