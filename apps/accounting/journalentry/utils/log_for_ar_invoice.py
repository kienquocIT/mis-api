from django.db.models import Sum

from apps.accounting.accountingsettings.models import ChartOfAccounts, DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry, JournalEntryItem


class JEForARInvoiceHandler:
    @classmethod
    def get_je_item_data(cls, ar_invoice_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for item in ar_invoice_obj.ar_invoice_deliveries.all():
            delivery_obj = item.delivery_mapped
            for deli_product in delivery_obj.delivery_product_delivery_sub.all():
                if deli_product.product:
                    for pw_data in deli_product.delivery_pw_delivery_product.all():
                        # lấy cost lúc giao của sp
                        cost = deli_product.product.get_current_unit_cost(
                            get_type=1,
                            **{
                                'warehouse_id': pw_data.warehouse_id,
                                'sale_order_id': delivery_obj.sale_order_data.get('id'),
                            }
                        )
                        sum_cost += cost
                        debit_rows_data.append({
                            # (+) giá vốn hàng bán (mđ: 632)
                            'account': item.product.get_product_account_determination(
                                account_deter_foreign_title = 'Cost of goods sold',
                                warehouse_id=pw_data.warehouse_id
                            ),
                            'product_mapped': deli_product.product,
                            'business_partner': None,
                            'debit': cost,
                            'credit': 0,
                            'is_fc': False,
                            'taxable_value': 0,
                        })
        credit_rows_data.append({
            # (-) giao hàng chưa xuất hóa đơn (mđ: 13881)
            'account': DefaultAccountDetermination.objects.filter(
                tenant=ar_invoice_obj.tenant,
                company=ar_invoice_obj.company,
                foreign_title='Customer underpayment'
            ).first(),
            'product_mapped': None,
            'business_partner': None,
            'debit': 0,
            'credit': sum_cost,
            'is_fc': False,
            'taxable_value': 0,
        })
        debit_rows_data.append({
            # (-) phải thu của khách hàng - trong nước (mđ: 131)
            'account': DefaultAccountDetermination.objects.filter(
                tenant=ar_invoice_obj.tenant,
                company=ar_invoice_obj.company,
                foreign_title='Receivables from domestic customers'
            ).first(),
            'product_mapped': None,
            'business_partner': ar_invoice_obj.customer_mapped,
            'debit': ar_invoice_obj.product_subtotal_final,
            'credit': 0,
            'is_fc': False,
            'taxable_value': 0,
        })
        credit_rows_data.append({
            # (+) doanh thu bán hàng hóa - trong nước (mđ: 511)
            'account': DefaultAccountDetermination.objects.filter(
                tenant=ar_invoice_obj.tenant,
                company=ar_invoice_obj.company,
                foreign_title='Domestic sales revenue'
            ).first(),
            'product_mapped': None,
            'business_partner': None,
            'debit': 0,
            'credit': ar_invoice_obj.product_subtotal_final - ar_invoice_obj.product_tax_value,
            'is_fc': False,
            'taxable_value': 0,
        })
        credit_rows_data.append({
            # (+) thuế GTGT đầu ra (mđ: 3331)
            'account': DefaultAccountDetermination.objects.filter(
                tenant=ar_invoice_obj.tenant,
                company=ar_invoice_obj.company,
                foreign_title='Sales tax'
            ).first(),
            'product_mapped': None,
            'business_partner': None,
            'debit': 0,
            'credit': ar_invoice_obj.product_tax_value,
            'is_fc': False,
            'taxable_value': ar_invoice_obj.product_tax_value,
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
