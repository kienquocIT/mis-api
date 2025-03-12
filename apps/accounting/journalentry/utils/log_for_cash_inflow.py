from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry


class JEForCIFHandler:
    @classmethod
    def get_je_item_data(cls, cif_obj):
        debit_rows_data = []
        credit_rows_data = []
        if cif_obj.cash_value > 0:
            credit_rows_data.append({
                # (-) Tiền mặt thu từ khách hàng (mđ: 1111)
                'account_data': DefaultAccountDetermination.get_default_account_deter_sub_data(
                    tenant_id=cif_obj.tenant_id,
                    company_id=cif_obj.company_id,
                    foreign_title='Cash in hand received from customers'
                ),
                'product_mapped': None,
                'business_partner': None,
                'debit': cif_obj.cash_value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
            })
        if cif_obj.bank_value > 0:
            credit_rows_data.append({
                # (-) Tiền mặt thu từ khách hàng (mđ: 1121)
                'account_data': DefaultAccountDetermination.get_default_account_deter_sub_data(
                    tenant_id=cif_obj.tenant_id,
                    company_id=cif_obj.company_id,
                    foreign_title='Cash in bank received from customers'
                ),
                'product_mapped': None,
                'business_partner': None,
                'debit': cif_obj.bank_value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
            })
        debit_rows_data.append({
            # (+) Phải thu khách hàng (mđ: 131)
            'account_data': DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=cif_obj.tenant_id,
                company_id=cif_obj.company_id,
                foreign_title='Receivables from customers'
            ),
            'product_mapped': None,
            'business_partner': cif_obj.customer,
            'debit': 0,
            'credit': cif_obj.total_value,
            'is_fc': False,
            'taxable_value': 0,
        })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, cif_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        debit_rows_data, credit_rows_data = cls.get_je_item_data(cif_obj)
        kwargs = {
            'je_transaction_app_code': cif_obj.get_model_code(),
            'je_transaction_id': str(cif_obj.id),
            'je_transaction_data': {
                'id': str(cif_obj.id),
                'code': cif_obj.code,
                'title': cif_obj.title,
                'date_created': str(cif_obj.date_created),
                'date_approved': str(cif_obj.date_approved),
            },
            'tenant_id': cif_obj.tenant_id,
            'company_id': cif_obj.company_id,
            'employee_created_id': cif_obj.employee_created_id,
            'je_item_data': {
                'debit_rows': debit_rows_data,
                'credit_rows': credit_rows_data
            }
        }
        JournalEntry.auto_create_journal_entry(**kwargs)
        return True
