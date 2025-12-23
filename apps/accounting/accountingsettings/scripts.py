from django.db import transaction
from apps.accounting.accountingsettings.data_list import (
    DOCUMENT_TYPE_LIST, POSTING_RULE_LIST, POSTING_GROUP_LIST, GL_MAPPING_TEMPLATE
)
from apps.accounting.accountingsettings.models import ChartOfAccounts, ChartOfAccountsSummarize
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JE_DOCUMENT_TYPE_APP, JEPostingGroup, JEGLAccountMapping, JEGroupAssignment,
    JEPostingGroupRoleKey, ROLE_KEY_CHOICES
)
from apps.accounting.journalentry.models import JournalEntrySummarize
from apps.core.company.models import Company
from apps.masterdata.saledata.models import ProductType, AccountType


class JournalEntryInitData:
    @staticmethod
    def generate_default_je_document_type_with_default_posting_rule(company_id):
        company_obj = Company.objects.get(id=company_id)

        # Clean data cũ
        JEDocumentType.objects.filter(company_id=company_id).delete()
        JEPostingRule.objects.filter(company_id=company_id).delete()

        # 1. Tạo Document Type
        app_map = dict(JE_DOCUMENT_TYPE_APP)
        bulk_info = []
        for module, code, app_code, _ in DOCUMENT_TYPE_LIST:
            bulk_info.append(JEDocumentType(
                tenant_id=company_obj.tenant_id,
                company_id=company_id,
                module=module,
                code=code,
                app_code=app_code,
                title=app_map.get(app_code, code),
                is_auto_je=True
            ))

        JEDocumentType.objects.bulk_create(bulk_info)
        print(f'> Created {len(bulk_info)} Doc Type')

        # 2. Tạo Posting Rules
        doc_types = JEDocumentType.objects.filter(company_id=company_id)
        doc_type_map = {item.code: item for item in doc_types}
        all_accounts = ChartOfAccounts.objects.filter(company_id=company_id)
        account_map = {item.acc_code: item for item in all_accounts}

        for posting_rule_data in POSTING_RULE_LIST:
            je_doc_type_code = posting_rule_data.get('je_doc_type')
            je_doc_type_obj = doc_type_map.get(je_doc_type_code)
            if je_doc_type_obj:
                bulk_info = []
                for rule_data in posting_rule_data.get('posting_rule_list', []):
                    rule_payload = rule_data.copy()
                    fixed_acc = None
                    fixed_code = rule_payload.pop('fixed_account_code', None)
                    if fixed_code:
                        fixed_acc = account_map.get(fixed_code)
                    bulk_info.append(JEPostingRule(
                        tenant_id=je_doc_type_obj.tenant_id,
                        company_id=je_doc_type_obj.company_id,
                        je_document_type=je_doc_type_obj,
                        fixed_account=fixed_acc,
                        **rule_payload
                    ))
                JEPostingRule.objects.bulk_create(bulk_info)
                print(f"  -> Created rules for {je_doc_type_code}")

        print(f"> Generated Rules for {company_obj.title}")
        return True

    @staticmethod
    def generate_default_je_posting_group(company_id):
        """ Bước 1: Tạo các Nhóm định khoản """
        company_obj = Company.objects.get(id=company_id)

        for group_data in POSTING_GROUP_LIST:
            JEPostingGroup.objects.update_or_create(
                tenant_id=company_obj.tenant_id,
                company_id=company_id,
                posting_group_type=group_data['posting_group_type'],
                code=group_data['code'],
                defaults={
                    'title': group_data['title']
                }
            )
        print(f"> Generated Posting Groups for {company_obj.title}")
        return True

    @staticmethod
    def generate_default_je_posting_group_role_keys(company_id):
        """
        Bước mới: Tạo danh sách các Role hợp lệ cho từng Nhóm
        """
        company_obj = Company.objects.get(id=company_id)
        all_groups = JEPostingGroup.objects.filter(company_id=company_id)

        role_choices_map = dict(ROLE_KEY_CHOICES)

        bulk_info = []
        for group in all_groups:
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config:
                continue

            for role_key, default_acc in acc_config.items():
                if default_acc is not None:
                    bulk_info.append(JEPostingGroupRoleKey(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=group,
                        role_key=role_key,
                        description=role_choices_map.get(role_key, role_key)
                    ))

        JEPostingGroupRoleKey.objects.filter(company_id=company_id).delete()
        JEPostingGroupRoleKey.objects.bulk_create(bulk_info)
        print(f"> Generated Role Keys for {len(bulk_info)} entries.")
        return True

    @classmethod
    def generate_default_je_group_assignment(cls, company_id):
        """ Bước 2: Tạo các phân bổ Nhóm định khoản """
        company_obj = Company.objects.get(id=company_id)
        bulk_info = []

        # ITEM_GROUP
        item_posting_group = JEPostingGroup.objects.filter(company_id=company_id, posting_group_type='ITEM_GROUP')
        item_group_map = {item.code: item for item in item_posting_group}
        if item_posting_group:
            item_code_map = {
                'goods': 'GOODS',  # Hàng hóa
                'material': 'MATERIAL',  # Nguyên vật liệu
                'finished_goods': 'FINISHED_GOODS',  # Thành phẩm
                'semi_finished': 'SEMI_FINISHED',  # Bán thành phẩm
                'tool': 'TOOL',  # Công cụ dụng cụ
                'service': 'SERVICE',  # Dịch vụ
                'consignment': 'CONSIGNMENT',  # Hàng gửi bán
            }
            default_product_type = ProductType.objects.filter(company_id=company_id, is_default=True)
            for item in default_product_type:
                posting_group_obj = item_group_map.get(item_code_map.get(item.code))
                if posting_group_obj:
                    bulk_info.append(JEGroupAssignment(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=posting_group_obj,
                        item_app=ProductType.get_model_code(),
                        item_app_data={
                            'id': str(item.id),
                            'code': item.code,
                            'title': item.title,
                        },
                        item_id=str(item.id)
                    ))
            print(f"Found {default_product_type.count()} Product Type records.")

        # PARTNER_GROUP
        partner_posting_group = JEPostingGroup.objects.filter(company_id=company_id, posting_group_type='PARTNER_GROUP')
        partner_group_map = {item.code: item for item in partner_posting_group}
        if partner_posting_group:
            partner_code_map = {
                'AT001': 'CUSTOMER',
                'AT002': 'SUPPLIER',
                'AT003': 'PARTNER_OTHER',
                'AT004': 'PARTNER_OTHER',
            }
            default_account_type = AccountType.objects.filter(company_id=company_id, is_default=True)
            for item in default_account_type:
                posting_group_obj = partner_group_map.get(partner_code_map.get(item.code))
                if posting_group_obj:
                    bulk_info.append(JEGroupAssignment(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=posting_group_obj,
                        item_app=AccountType.get_model_code(),
                        item_app_data={
                            'id': str(item.id),
                            'code': item.code,
                            'title': item.title,
                        },
                        item_id=str(item.id)
                    ))
            print(f"Found {default_account_type.count()} Account Type records.")

        JEGroupAssignment.objects.filter(company_id=company_id).delete()
        JEGroupAssignment.objects.bulk_create(bulk_info)
        print(f"Created {len(bulk_info)} JEGroupAssignment records.")
        return True

    @staticmethod
    def generate_default_je_gl_mapping(company_id):
        """ Bước 3: Map tài khoản cho từng nhóm """
        company_obj = Company.objects.get(id=company_id)
        all_groups = JEPostingGroup.objects.filter(company_id=company_id)

        all_accounts = ChartOfAccounts.objects.filter(company_id=company_id)
        account_map = {item.acc_code: item for item in all_accounts}

        bulk_info = []
        for group in all_groups:
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config:
                continue

            for role_key, acc_code in acc_config.items():
                if not acc_code:
                    continue
                # Tìm Account
                account = account_map.get(acc_code)
                if account:
                    bulk_info.append(JEGLAccountMapping(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=group,
                        role_key=role_key,
                        account=account
                    ))

        JEGLAccountMapping.objects.filter(company_id=company_id).delete()
        JEGLAccountMapping.objects.bulk_create(bulk_info)
        print(f"> Generated GL Mappings for {company_obj.title}")
        return True

    @classmethod
    def run(cls, company_id):
        with transaction.atomic():
            print("--- Cleaning old config ---")
            ChartOfAccountsSummarize.objects.filter(company_id=company_id).delete()
            JournalEntrySummarize.objects.filter(company_id=company_id).delete()
            cls.generate_default_je_document_type_with_default_posting_rule(company_id)
            cls.generate_default_je_posting_group(company_id)
            cls.generate_default_je_posting_group_role_keys(company_id)
            cls.generate_default_je_group_assignment(company_id)
            cls.generate_default_je_gl_mapping(company_id)
        return True
