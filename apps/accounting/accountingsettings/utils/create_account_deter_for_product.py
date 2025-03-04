from apps.accounting.accountingsettings.models.account_masterdata_models import DefaultAccountDetermination
from apps.accounting.accountingsettings.models.prd_account_deter import ProductAccountDetermination


class AccountDeterminationForProductHandler:
    @classmethod
    def create_account_determination_for_product(cls, product_obj):
        """ Gắn TK mặc định cho kho vừa tạo """
        if product_obj.account_deter_referenced_by == 2:
            company = product_obj.company
            tenant = product_obj.tenant
            bulk_info_prd = []
            for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
                prd_account_deter_obj = ProductAccountDetermination(
                    company=company,
                    tenant=tenant,
                    product_mapped=product_obj,
                    title=default_account.title,
                    account_mapped=default_account.account_mapped,
                    account_mapped_data={
                        'id': str(default_account.account_mapped_id),
                        'acc_code': default_account.account_mapped.acc_code,
                        'acc_name': default_account.account_mapped.acc_name,
                        'foreign_acc_name': default_account.account_mapped.foreign_acc_name
                    },
                    account_determination_type=default_account.default_account_determination_type
                )
                bulk_info_prd.append(prd_account_deter_obj)
            ProductAccountDetermination.objects.filter(product_mapped=product_obj).delete()
            ProductAccountDetermination.objects.bulk_create(bulk_info_prd)
        return True
