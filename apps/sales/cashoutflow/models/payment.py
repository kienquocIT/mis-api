from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.acceptance.models import FinalAcceptance
from apps.shared import DataAbstractModel, SimpleAbstractModel
from .advance_payment import AdvancePaymentCost

__all__ = [
    'Payment',
    'PaymentCost',
    'PaymentConfig',
    'PaymentAttachmentFile'
]

from ..utils import PaymentHandler

SALE_CODE_TYPE = [
    (0, _('Sale')),
    (1, _('Purchase')),
    (2, _('None-sale')),
    (3, _('Others'))
]

ADVANCE_PAYMENT_METHOD = [
    (0, _('None')),
    (1, _('Cash')),
    (2, _('Bank Transfer')),
]


class Payment(DataAbstractModel):
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="payment_sale_order_mapped"
    )
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="payment_quotation_mapped"
    )
    opportunity_mapped = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="payment_opportunity_mapped"
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
        choices=ADVANCE_PAYMENT_METHOD,
        verbose_name='Payment method',
        help_text='0 is None, 1 is Cash, 2 is Bank Transfer'
    )
    creator_name = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='payment_creator_name'
    )

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def push_final_acceptance_payment(cls, instance):
        sale_order_id = None
        opportunity_id = None
        if instance.sale_order_mapped:
            sale_order_id = instance.sale_order_mapped_id
            opportunity_id = instance.sale_order_mapped.opportunity_id
        elif instance.opportunity_mapped:
            if instance.opportunity_mapped.sale_order:
                sale_order_id = instance.opportunity_mapped.sale_order_id
                opportunity_id = instance.opportunity_mapped_id
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
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                opportunity_id=opportunity_id,
                list_data_indicator=list_data_indicator,
            )
        return True

    @classmethod
    def convert_ap_cost(cls, instance):
        payment_cost_list = instance.payment.all()
        ap_item_valid = []
        ap_item_value_converted_valid = []
        for item in payment_cost_list:
            for child in item.ap_cost_converted_list:
                ap_item_id = child.get('ap_cost_converted_id', None)
                ap_item_value_converted = child.get('value_converted', None)
                if ap_item_id and ap_item_value_converted:
                    ap_item = AdvancePaymentCost.objects.filter(id=ap_item_id).first()
                    if ap_item:
                        available = (ap_item.expense_after_tax_price + ap_item.sum_return_value -
                                     ap_item.sum_converted_value)
                        if available >= ap_item_value_converted:
                            ap_item_valid.append(ap_item)
                            ap_item_value_converted_valid.append(ap_item_value_converted)
                        else:
                            raise ValueError('Can not convert advance payment expenses to payment')
        for index, item in enumerate(ap_item_valid):
            item.sum_converted_value += float(ap_item_value_converted_valid[index])
            item.save(update_fields=['sum_converted_value'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                code_generated = CompanyFunctionNumber.gen_code(company_obj=self.company, func=7)
                if code_generated:
                    self.code = code_generated
                else:
                    records = Payment.objects.filter(
                        company=self.company, tenant=self.tenant, is_delete=False, system_status=3
                    )
                    self.code = 'PM.00' + str(records.count() + 1)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                self.push_final_acceptance_payment(self)
                self.convert_ap_cost(self)

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
    expense_type = models.ForeignKey('saledata.ExpenseItem', on_delete=models.CASCADE, null=True)
    expense_description = models.CharField(max_length=150, null=True)
    expense_uom_name = models.CharField(max_length=150, null=True)
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    expense_tax = models.ForeignKey('saledata.Tax', null=True, on_delete=models.CASCADE)
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

    class Meta:
        verbose_name = 'Payment attachment'
        verbose_name_plural = 'Payment attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
