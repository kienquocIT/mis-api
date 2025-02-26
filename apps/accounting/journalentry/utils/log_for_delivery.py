from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.journalentry.models import JournalEntry


class JEForDeliveryHandler:
    @classmethod
    def get_sum_delivery_cost(cls, delivery_obj):
        """ Lấy tổng cost hiện tại của tất cả các sản phẩm trong phếu Giao hàng """
        sum_delivery_cost = 0
        for deli_product in delivery_obj.delivery_product_delivery_sub.all():
            if deli_product.product:
                for pw_data in deli_product.delivery_pw_delivery_product.all():
                    sum_delivery_cost += deli_product.product.get_unit_cost_by_warehouse(
                        warehouse_id=pw_data.warehouse_id,
                        get_type=1
                    )
        return sum_delivery_cost

    @classmethod
    def push_to_journal_entry(cls, delivery_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        value = cls.get_sum_delivery_cost(delivery_obj)
        debit_rows_data = [
            {
                # (-) hàng hóa
                'account': ChartOfAccounts.objects.filter(acc_code=156).first(),
                'business_partner': None,
                'debit': value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
            }
        ]
        credit_rows_data = [
            {
                # (+) giao hàng chưa xuất hóa đơn
                'account': ChartOfAccounts.objects.filter(acc_code=13881).first(),
                'business_partner': None,
                'debit': 0,
                'credit': value,
                'is_fc': False,
                'taxable_value': 0,
            }
        ]
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
