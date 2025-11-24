from apps.accounting.accountingsettings.models import (
    AccountDetermination,
    AccountDeterminationSub,
    ChartOfAccounts
)


class AccountDeterminationSpecificRule:
    @staticmethod
    def get_specific_rules(company_id, context_dict, account_determination_types=None):
        filter_kwargs = {'company_id': company_id}
        if account_determination_types is not None:
            if isinstance(account_determination_types, list):
                filter_kwargs['account_determination_type__in'] = account_determination_types
            else:
                filter_kwargs['account_determination_type'] = account_determination_types
        acc_deter_list = AccountDetermination.objects.filter(**filter_kwargs).order_by(
            'account_determination_type', 'order'
        )
        result = []
        for header in acc_deter_list:
            best_rule_obj = AccountDeterminationSub.get_best_rule(
                company_id=company_id,
                transaction_key=header.transaction_key,
                context_dict=context_dict
            )
            if best_rule_obj:
                result.append({
                    'id': str(header.id),
                    'transaction_key': header.transaction_key,
                    'title': header.title or header.foreign_title,
                    'foreign_title': header.foreign_title,
                    'description': header.description,
                    'example': header.example,
                    'can_change_account': header.can_change_account,
                    'is_custom': best_rule_obj.is_custom,
                    'best_rule_account_mapped_data': best_rule_obj.account_mapped_data
                })
        return result

    @staticmethod
    def create_specific_rule(company_id, context_dict, transaction_key, account_id):
        account_obj = ChartOfAccounts.objects.filter(id=account_id).first()
        if account_obj:
            AccountDeterminationSub.create_specific_rule(
                company_id, transaction_key, account_obj.acc_code, context_dict
            )
        return True

    @staticmethod
    def delete_specific_rule(company_id, context_dict, transaction_key):
        AccountDeterminationSub.delete_specific_rule(company_id, transaction_key, context_dict)
        return True
