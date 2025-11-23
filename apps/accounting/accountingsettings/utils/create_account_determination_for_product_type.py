from apps.accounting.accountingsettings.models.account_determination import AccountDetermination
from apps.accounting.accountingsettings.models.product_type_account_determination import (
    ProductTypeAccountDetermination, ProductTypeAccountDeterminationSub
)


class AccountDeterminationForProductTypeHandler:
    @classmethod
    def create_account_determination_for_product_type(cls, product_type_obj, account_determination_type):
        """ Gắn TK mặc định cho kho vừa tạo """
        company = product_type_obj.company
        tenant = product_type_obj.tenant
        bulk_info_prd_type = []
        bulk_info_wh_sub = []
        for account_deter in AccountDetermination.objects.filter(
            company=company, tenant=tenant, account_determination_type=account_determination_type
        ):
            prd_type_account_deter_obj = ProductTypeAccountDetermination(
                company=company,
                tenant=tenant,
                product_type_mapped=product_type_obj,
                title=account_deter.title,
                foreign_title=account_deter.foreign_title,
                account_determination_type=account_determination_type,
                can_change_account=True
            )
            bulk_info_prd_type.append(prd_type_account_deter_obj)
            for item in account_deter.sub_items.all():
                bulk_info_wh_sub.append(
                    ProductTypeAccountDeterminationSub(
                        prd_type_account_deter=prd_type_account_deter_obj,
                        account_mapped=item.account_mapped,
                        account_mapped_data=item.account_mapped_data,
                    )
                )
        ProductTypeAccountDetermination.objects.filter(
            product_type_mapped=product_type_obj,
            account_determination_type=account_determination_type,
        ).delete()
        ProductTypeAccountDetermination.objects.bulk_create(bulk_info_prd_type)
        ProductTypeAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
