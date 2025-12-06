from apps.accounting.accountingsettings.data_list import (
    DOCUMENT_TYPE_LIST, POSTING_RULE_LIST, GL_MAPPING_TEMPLATE
)
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JE_DOCUMENT_TYPE_APP, JEPostingGroup, JEGLAccountMapping
)
from apps.core.company.models import Company


class JournalEntryInitData:
    @staticmethod
    def generate_default_je_document_type_with_default_posting_rule(company_id):
        company_obj = Company.objects.get(id=company_id)
        for module, code, app_code in DOCUMENT_TYPE_LIST:
            obj, created = JEDocumentType.objects.update_or_create(
                tenant_id=company_obj.tenant_id,
                company_id=company_id,
                module=module,
                code=code,
                app_code=app_code,
                title=dict(JE_DOCUMENT_TYPE_APP)[app_code],
                defaults={'is_auto_je': True}
            )
            print(f'Created {app_code}.' if created else f'Updated {app_code}.')
        for posting_rule_data in POSTING_RULE_LIST:
            je_doc_type_obj = JEDocumentType.objects.filter(
                company_id=company_id, code=posting_rule_data.get('je_doc_type')
            ).first()
            if je_doc_type_obj:
                bulk_info = []
                for rule_data in posting_rule_data.get('posting_rule_list', []):
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
                JEPostingRule.objects.bulk_create(bulk_info)
        print(f"> Generated Posting Rules for {company_obj.title}")
        return True

    @staticmethod
    def generate_default_je_posting_group(company_id):
        """ Bước 1: Tạo các Nhóm định khoản """
        company_obj = Company.objects.get(id=company_id)
        for group_data in POSTING_RULE_LIST:
            JEPostingGroup.objects.create(
                tenant_id=company_obj.tenant_id,
                company_id=company_id,
                posting_group_type=group_data['posting_group_type'],
                code=group_data['code'],
                title=group_data['title']
            )
        print(f"> Generated Posting Groups for {company_obj.title}")
        return True

    @staticmethod
    def generate_default_gl_mapping(company_id):
        """ Bước 2: Map tài khoản cho từng nhóm """
        company_obj = Company.objects.get(id=company_id)
        all_groups = JEPostingGroup.objects.filter(company_id=company_id)
        mappings_to_create = []
        for group in all_groups:
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config:
                continue
            for role_key, acc_code in acc_config.items():
                if not acc_code:
                    continue
                account = ChartOfAccounts.get_acc(company_id, acc_code)
                mappings_to_create.append(JEGLAccountMapping(
                    tenant_id=company_obj.tenant_id,
                    company_id=company_id,
                    posting_group=group,
                    role_key=role_key,
                    account=account
                ))
        JEGLAccountMapping.objects.filter(company_id=company_id).delete()
        JEGLAccountMapping.objects.bulk_create(mappings_to_create)
        print(f"> Generated GL Mappings for {company_obj.title}")
        return True

    @classmethod
    def run(cls, company_id):
        JEDocumentType.objects.filter(company_id=company_id).delete()
        JEPostingRule.objects.filter(company_id=company_id).delete()
        JEPostingGroup.objects.filter(company_id=company_id).delete()
        JEGLAccountMapping.objects.filter(company_id=company_id).delete()
        cls.generate_default_je_document_type_with_default_posting_rule(company_id)
        cls.generate_default_je_posting_group(company_id)
        cls.generate_default_gl_mapping(company_id)
        return True
