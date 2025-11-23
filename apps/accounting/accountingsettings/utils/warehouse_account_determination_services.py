from apps.accounting.accountingsettings.models import AccountDetermination, AccountDeterminationSub, ChartOfAccounts


class WarehouseAccountingService:

    @staticmethod
    def get_warehouse_settings(company_id, warehouse_id):
        """
        Thay thế cho việc query model WarehouseAccountDetermination cũ.
        Hàm này trả về danh sách các Rule áp dụng cho kho này.
        """
        # 1. Lấy tất cả các loại nghiệp vụ Kho (Type 2: Inventory)
        headers = AccountDetermination.objects.filter(
            company_id=company_id,
            account_determination_type=2  # Inventory Type
        ).order_by('order')

        result = []
        context = {'warehouse_id': int(warehouse_id)}

        for header in headers:
            # Tìm tài khoản đang áp dụng cho kho này (Pull Logic)
            # Nó sẽ tự tìm: Có rule riêng cho kho ko? Ko thì lấy Default.
            acc = AccountDeterminationSub.get_gl_account(
                company_id=company_id,
                transaction_key=header.transaction_key,
                context_dict=context
            )

            # Kiểm tra xem đây là cấu hình riêng hay mặc định
            # (Tương đương việc check xem record có tồn tại trong bảng cũ hay ko)
            specific_key = AccountDeterminationSub.generate_key_from_dict(context)
            is_custom = AccountDeterminationSub.objects.filter(
                account_determination=header,
                search_rule=specific_key
            ).exists()

            result.append({
                'transaction_key': header.transaction_key,
                'title': header.title,
                'account_id': acc.id if acc else None,
                'account_code': acc.acc_code if acc else '',
                'account_name': acc.acc_name if acc else '',
                'is_custom': is_custom  # True = Đang dùng cấu hình riêng, False = Đang dùng mặc định
            })

        return result

    @staticmethod
    def save_warehouse_setting(company_id, warehouse_id, transaction_key, account_id):
        """
        Thay thế cho việc save() vào model WarehouseAccountDeterminationSub cũ.
        """
        # Dùng lại Manager chúng ta đã viết
        context = {'warehouse_id': int(warehouse_id)}

        if account_id:
            # Tạo/Update rule riêng
            # Tìm Account object
            account = ChartOfAccounts.objects.get(id=account_id)
            AccountDetermination.create_specific_rule(
                company_id, transaction_key, account.acc_code, context
            )
        else:
            # Nếu user xóa tài khoản -> Xóa rule riêng (Về mặc định)
            AccountDetermination.delete_specific_rule(
                company_id, transaction_key, context
            )