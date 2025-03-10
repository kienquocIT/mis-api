from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.journalentry.models import JournalEntry


class JEForDeliveryHandler:
    @classmethod
    def get_je_item_data(cls, delivery_obj):
        debit_rows_data = []
        credit_rows_data = []
        for deli_product in delivery_obj.delivery_product_delivery_sub.all():
            if deli_product.product:
                for pw_data in deli_product.delivery_pw_delivery_product.all():
                    # lấy cost hiện tại của sp
                    cost = deli_product.product.get_current_unit_cost(
                        get_type=1,
                        **{
                            'warehouse_id': pw_data.warehouse_id,
                            'sale_order_id': delivery_obj.sale_order_data.get('id'),
                        }
                    )
                    debit_rows_data.append({
                        # (+) giao hàng chưa xuất hóa đơn (mđ: 13881)
                        'account': deli_product.product.get_product_account_determination(
                            account_deter_foreign_title='Customer underpayment',
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
                        # (-) hàng hóa (mđ: 156)
                        'account': deli_product.product.get_product_account_determination(
                            account_deter_foreign_title='Inventory account',
                            warehouse_id=pw_data.warehouse_id
                        ),
                        'product_mapped': deli_product.product,
                        'business_partner': None,
                        'debit': 0,
                        'credit': cost,
                        'is_fc': False,
                        'taxable_value': 0,
                    })
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, delivery_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
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
            'employee_created_id': delivery_obj.employee_created_id,
            'je_item_data': {
                'debit_rows': debit_rows_data,
                'credit_rows': credit_rows_data
            }
        }
        JournalEntry.auto_create_journal_entry(**kwargs)
        print('Write to Journal Entry successfully!')
        return True
