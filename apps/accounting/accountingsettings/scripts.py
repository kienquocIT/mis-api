from django.db import transaction
# Import đúng và đủ các list dữ liệu
from apps.accounting.accountingsettings.data_list import (
    DOCUMENT_TYPE_LIST, POSTING_RULE_LIST, POSTING_GROUP_LIST, GL_MAPPING_TEMPLATE
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

        # 1. Tạo Document Type
        # Convert tuple sang dict để lấy title an toàn
        app_map = dict(JE_DOCUMENT_TYPE_APP)

        for module, code, app_code in DOCUMENT_TYPE_LIST:
            obj, created = JEDocumentType.objects.update_or_create(
                tenant_id=company_obj.tenant_id,
                company_id=company_id,
                module=module,
                code=code,  # Transaction Key (VD: DO_SALE)
                defaults={
                    'app_code': app_code,  # Model Code (VD: inventory...)
                    'title': app_map.get(app_code, code),
                    'is_auto_je': True
                }
            )
            print(f'Processed Doc Type: {code}')

        # 2. Tạo Posting Rules
        for posting_rule_data in POSTING_RULE_LIST:
            # Tìm Document Type cha
            je_doc_type_code = posting_rule_data.get('je_doc_type')
            je_doc_type_obj = JEDocumentType.objects.filter(
                company_id=company_id, code=je_doc_type_code
            ).first()

            if je_doc_type_obj:
                bulk_info = []
                for rule_data in posting_rule_data.get('posting_rule_list', []):
                    # [FIX] Sao chép dict để không làm hỏng dữ liệu gốc khi pop
                    rule_payload = rule_data.copy()

                    # Xử lý Fixed Account
                    fixed_acc = None
                    fixed_code = rule_payload.pop('fixed_account_code', None)  # Dùng pop an toàn

                    if fixed_code:
                        fixed_acc = ChartOfAccounts.objects.filter(
                            company_id=company_id, acc_code=fixed_code
                        ).first()

                    # Tạo Object (Chưa save)
                    bulk_info.append(JEPostingRule(
                        tenant_id=je_doc_type_obj.tenant_id,
                        company_id=je_doc_type_obj.company_id,
                        je_document_type=je_doc_type_obj,
                        fixed_account=fixed_acc,
                        **rule_payload  # Các field còn lại (side, amount_source...)
                    ))

                if bulk_info:
                    JEPostingRule.objects.bulk_create(bulk_info)
                    print(f"  -> Created rules for {je_doc_type_code}")

        print(f"> Generated Rules for {company_obj.title}")
        return True

    @staticmethod
    def generate_default_je_posting_group(company_id):
        """ Bước 1: Tạo các Nhóm định khoản """
        company_obj = Company.objects.get(id=company_id)

        # [FIX QUAN TRỌNG] Phải loop qua POSTING_GROUP_LIST (Không phải RULE list)
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
    def generate_default_gl_mapping(company_id):
        """ Bước 2: Map tài khoản cho từng nhóm """
        company_obj = Company.objects.get(id=company_id)
        all_groups = JEPostingGroup.objects.filter(company_id=company_id)

        mappings_to_create = []
        for group in all_groups:
            # Lấy config từ Template
            acc_config = GL_MAPPING_TEMPLATE.get(group.code)
            if not acc_config: continue

            for role_key, acc_code in acc_config.items():
                if not acc_code: continue

                # Tìm Account
                account = ChartOfAccounts.get_acc(company_id, acc_code)
                if account:
                    mappings_to_create.append(JEGLAccountMapping(
                        tenant_id=company_obj.tenant_id,
                        company_id=company_id,
                        posting_group=group,
                        role_key=role_key,
                        account=account
                    ))

        # Reset và tạo lại
        JEGLAccountMapping.objects.filter(company_id=company_id).delete()
        JEGLAccountMapping.objects.bulk_create(mappings_to_create)

        print(f"> Generated GL Mappings for {company_obj.title}")
        return True

    @classmethod
    def run(cls, company_id):
        with transaction.atomic():
            # Xóa sạch dữ liệu cũ để init lại từ đầu (Clean Slate)
            print("--- Cleaning old config ---")
            JEPostingRule.objects.filter(company_id=company_id).delete()
            # Lưu ý: JEDocumentType nên dùng update_or_create thay vì delete để giữ ID nếu có ref
            # Nhưng nếu delete hết cũng được nếu chưa có transaction data
            # JEDocumentType.objects.filter(company_id=company_id).delete()

            # Chạy từng bước
            cls.generate_default_je_document_type_with_default_posting_rule(company_id)
            cls.generate_default_je_posting_group(company_id)
            cls.generate_default_gl_mapping(company_id)

        return True
