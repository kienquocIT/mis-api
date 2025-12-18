from django.db import transaction
from apps.accounting.accountingsettings.data_list import (
    DOCUMENT_TYPE_LIST, POSTING_RULE_LIST, POSTING_GROUP_LIST, GL_MAPPING_TEMPLATE
)
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JE_DOCUMENT_TYPE_APP, JEPostingGroup, JEGLAccountMapping, JEGroupAssignment,
    JEPostingGroupRoleKey, ROLE_KEY_CHOICES
)
from apps.core.company.models import Company
from apps.masterdata.saledata.models import ProductType, AccountType


class JournalEntryInitData:
    @staticmethod
    def generate_default_je_document_type_with_default_posting_rule(company_id):
        company_obj = Company.objects.get(id=company_id)
        JEDocumentType.objects.filter(company_id=company_id).delete()
        JEPostingRule.objects.filter(company_id=company_id).delete()

        # 1. Tạo Document Type
        app_map = dict(JE_DOCUMENT_TYPE_APP)
        bulk_info = []
        for module, code, app_code in DOCUMENT_TYPE_LIST:
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
        for posting_rule_data in POSTING_RULE_LIST:
            je_doc_type_code = posting_rule_data.get('je_doc_type')
            je_doc_type_obj = JEDocumentType.objects.filter(
                company_id=company_id, code=je_doc_type_code
            ).first()
            if je_doc_type_obj:
                bulk_info = []
                for rule_data in posting_rule_data.get('posting_rule_list', []):
                    rule_payload = rule_data.copy()
                    fixed_acc = None
                    fixed_code = rule_payload.pop('fixed_account_code', None)
                    if fixed_code:
                        fixed_acc = ChartOfAccounts.objects.filter(company_id=company_id, acc_code=fixed_code).first()
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

        bulk_info = []
        for group in all_groups:
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config:
                continue

            for role_key in acc_config.keys():
                if acc_config[role_key]:
                    bulk_info.append(JEPostingGroupRoleKey(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=group,
                        role_key=role_key,
                        description=dict(ROLE_KEY_CHOICES).get(role_key)
                    ))

        JEPostingGroupRoleKey.objects.filter(company_id=company_id).delete()
        JEPostingGroupRoleKey.objects.bulk_create(bulk_info)
        print(f"> Generated Role Keys for {len(bulk_info)} entries.")
        return True

    @classmethod
    def generate_default_je_group_assignment(cls, company_id):
        """ Bước 2: Tạo các phân bổ Nhóm định khoản """
        # ITEM_GROUP
        company_obj = Company.objects.get(id=company_id)

        bulk_info = []

        item_posting_group = JEPostingGroup.objects.filter(
            company_id=company_id,
            posting_group_type='ITEM_GROUP'
        )
        if item_posting_group:
            ITEM_CODE_MAP = {
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
                posting_group_obj = item_posting_group.filter(code=ITEM_CODE_MAP.get(item.code)).first()
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

        partner_posting_group = JEPostingGroup.objects.filter(
            company_id=company_id,
            posting_group_type='PARTNER_GROUP'
        )
        if partner_posting_group:
            ITEM_CODE_MAP = {
                'AT001': 'CUSTOMER',
                'AT002': 'SUPPLIER',
                'AT003': 'PARTNER_OTHER',
                'AT004': 'PARTNER_OTHER',
            }
            default_account_type = AccountType.objects.filter(company_id=company_id, is_default=True)
            for item in default_account_type:
                posting_group_obj = partner_posting_group.filter(code=ITEM_CODE_MAP.get(item.code)).first()
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

        bulk_info = []
        for group in all_groups:
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config:
                continue

            for role_key, acc_code in acc_config.items():
                if not acc_code:
                    continue
                # Tìm Account
                account = ChartOfAccounts.get_acc(company_id, acc_code)
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
            cls.generate_default_je_document_type_with_default_posting_rule(company_id)
            cls.generate_default_je_posting_group(company_id)
            cls.generate_default_je_posting_group_role_keys(company_id)
            cls.generate_default_je_group_assignment(company_id)
            cls.generate_default_je_gl_mapping(company_id)
        return True
