from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.prd_account_deter import ProductAccountDetermination, \
    ProductAccountDeterminationSub


class AccountDeterminationForProductHandler:
    @classmethod
    def create_account_determination_for_product(cls, product_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        if product_obj.account_deter_referenced_by == 2:
            company = product_obj.company
            tenant = product_obj.tenant
            bulk_info_prd = []
            bulk_info_wh_sub = []
            for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
                prd_account_deter_obj = ProductAccountDetermination(
                    company=company,
                    tenant=tenant,
                    foreign_title=default_account.foreign_title,
                    product_mapped=product_obj,
                    title=default_account.title,
                    account_determination_type=default_account.default_account_determination_type
                )
                bulk_info_prd.append(prd_account_deter_obj)
                for item in default_account.default_acc_deter_sub.all():
                    bulk_info_wh_sub.append(
                        ProductAccountDeterminationSub(
                            prd_account_deter=prd_account_deter_obj,
                            account_mapped=item.account_mapped,
                            account_mapped_data=item.account_mapped_data,
                        )
                    )
            ProductAccountDetermination.objects.filter(product_mapped=product_obj).delete()
            ProductAccountDetermination.objects.bulk_create(bulk_info_prd)
            ProductAccountDeterminationSub.objects.bulk_create(bulk_info_wh_sub)
        return True
