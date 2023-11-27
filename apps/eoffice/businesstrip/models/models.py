import json
import uuid

from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

__all__ = ['BusinessRequest', 'ExpenseItemMapBusinessRequest', 'BusinessRequestAttachmentFile']


class BusinessRequest(DataAbstractModel):
    remark = models.TextField(blank=True)
    departure = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='business_request_departure'
    )
    destination = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='business_request_destination'
    )
    employee_on_trip = models.JSONField(
        default=dict,
        verbose_name='Employee on trip',
        null=True,
        help_text=json.dumps(
            [
                {
                    "id": "442e1a4d-1efa-45c9-92cc-2f1a7d4a90d2",
                    "last_name": "Jobs",
                    "first_name": "Steve",
                    "full_name": "Steve Jobs",
                    "group": {
                        "id": "442e1a4d-1efa-45c9-92cc-2f1a7d4a90d2",
                        "title": "CEO",
                        "code": "IS_CEO"
                    }
                }
            ]
        )
    )
    date_f = models.DateTimeField(
        verbose_name='From Date', null=True
    )
    morning_f = models.BooleanField(
        verbose_name='morning from',
        help_text='morning or afternoon shift of date from'
    )
    date_t = models.DateTimeField(
        verbose_name='To Date', null=True
    )
    morning_t = models.BooleanField(
        verbose_name='morning to',
        help_text='morning or afternoon shift of date to'
    )
    total_day = models.FloatField(
        verbose_name='Total day',
        help_text='total day of trip',
        null=True,
    )
    pretax_amount = models.FloatField(
        verbose_name='Pretax amount',
        help_text='',
        null=True,
    )
    taxes = models.FloatField(
        verbose_name='Taxes',
        help_text='',
        null=True,
    )
    total_amount = models.FloatField(
        verbose_name='Total amount',
        help_text='',
        null=True,
    )
    attachment = models.JSONField(
        default=list,
        null=True,
        verbose_name='Attachment file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    expense_items = models.ManyToManyField(
        'saledata.ExpenseItem',
        through='ExpenseItemMapBusinessRequest',
        symmetrical=False,
        related_name='expense_item_of_business_request',
    )

    def code_generator(self):
        b_rqst = BusinessRequest.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        if not self.code:
            char = "B"
            temper = b_rqst + 1
            code = f"{char}{temper:03d}"
            self.code = code

    def before_save(self):
        self.code_generator()

    def save(self, *args, **kwargs):
        if self.system_status == 3:
            self.before_save()
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Business trip request'
        verbose_name_plural = 'Business trip request'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ExpenseItemMapBusinessRequest(SimpleAbstractModel):
    title = models.CharField(max_length=100, blank=True)
    business_request = models.ForeignKey(
        BusinessRequest,
        on_delete=models.CASCADE,
        verbose_name='Business request map expense item',
        related_name='expense_item_map_business_request',
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name='Product need Picking',
    )
    expense_item_data = models.JSONField(
        default=dict,
        verbose_name='Expanse item data backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': ''}
            ]
        )
    )
    uom_txt = models.CharField(max_length=100, blank=True)
    quantity = models.FloatField(
        verbose_name='Quantity',
        null=True,
    )
    price = models.FloatField(default=0, verbose_name='Price')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name='',
    )
    tax_data = models.JSONField(
        default=dict,
        verbose_name='Tax backup',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '', 'rate': '',
            }
        )
    )
    subtotal = models.FloatField(default=0, verbose_name='Subtotal price')
    order = models.IntegerField(
        default=1
    )

    def put_backup_data(self):
        if self.tax and not self.tax_data:
            self.tax_data = {
                "id": str(self.tax_id),
                "title": str(self.tax.title),
                "code": str(self.tax.code),
                "rate": str(self.tax.rate),
            }
        if self.expense_item and not self.expense_item_data:
            self.expense_item_data = {
                "id": str(self.expense_item_id),
                "title": str(self.expense_item.title),
                "code": str(self.expense_item.code),
            }
        return True

    def before_save(self):
        self.put_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Business trip expanse item'
        verbose_name_plural = 'Business trip expanse item'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class BusinessRequestAttachmentFile(MasterDataAbstractModel):
    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Business trip attachment files',
        help_text='Business trip had one/many attachment file',
        related_name='business_request_attachment_file',
    )
    business_request = models.ForeignKey(
        'businesstrip.BusinessRequest',
        on_delete=models.CASCADE,
        verbose_name='Attachment file of business request'
    )
    order = models.SmallIntegerField(
        default=1
    )
    media_file = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        verbose_name = 'Business trip attachments'
        verbose_name_plural = 'Business trip attachments'
        default_permissions = ()
        permissions = ()
