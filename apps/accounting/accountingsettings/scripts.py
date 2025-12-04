from apps.accounting.accountingsettings.data_list import APP_LIST, POSTING_RULE_APP_LIST
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JE_DOCUMENT_TYPE_APP
)


class JournalEntryInitData:
    @staticmethod
    def create_je_document_type(tenant_id, company_id):
        """ Hàm khởi tạo các app hỗ trợ bút toán tự động """
        for module, code, app_code in APP_LIST:
            obj, created = JEDocumentType.objects.update_or_create(
                tenant_id=tenant_id,
                company_id=company_id,
                module=module,
                code=code,
                app_code=app_code,
                title=dict(JE_DOCUMENT_TYPE_APP)[app_code],
                defaults={'is_auto_je': False}
            )
            print(f'Created {app_code}.' if created else f'Updated {app_code}.')
        return True

    @staticmethod
    def create_je_posting_rules(company_id):
        """ Hàm khởi tạo các app hỗ trợ bút toán tự động """
        for je_doc_type in POSTING_RULE_APP_LIST:
            je_doc_type_obj = JEDocumentType.objects.filter(
                company_id=company_id, code=je_doc_type.get('je_doc_type')
            ).first()
            if je_doc_type_obj:
                bulk_info = []
                for rule_data in je_doc_type.get('posting_rule_list', []):
                    print(rule_data)
                    rule_data['je_document_type'] = je_doc_type_obj
                    fixed_account_obj = ChartOfAccounts.objects.filter(
                        company_id=company_id, acc_code=rule_data.pop('fixed_account_code')
                    ).first()
                    rule_data['fixed_account'] = fixed_account_obj
                    bulk_info.append(JEPostingRule(
                        tenant_id=je_doc_type_obj.tenant_id,
                        company_id=je_doc_type_obj.company_id,
                        **rule_data
                    ))
                    print(f"Created {rule_data.get('role_key')} for {rule_data.get('je_document_type')}.")
                je_doc_type_obj.je_posting_rules.all().delete()
                JEPostingRule.objects.bulk_create(bulk_info)
        return True
