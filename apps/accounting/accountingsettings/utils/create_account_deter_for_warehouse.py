from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination, \
    DefaultAccountDeterminationSub
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
        for default_account in DefaultAccountDetermination.objects.filter(
            company=company, tenant=tenant, default_account_determination_type=2
        ):
            wh_account_deter_obj = WarehouseAccountDetermination(
                company=company,
                tenant=tenant,
                warehouse_mapped=warehouse_obj,
                title=default_account.title,
                foreign_title=default_account.foreign_title,
                account_determination_type=default_account.default_account_determination_type,
                can_change_account=True
            )
            bulk_info_wh.append(wh_account_deter_obj)
            for item in default_account.default_acc_deter_sub.all():
                bulk_info_wh_sub.append(
                    WarehouseAccountDeterminationSub(
                        wh_account_deter=wh_account_deter_obj,
                        account_mapped=item.account_mapped,
                        account_mapped_data=item.account_mapped_data,
                    )
                )
        WarehouseAccountDetermination.objects.filter(warehouse_mapped=warehouse_obj).delete()
        WarehouseAccountDetermination.objects.bulk_create(bulk_info_wh)
        WarehouseAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
