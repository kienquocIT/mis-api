from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.wh_account_deter import WarehouseAccountDetermination, \
    WarehouseAccountDeterminationSub


class AccountDeterminationForWarehouseHandler:
    @classmethod
    def create_account_determination_for_warehouse(cls, warehouse_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = warehouse_obj.company
        tenant = warehouse_obj.tenant
        bulk_info_wh = []
        bulk_info_wh_sub = []
        for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
            wh_account_deter_obj = WarehouseAccountDetermination(
                company=company,
                tenant=tenant,
                warehouse_mapped=warehouse_obj,
                title=default_account.title,
                account_number_list=[{
                    'id': str(default_account.account_mapped_id),
                    'acc_code': default_account.account_mapped.acc_code,
                    'acc_name': default_account.account_mapped.acc_name,
                    'foreign_acc_name': default_account.account_mapped.foreign_acc_name,
                    'default_account_determination_type': default_account.default_account_determination_type
                }],
                account_determination_type=default_account.default_account_determination_type
            )
            bulk_info_wh.append(wh_account_deter_obj)
            bulk_info_wh_sub.append(
                WarehouseAccountDeterminationSub(
                    wh_account_deter=wh_account_deter_obj,
                    account_mapped=default_account.account_mapped,
                )
            )
        WarehouseAccountDetermination.objects.filter(warehouse_mapped=warehouse_obj).delete()
        WarehouseAccountDetermination.objects.bulk_create(bulk_info_wh)
        WarehouseAccountDeterminationSub.objects.filter(wh_account_deter__warehouse_mapped=warehouse_obj).delete()
        WarehouseAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
