import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.models import ReportStockLog


logger = logging.getLogger(__name__)


class JEForGoodsReceiptHandler:
    @classmethod
    def get_je_item_data(cls, gr_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for gr_prd_obj in gr_obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                # lấy cost hiện tại của sp
                stock_log_item = ReportStockLog.objects.filter(
                    product=gr_prd_obj.product,
                    trans_code=gr_obj.code,
                    trans_id=str(gr_obj.id)
                ).first()
                cost = stock_log_item.value if stock_log_item else 0
                sum_cost += cost
                account_list = gr_prd_obj.product.get_product_account_deter_sub_data(
                    account_deter_foreign_title='Inventory account',
                    warehouse_id=gr_wh_obj.warehouse_id
                )
                if len(account_list) == 1:
                    debit_rows_data.append({
                        # (-) hàng hóa (mđ: 156)
                        'account': account_list[0],
                        'product_mapped': gr_prd_obj.product,
                        'business_partner': None,
                        'debit': cost,
                        'credit': 0,
                        'is_fc': False,
                        'taxable_value': 0,
                    })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=gr_obj.tenant_id,
            company_id=gr_obj.company_id,
            foreign_title='Customer overpayment'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) nhập hàng chưa nhập hóa đơn (mđ: 33881)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': 0,
                'credit': sum_cost,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'gr-ap'
            })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, gr_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.get_je_item_data(gr_obj)
                kwargs = {
                    'je_transaction_app_code': gr_obj.get_model_code(),
                    'je_transaction_id': str(gr_obj.id),
                    'je_transaction_data': {
                        'id': str(gr_obj.id),
                        'code': gr_obj.code,
                        'title': gr_obj.title,
                        'date_created': str(gr_obj.date_created),
                        'date_approved': str(gr_obj.date_approved),
                    },
                    'tenant_id': str(gr_obj.tenant_id),
                    'company_id': str(gr_obj.company_id),
                    'employee_created_id': str(gr_obj.employee_created_id),
                    'employee_inherit_id': str(gr_obj.employee_inherit_id),
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
