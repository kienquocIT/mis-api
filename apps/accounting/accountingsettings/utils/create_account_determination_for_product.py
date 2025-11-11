from apps.accounting.accountingsettings.models.account_determination import AccountDetermination
from apps.accounting.accountingsettings.models.product_account_determination import (
    ProductAccountDetermination, ProductAccountDeterminationSub
)


class AccountDeterminationForProductHandler:
    @classmethod
    def create_account_determination_for_product(cls, product_obj, account_determination_type):
        """ Gắn TK mặc định cho kho vừa tạo """
        if product_obj.account_deter_referenced_by == 2:
            company = product_obj.company
            tenant = product_obj.tenant
            bulk_info_prd = []
            bulk_info_wh_sub = []
            for account_deter in AccountDetermination.objects.filter(
                company=company, tenant=tenant, account_determination_type=account_determination_type
            ):
                prd_account_deter_obj = ProductAccountDetermination(
                    company=company,
                    tenant=tenant,
                    foreign_title=account_deter.foreign_title,
                    product_mapped=product_obj,
                    title=account_deter.title,
                    account_determination_type=account_determination_type,
                    can_change_account=True
                )
                bulk_info_prd.append(prd_account_deter_obj)
                for item in account_deter.account_determination_sub.all():
                    bulk_info_wh_sub.append(
                        ProductAccountDeterminationSub(
                            prd_account_deter=prd_account_deter_obj,
                            account_mapped=item.account_mapped,
                            account_mapped_data=item.account_mapped_data,
                        )
                    )
            ProductAccountDetermination.objects.filter(
                product_mapped=product_obj,
                account_determination_type=account_determination_type,
            ).delete()
            ProductAccountDetermination.objects.bulk_create(bulk_info_prd)
            ProductAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
