from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.cashoutflow.utils import AdvanceHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel, BastionFieldAbstractModel

class Consulting(DataAbstractModel, BastionFieldAbstractModel):
    value = models.FloatField(default=0)
    due_date = models.DateField()
    abstract_content = models.TextField(blank=True, null=True)
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="consulting_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )

    product_categories = models.ManyToManyField(
        'saledata.ProductCategory',
        through='ConsultingProductCategory',
        symmetrical=False,
        blank=True,
        related_name='consulting_product_categories',
    )

    attachment_data = models.ManyToManyField(
        'attachments.Files',
        through='ConsultingAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_consulting',
    )

    class Meta:
        verbose_name = 'Consulting'
        verbose_name_plural = 'Consultings'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '3a369ba5-82a0-4c4d-a447-3794b67d1d02' # consulting's application id

    # FILE
    @classmethod
    def set_true_file_is_approved(cls, instance):
        for m2m_attachment in instance.consulting_attachment_consulting.all():
            attachment = m2m_attachment.attachment
            if attachment:
                attachment.is_approved = True
                attachment.save(update_fields=['is_approved'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    self.set_true_file_is_approved(instance=self)  # file

        AdvanceHandler.push_opportunity_log(self)
        # hit DB
        super().save(*args, **kwargs)

class ConsultingDocument(MasterDataAbstractModel):
    consulting = models.ForeignKey(
        'consulting.Consulting',
        on_delete=models.CASCADE,
        verbose_name="consulting",
        related_name='consulting_document_consulting',
    )
    document_type = models.ForeignKey(
        'saledata.DocumentType',
        on_delete=models.CASCADE,
        verbose_name="consulting document type",
        related_name="consulting_document_document_type",
        null=True,
        blank=True
    )
    remark = models.TextField(verbose_name="remark", blank=True, null=True)
    attachment_data = models.JSONField(default=list, help_text='data json of attachment')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Consulting document'
        verbose_name_plural = 'Consulting documents'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

class ConsultingAttachment(M2MFilesAbstractModel):
    consulting = models.ForeignKey(
        'consulting.Consulting',
        on_delete=models.CASCADE,
        verbose_name="consulting",
        related_name="consulting_attachment_consulting",
    )
    document = models.ForeignKey(
        'consulting.ConsultingDocument',
        on_delete=models.SET_NULL,
        verbose_name="document",
        related_name="consulting_attachment_consulting_document",
        null=True
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'consulting'

    class Meta:
        verbose_name = 'Consulting attachment'
        verbose_name_plural = 'Consulting attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

class ConsultingProductCategory(SimpleAbstractModel):
    consulting = models.ForeignKey(
        'consulting.Consulting',
        on_delete=models.CASCADE,
        verbose_name="consulting",
        related_name="consulting_product_category_consulting",
    )
    product_category = models.ForeignKey(
        'saledata.ProductCategory',
        null=True,
        on_delete=models.CASCADE,
        related_name='consulting_product_category'
    )
    value = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Consulting product category'
        verbose_name_plural = 'Consulting product category list'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
