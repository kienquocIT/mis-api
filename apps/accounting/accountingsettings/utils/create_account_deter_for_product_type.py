from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.prd_type_account_deter import ProductTypeAccountDetermination


class AccountDeterminationForProductTypeHandler:
    @classmethod
    def create_account_determination_for_product_type(cls, product_type_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = product_type_obj.company
        tenant = product_type_obj.tenant
        bulk_info_wh = []
        for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
            bulk_info_wh.append(
                ProductTypeAccountDetermination(
                    company=company,
                    tenant=tenant,
                    product_type_mapped=product_type_obj,
                    title=default_account.title,
                    account_mapped=default_account.account_mapped,
                    account_determination_type=default_account.default_account_determination_type
                )
            )
        ProductTypeAccountDetermination.objects.filter(product_type_mapped=product_type_obj).delete()
        ProductTypeAccountDetermination.objects.bulk_create(bulk_info_wh)
        return True
