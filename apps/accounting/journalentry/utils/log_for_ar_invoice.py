from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.journalentry.models import JournalEntry, JournalEntryItem


class JEForARInvoiceHandler:
    @classmethod
    def get_je_item_data(cls, ar_invoice_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_delivery_cost = 0
        for item in ar_invoice_obj.ar_invoice_deliveries.all():
            for je_item in JournalEntryItem.objects.filter(
                    journal_entry__je_transaction_id=str(item.delivery_mapped_id),
                    account__acc_code=13881
            ):
                sum_delivery_cost += je_item.credit
        debit_rows_data.append({
            # (-) giao hàng chưa xuất hóa đơn
            'account': ChartOfAccounts.objects.filter(
                tenant_id=ar_invoice_obj.tenant_id,
                company_id=ar_invoice_obj.company_id,
                acc_code=13881
            ).first(),
            'business_partner': None,
            'debit': sum_delivery_cost,
            'credit': 0,
            'is_fc': False,
            'taxable_value': 0,
        })
        debit_rows_data.append({
            # (-) phải thu của khách hàng (mđ: 131)
            'account': ChartOfAccounts.objects.filter(
                tenant_id=ar_invoice_obj.tenant_id,
                company_id=ar_invoice_obj.company_id,
                acc_code=131
            ).first(),
            'business_partner': ar_invoice_obj.customer_mapped,
            'debit': ar_invoice_obj.sum_after_tax_value,
            'credit': 0,
            'is_fc': False,
            'taxable_value': 0,
        })
        credit_rows_data.append({
            # (+) giá vốn hàng bán (mđ: 632)
            'account': ChartOfAccounts.objects.filter(
                tenant_id=ar_invoice_obj.tenant_id,
                company_id=ar_invoice_obj.company_id,
                acc_code=632
            ).first(),
            'business_partner': None,
            'debit': 0,
            'credit': sum_delivery_cost,
            'is_fc': False,
            'taxable_value': 0,
        })
        credit_rows_data.append({
            # (+) doanh thu bán hàng hóa (mđ: 5111)
            'account': ChartOfAccounts.objects.filter(
                tenant_id=ar_invoice_obj.tenant_id,
                company_id=ar_invoice_obj.company_id,
                acc_code=5111
            ).first(),
            'business_partner': None,
            'debit': 0,
            'credit': ar_invoice_obj.sum_after_tax_value - ar_invoice_obj.sum_tax_value,
            'is_fc': False,
            'taxable_value': 0,
        })
        credit_rows_data.append({
            # (+) thuế GTGT đầu ra (mđ: 3331)
            'account': ChartOfAccounts.objects.filter(
                tenant_id=ar_invoice_obj.tenant_id,
                company_id=ar_invoice_obj.company_id,
                acc_code=3331
            ).first(),
            'business_partner': None,
            'debit': 0,
            'credit': ar_invoice_obj.sum_tax_value,
            'is_fc': False,
            'taxable_value': ar_invoice_obj.sum_pretax_value,
        })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, ar_invoice_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        debit_rows_data, credit_rows_data = cls.get_je_item_data(ar_invoice_obj)
        kwargs = {
            'je_transaction_app_code': ar_invoice_obj.get_model_code(),
            'je_transaction_id': str(ar_invoice_obj.id),
            'je_transaction_data': {
                'id': str(ar_invoice_obj.id),
                'code': ar_invoice_obj.code,
                'title': ar_invoice_obj.title,
                'date_created': str(ar_invoice_obj.date_created),
                'date_approved': str(ar_invoice_obj.date_approved),
            },
            'tenant_id': ar_invoice_obj.tenant_id,
            'company_id': ar_invoice_obj.company_id,
            'employee_created_id': ar_invoice_obj.employee_created_id,
            'je_item_data': {
                'debit_rows': debit_rows_data,
                'credit_rows': credit_rows_data
            }
        }
        JournalEntry.auto_create_journal_entry(**kwargs)
        print('Write to Journal Entry successfully!')
        return True
