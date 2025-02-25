from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.prd_account_deter import ProductAccountDetermination


class AccountDeterminationForProductHandler:
    @classmethod
    def create_account_determination_for_product(cls, product_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = product_obj.company
        tenant = product_obj.tenant
        bulk_info_wh = []
        for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
            bulk_info_wh.append(
                ProductAccountDetermination(
                    company=company,
                    tenant=tenant,
                    product_mapped=product_obj,
                    title=default_account.title,
                    account_mapped=default_account.account_mapped,
                    account_determination_type=default_account.default_account_determination_type
                )
            )
        ProductAccountDetermination.objects.filter(product_mapped=product_obj).delete()
        ProductAccountDetermination.objects.bulk_create(bulk_info_wh)
        return True
