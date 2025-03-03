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
        bulk_info_prd_type_sub = []
        for default_account in DefaultAccountDetermination.objects.filter(company=company, tenant=tenant):
            prd_type_account_deter_obj = ProductTypeAccountDetermination(
                company=company,
                tenant=tenant,
                product_type_mapped=product_type_obj,
                title=default_account.title,
                account_number_list=[{
                    'id': str(default_account.account_mapped_id),
                    'acc_code': default_account.account_mapped.acc_code,
                    'acc_name': default_account.account_mapped.acc_name,
                    'foreign_acc_name': default_account.account_mapped.foreign_acc_name,
                    'default_account_determination_type': default_account.default_account_determination_type
                }],
                account_determination_type=default_account.default_account_determination_type
            )
            bulk_info_prd_type.append(prd_type_account_deter_obj)
            bulk_info_prd_type_sub.append(
                ProductTypeAccountDeterminationSub(
                    prd_type_account_deter=prd_type_account_deter_obj,
                    account_mapped=default_account.account_mapped,
                )
            )
        ProductTypeAccountDetermination.objects.filter(product_type_mapped=product_type_obj).delete()
        ProductTypeAccountDetermination.objects.bulk_create(bulk_info_prd_type)
        ProductTypeAccountDeterminationSub.objects.filter(
            prd_type_account_deter__product_type_mapped=product_type_obj
        ).delete()
        ProductTypeAccountDeterminationSub.objects.bulk_create(bulk_info_prd_type_sub)
        return True
