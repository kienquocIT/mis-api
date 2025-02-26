from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.wh_account_deter import WarehouseAccountDetermination


class AccountDeterminationForWarehouseHandler:
    @classmethod
    def create_account_determination_for_warehouse(cls, warehouse_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = warehouse_obj.company
        tenant = warehouse_obj.tenant
        bulk_info_wh = []
        for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
            bulk_info_wh.append(
                WarehouseAccountDetermination(
                    company=company,
                    tenant=tenant,
                    warehouse_mapped=warehouse_obj,
                    title=default_account.title,
                    account_mapped=default_account.account_mapped,
                    account_determination_type=default_account.default_account_determination_type
                )
            )
        WarehouseAccountDetermination.objects.filter(warehouse_mapped=warehouse_obj).delete()
        WarehouseAccountDetermination.objects.bulk_create(bulk_info_wh)
        return True
