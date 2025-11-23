import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import AccountDetermination
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.models import ReportStockLog


logger = logging.getLogger(__name__)


class JEForDeliveryHandler:
    @classmethod
    def parse_je_line_data(cls, dlvr_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for deli_product in dlvr_obj.delivery_product_delivery_sub.all():
            if deli_product.product:
                for pw_data in deli_product.delivery_pw_delivery_product.all():
                    # lấy cost hiện tại của sp
                    stock_log_item = ReportStockLog.objects.filter(
                        product=deli_product.product,
                        trans_code=dlvr_obj.code,
                        trans_id=str(dlvr_obj.id)
                    ).first()
                    cost = stock_log_item.value if stock_log_item else 0
                    sum_cost += cost
                    account_list = deli_product.product.get_product_account_deter_sub_data(
                        account_deter_foreign_title='Inventory account',
                        warehouse_id=pw_data.warehouse_id
                    )
                    if len(account_list) == 1:
                        credit_rows_data.append({
                            # (+) hàng hóa (mđ: 156)
                            'account': account_list[0],
                            'product_mapped': deli_product.product,
                            'business_partner': None,
                            'debit': 0,
                            'credit': cost,
                            'is_fc': False,
                            'taxable_value': 0,
                        })

        account_list = AccountDetermination.get_sub_items_data(
            tenant_id=dlvr_obj.tenant_id,
            company_id=dlvr_obj.company_id,
            foreign_title='Customer underpayment'
        )
        if len(account_list) == 1:
            debit_rows_data.append({
                # (-) giao hàng chưa xuất hóa đơn (mđ: 13881)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': sum_cost,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'deli-ar'
            })

        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, dlvr_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.parse_je_line_data(dlvr_obj)
                kwargs = {
                    'je_transaction_app_code': dlvr_obj.get_model_code(),
                    'je_transaction_id': str(dlvr_obj.id),
                    'je_transaction_data': {
                        'id': str(dlvr_obj.id),
                        'code': dlvr_obj.code,
                        'title': dlvr_obj.title,
                        'date_created': str(dlvr_obj.date_created),
                        'date_approved': str(dlvr_obj.date_approved),
                    },
                    'je_line_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(dlvr_obj, **kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
