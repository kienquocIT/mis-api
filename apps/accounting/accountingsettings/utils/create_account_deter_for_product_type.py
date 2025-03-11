from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.prd_type_account_deter import ProductTypeAccountDetermination, \
    ProductTypeAccountDeterminationSub


class AccountDeterminationForProductTypeHandler:
    @classmethod
    def create_account_determination_for_product_type(cls, product_type_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = product_type_obj.company
        tenant = product_type_obj.tenant
        bulk_info_prd_type = []
        bulk_info_wh_sub = []
        for default_account in DefaultAccountDetermination.objects.filter(
            company=company, tenant=tenant, default_account_determination_type=2
        ):
            prd_type_account_deter_obj = ProductTypeAccountDetermination(
                company=company,
                tenant=tenant,
                product_type_mapped=product_type_obj,
                title=default_account.title,
                foreign_title=default_account.foreign_title,
                account_determination_type=default_account.default_account_determination_type,
                can_change_account=True
            )
            bulk_info_prd_type.append(prd_type_account_deter_obj)
            for item in default_account.default_acc_deter_sub.all():
                bulk_info_wh_sub.append(
                    ProductTypeAccountDeterminationSub(
                        prd_type_account_deter=prd_type_account_deter_obj,
                        account_mapped=item.account_mapped,
                        account_mapped_data=item.account_mapped_data,
                    )
                )
        ProductTypeAccountDetermination.objects.filter(product_type_mapped=product_type_obj).delete()
        ProductTypeAccountDetermination.objects.bulk_create(bulk_info_prd_type)
        ProductTypeAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
