import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.utils import ReportInvCommonFunc


logger = logging.getLogger(__name__)


class JEForDeliveryHandler:
    @classmethod
    def get_je_item_data(cls, delivery_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for deli_product in delivery_obj.delivery_product_delivery_sub.all():
            if deli_product.product:
                for pw_data in deli_product.delivery_pw_delivery_product.all():
                    # lấy cost hiện tại của sp
                    casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                        pw_data.uom,
                        pw_data.quantity_delivery
                    )
                    cost = deli_product.product.get_current_unit_cost(
                        get_type=1,
                        **{
                            'warehouse_id': pw_data.warehouse_id,
                            'sale_order_id': delivery_obj.sale_order_data.get('id'),
                        }
                    ) * casted_quantity
                    sum_cost += cost
                    for account in deli_product.product.get_product_account_deter_sub_data(
                        account_deter_foreign_title='Inventory account',
                        warehouse_id=pw_data.warehouse_id
                    ):
                        credit_rows_data.append({
                            # (-) hàng hóa (mđ: 156)
                            'account': account,
                            'product_mapped': deli_product.product,
                            'business_partner': None,
                            'debit': 0,
                            'credit': cost,
                            'is_fc': False,
                            'taxable_value': 0,
                        })
        for account in DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=delivery_obj.tenant_id,
            company_id=delivery_obj.company_id,
            foreign_title='Customer underpayment'
        ):
            debit_rows_data.append({
                # (+) giao hàng chưa xuất hóa đơn (mđ: 13881)
                'account': account,
                'product_mapped': None,
                'business_partner': None,
                'debit': sum_cost,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_order': 1
            })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, delivery_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.get_je_item_data(delivery_obj)
                kwargs = {
                    'je_transaction_app_code': delivery_obj.get_model_code(),
                    'je_transaction_id': str(delivery_obj.id),
                    'je_transaction_data': {
                        'id': str(delivery_obj.id),
                        'code': delivery_obj.code,
                        'title': delivery_obj.title,
                        'date_created': str(delivery_obj.date_created),
                        'date_approved': str(delivery_obj.date_approved),
                    },
                    'tenant_id': delivery_obj.tenant_id,
                    'company_id': delivery_obj.company_id,
                    'employee_created_id': delivery_obj.employee_created_id or delivery_obj.employee_inherit_id,
                    'je_item_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    },
                    'je_posting_date': str(delivery_obj.date_approved),
                    'je_document_date': str(delivery_obj.date_approved),
                }
                je_obj = JournalEntry.auto_create_journal_entry(**kwargs)
                if je_obj:
                    return True
                transaction.set_rollback(True)  # rollback thủ công
                return None
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
