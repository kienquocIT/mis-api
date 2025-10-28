from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.acceptance.models import FinalAcceptance
from apps.shared import DataAbstractModel, SimpleAbstractModel, BastionFieldAbstractModel
from .advance_payment import AdvancePaymentCost
from ..utils import PaymentHandler


__all__ = [
    'Payment',
    'PaymentCost',
    'PaymentConfig',
    'PaymentAttachmentFile'
]


SALE_CODE_TYPE = [
    (0, _('Sale')),
    (1, _('Purchase')),
    (2, _('None-sale')),
    (3, _('Others'))
]


PAYMENT_METHOD = [
    (0, _('None')),
    (1, _('Cash')),
    (2, _('Bank Transfer')),
]


class Payment(DataAbstractModel, BastionFieldAbstractModel):
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="payment_quotation_mapped"
    )
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="payment_sale_order_mapped"
    )
    sale_code_type = models.SmallIntegerField(
        choices=SALE_CODE_TYPE,
        help_text='0 is Sale, 1 is Purchase, 2 is None-sale'
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        verbose_name='Supplier mapped',
        on_delete=models.CASCADE,
        null=True
    )
    employee_payment = models.ForeignKey(
        'hr.Employee',
        verbose_name='Employee payment mapped',
        on_delete=models.CASCADE,
        null=True
    )
    is_internal_payment = models.BooleanField(default=False)
    method = models.SmallIntegerField(
        choices=PAYMENT_METHOD,
        verbose_name='Payment method',
        help_text='0 is None, 1 is Cash, 2 is Bank Transfer'
    )
    bank_data = models.CharField(max_length=200, null=True, blank=True)
    payment_value_before_tax = models.FloatField(default=0)
    payment_value_tax = models.FloatField(default=0)
    payment_value = models.FloatField(default=0)
    payment_value_by_words = models.CharField(max_length=500, default='', blank=True)
    sale_code = models.CharField(max_length=100, null=True)
    free_input = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '1010563f-7c94-42f9-ba99-63d5d26a1aca'

    @classmethod
    def push_final_acceptance_payment(cls, instance):
        sale_order_id = None
        lease_order_id = None
        opportunity_id = None
        if instance.sale_order_mapped:
            sale_order_id = instance.sale_order_mapped_id
            opportunity_id = instance.sale_order_mapped.opportunity_id
        elif instance.opportunity:
            if instance.opportunity.sale_order:
                sale_order_id = instance.opportunity.sale_order_id
                opportunity_id = instance.opportunity_id
        if sale_order_id:
            list_data_indicator = []
            for payment_exp in instance.payment.all():
                if payment_exp.expense_type:
                    so_expense = payment_exp.expense_type.sale_order_expense_expense_item.first()
                    list_data_indicator.append({
                        'tenant_id': instance.tenant_id,
                        'company_id': instance.company_id,
                        'payment_id': instance.id,
                        'expense_item_id': payment_exp.expense_type_id,
                        'labor_item_id': so_expense.expense_id if so_expense else None,
                        'actual_value': payment_exp.expense_subtotal_price,
                        'actual_value_after_tax': payment_exp.expense_after_tax_price,
                        'acceptance_affect_by': 4,
                    })
            FinalAcceptance.push_final_acceptance(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                sale_order_id=sale_order_id,
                lease_order_id=lease_order_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                opportunity_id=opportunity_id,
                list_data_indicator=list_data_indicator,
            )
        return True

    @classmethod
    def convert_ap_cost(cls, instance):
        payment_cost_list = instance.payment.all()
        ap_convert_map = {}
        for item in payment_cost_list:
            for child in item.ap_cost_converted_list:
                ap_id = child.get('ap_cost_converted_id')
                value = child.get('value_converted')
                if ap_id and value:
                    if ap_id in ap_convert_map:
                        ap_convert_map[ap_id] += float(value)
                    else:
                        ap_convert_map[ap_id] = float(value)
        for ap_id, total_convert in ap_convert_map.items():
            ap_item = AdvancePaymentCost.objects.filter(id=ap_id).first()
            if not ap_item:
                raise ValueError('ap_item is not found')
            available = ap_item.expense_after_tax_price + ap_item.sum_return_value - ap_item.sum_converted_value
            if available < total_convert:
                raise ValueError(
                    f"Cannot convert advance payment (ID {ap_id}). "
                    f"Available: {available}, Requested: {total_convert}"
                )
        for ap_id, total_convert in ap_convert_map.items():
            ap_item = AdvancePaymentCost.objects.filter(id=ap_id).first()
            if ap_item:
                ap_item.sum_converted_value += total_convert
                ap_item.save(update_fields=['sum_converted_value'])
        return True

    @classmethod
    def set_true_file_is_approved(cls, instance):
        for m2m_attachment in instance.payment_attachments.all():
            attachment = m2m_attachment.attachment
            if attachment:
                attachment.is_approved = True
                attachment.save(update_fields=['is_approved'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('payment', True, self, kwargs)
                    self.push_final_acceptance_payment(self)
                    self.convert_ap_cost(self)
                    self.set_true_file_is_approved(self)

        # opportunity log
        PaymentHandler.push_opportunity_log(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class PaymentCost(SimpleAbstractModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="payment_cost_sale_order_mapped"
    )
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="payment_cost_quotation_mapped"
    )
    opportunity_mapped = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="payment_cost_opportunity_mapped"
    )
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="payment_cost_opportunity"
    )
    expense_type = models.ForeignKey('saledata.ExpenseItem', on_delete=models.CASCADE, null=True)
    expense_type_data = models.JSONField(default=dict)
    expense_description = models.CharField(max_length=250, null=True)
    expense_uom_name = models.CharField(max_length=150, null=True)
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    expense_tax = models.ForeignKey('saledata.Tax', null=True, on_delete=models.CASCADE)
    expense_tax_data = models.JSONField(default=dict)
    expense_tax_price = models.FloatField(default=0)
    expense_subtotal_price = models.FloatField(default=0)
    expense_after_tax_price = models.FloatField(default=0)
    document_number = models.CharField(max_length=150)
    real_value = models.FloatField(default=0)
    converted_value = models.FloatField(default=0)
    sum_value = models.FloatField(default=0)
    ap_cost_converted_list = models.JSONField(default=list)

    currency = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE)

    date_created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='The record created at value'
    )

    class Meta:
        verbose_name = 'Payment Cost'
        verbose_name_plural = 'Payment Costs'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class PaymentConfig(SimpleAbstractModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
    )
    employee_allowed = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Payment Config'
        verbose_name_plural = 'Payment Configs'
        default_permissions = ()
        permissions = ()


class PaymentAttachmentFile(M2MFilesAbstractModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='payment_attachments'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'payment'

    class Meta:
        verbose_name = 'Payment attachment'
        verbose_name_plural = 'Payment attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
