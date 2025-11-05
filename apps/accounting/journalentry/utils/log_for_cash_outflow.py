import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry


logger = logging.getLogger(__name__)


class JEForCOFHandler:
    @classmethod
    def parse_je_line_data(cls, cof_obj):
        debit_rows_data = []
        credit_rows_data = []
        if cof_obj.cash_value > 0:
            account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=cof_obj.tenant_id,
                company_id=cof_obj.company_id,
                foreign_title='Cash in hand received from customers'
            )
            if len(account_list) == 1:
                credit_rows_data.append({
                    # (+) Tiền mặt thu từ khách hàng (mđ: 1111)
                    'account': account_list[0],
                    'product_mapped': None,
                    'business_partner': None,
                    'debit': 0,
                    'credit': cof_obj.cash_value,
                    'is_fc': False,
                    'taxable_value': 0,
                })

        if cof_obj.bank_value > 0:
            account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=cof_obj.tenant_id,
                company_id=cof_obj.company_id,
                foreign_title='Cash in bank received from customers'
            )
            if len(account_list) == 1:
                credit_rows_data.append({
                    # (+) Tiền mặt thu từ khách hàng (mđ: 1121)
                    'account': account_list[0],
                    'product_mapped': None,
                    'business_partner': None,
                    'debit': 0,
                    'credit': cof_obj.bank_value,
                    'is_fc': False,
                    'taxable_value': 0,
                })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=cof_obj.tenant_id,
            company_id=cof_obj.company_id,
            foreign_title='Payable to suppliers'
        )
        if len(account_list) == 1:
            debit_rows_data.append({
                # (-) Phải trả cho NCC (mđ: 331)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': cof_obj.customer or cof_obj.supplier,
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
                debit_rows_data, credit_rows_data = cls.parse_je_line_data(cof_obj)
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
                    'je_line_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(cof_obj, **kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
