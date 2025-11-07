from apps.accounting.accountingsettings.models.account_determination import AccountDetermination
from apps.accounting.accountingsettings.models.warehouse_account_determination import (
    WarehouseAccountDetermination, WarehouseAccountDeterminationSub
)


class AccountDeterminationForWarehouseHandler:
    @classmethod
    def create_account_determination_for_warehouse(cls, warehouse_obj, account_determination_type):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = warehouse_obj.company
        tenant = warehouse_obj.tenant
        bulk_info_wh = []
        bulk_info_wh_sub = []
        for account_deter in AccountDetermination.objects.filter(
            company=company, tenant=tenant, account_determination_type=account_determination_type
        ):
            wh_account_deter_obj = WarehouseAccountDetermination(
                company=company,
                tenant=tenant,
                warehouse_mapped=warehouse_obj,
                title=account_deter.title,
                foreign_title=account_deter.foreign_title,
                account_determination_type=account_determination_type,
                can_change_account=True
            )
            bulk_info_wh.append(wh_account_deter_obj)
            for item in account_deter.account_determination_sub.all():
                bulk_info_wh_sub.append(
                    WarehouseAccountDeterminationSub(
                        wh_account_deter=wh_account_deter_obj,
                        account_mapped=item.account_mapped,
                        account_mapped_data=item.account_mapped_data,
                    )
                )
        WarehouseAccountDetermination.objects.filter(
            warehouse_mapped=warehouse_obj,
            account_determination_type=account_determination_type,
        ).delete()
        WarehouseAccountDetermination.objects.bulk_create(bulk_info_wh)
        WarehouseAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
