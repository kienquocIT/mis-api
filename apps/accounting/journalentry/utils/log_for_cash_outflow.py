import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry


logger = logging.getLogger(__name__)


class JEForCOFHandler:
    @classmethod
    def get_je_item_data(cls, cof_obj):
        debit_rows_data = []
        credit_rows_data = []
        if cof_obj.cash_value > 0:
            for account in DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=cof_obj.tenant_id,
                company_id=cof_obj.company_id,
                foreign_title='Cash in hand received from customers'
            ):
                credit_rows_data.append({
                    # (+) Tiền mặt thu từ khách hàng (mđ: 1111)
                    'account': account,
                    'product_mapped': None,
                    'business_partner': None,
                    'debit': 0,
                    'credit': cof_obj.cash_value,
                    'is_fc': False,
                    'taxable_value': 0,
                })
        if cof_obj.bank_value > 0:
            for account in DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=cof_obj.tenant_id,
                company_id=cof_obj.company_id,
                foreign_title='Cash in bank received from customers'
            ):
                credit_rows_data.append({
                    # (+) Tiền mặt thu từ khách hàng (mđ: 1121)
                    'account': account,
                    'product_mapped': None,
                    'business_partner': None,
                    'debit': 0,
                    'credit': cof_obj.bank_value,
                    'is_fc': False,
                    'taxable_value': 0,
                })
        for account in DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=cof_obj.tenant_id,
            company_id=cof_obj.company_id,
            foreign_title='Payable to suppliers'
        ):
            debit_rows_data.append({
                # (-) Phải thu khách hàng (mđ: 331)
                'account': account,
                'product_mapped': None,
                'business_partner': cof_obj.customer,
                'debit': cof_obj.total_value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'cof-ap'
            })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, cof_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.get_je_item_data(cof_obj)
                kwargs = {
                    'je_transaction_app_code': cof_obj.get_model_code(),
                    'je_transaction_id': str(cof_obj.id),
                    'je_transaction_data': {
                        'id': str(cof_obj.id),
                        'code': cof_obj.code,
                        'title': cof_obj.title,
                        'date_created': str(cof_obj.date_created),
                        'date_approved': str(cof_obj.date_approved),
                    },
                    'tenant_id': cof_obj.tenant_id,
                    'company_id': cof_obj.company_id,
                    'employee_created_id': cof_obj.employee_created_id,
                    'je_item_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(**kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
