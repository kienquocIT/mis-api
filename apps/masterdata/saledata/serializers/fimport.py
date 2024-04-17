import json

from rest_framework import serializers

from apps.masterdata.saledata.models import (
    Contact, Salutation, Account, Currency, AccountGroup, AccountType, Industry,
    PaymentTerm, Term, Price,
)
from apps.masterdata.saledata.serializers import (
    create_employee_map_account, add_account_types_information,
    add_shipping_address_information, add_billing_address_information,
)
from apps.shared import AccountsMsg, HrMsg, BaseMsg

from apps.core.base.models import Currency as BaseCurrency
from apps.core.hr.models import Employee


class SaleDataCurrencyImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'abbreviation')


class SaleDataCurrencyImportSerializer(serializers.ModelSerializer):
    abbreviation = serializers.CharField(max_length=100)

    @classmethod
    def validate_abbreviation(cls, attrs):
        if not Currency.objects.filter_current(fill__company=True, abbreviation=attrs).exists():
            return attrs
        raise serializers.ValidationError(
            {
                'abbreviation': BaseMsg.CODE_IS_EXISTS,
            }
        )

    currency = serializers.CharField(max_length=10, allow_null=True, allow_blank=True)

    @classmethod
    def validate_currency(cls, attrs):
        if attrs:
            try:
                return BaseCurrency.objects.get(code=attrs)
            except BaseCurrency.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'currency': BaseMsg.CODE_NOT_EXIST,
                    }
                )
        return None

    rate = serializers.FloatField(allow_null=True)

    @classmethod
    def validate_rate(cls, attrs):
        if attrs:
            return attrs
        return None

    class Meta:
        model = Currency
        fields = ('currency', 'abbreviation', 'rate')


class AccountGroupImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ('id', 'title', 'code')


class AccountGroupImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if value:
            if AccountGroup.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    title = serializers.CharField(max_length=100)

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})

    description = serializers.CharField(max_length=200, allow_blank=True)

    @classmethod
    def validate_description(cls, attrs):
        if not attrs:
            return attrs
        return ''

    class Meta:
        model = AccountGroup
        fields = ('code', 'title', 'description')


class AccountTypeImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code')


class AccountTypeImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if value:
            if AccountType.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    title = serializers.CharField(max_length=100)

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})

    class Meta:
        model = AccountType
        fields = ('code', 'title', 'description')


class IndustryImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code')


class IndustryImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if value:
            if Industry.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    title = serializers.CharField(max_length=100)

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})

    class Meta:
        model = Industry
        fields = ('code', 'title', 'description')


class PaymentTermImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerm
        fields = ('id', 'title')


class PaymentTermImportSubTermSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Term.objects.create(**validated_data)

    class Meta:
        model = Term
        fields = (
            'value',
            'unit_type',
            'day_type',
            'no_of_days',
            'after',
            'order',
        )


TERM_HEP_TEXT = """
[Loại, Giá trị, Kiểu ngày, Số ngày, Kích hoạt khi]
- Loại: Đơn vị để tính cho phần giá trị
0: Phần trăm
1: Số lượng
2: Cân bằng
- Giá trị: Dữ liệu số thực theo đơn vị tính của loại
- Kiểu ngày: Kiểu ngày để tính chính xác cho phần số lượng ngày
1: Ngày làm việc
2: Ngày dương lịch
- Số ngày: Dữ liệu số nguyên về số ngày cho công thức, sẽ tuân thủ bộ đếm ngày của "Kiểu ngày"
- Kích hoạt khi: Là mốc thời gian mà sự kiện sẽ được kích hoạt
1: Ngày ký hợp đồng
2: Ngày giao hàng
3: Ngày xuất hoá đơn
4: Ngày thông qua 
5: Kết thúc tháng hoá đơn
6: Ngày đặt hàng
- Ví dụ: [[0, 30, 1, 1, 1], [0, 30, 1, 1, 2], [0, 40, 1, 1, 3]] : Cấu hình này là chính sách thanh toán theo phần 
trăm với mốc 30 - 30 - 40 cho sự kiện ký hợp đồng - giao hàng - xuất hoá đơn và ngày chậm nhất thanh toán là 1 ngày 
làm việc sau sự kiện kích hoạt.
"""


class PaymentTermImportSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError(
            {
                'title': BaseMsg.REQUIRED,
            }
        )

    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, attrs):
        if not PaymentTerm.objects.filter_current(fill__company=True, code=attrs).exists():
            return attrs
        raise serializers.ValidationError(
            {
                'code': BaseMsg.CODE_IS_EXISTS,
            }
        )

    term = serializers.CharField(help_text=TERM_HEP_TEXT)  # PaymentTermImportSubTermSerializer(many=True)

    @classmethod
    def validate_term(cls, value):
        try:
            term_data = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise serializers.ValidationError(
                {
                    'term': BaseMsg.FORMAT_NOT_MATCH,
                }
            )
        except Exception as err:
            print('[PaymentTermImportSerializer][validate_term] errors:', err)
            raise serializers.ValidationError(
                {
                    'term': BaseMsg.FORMAT_NOT_MATCH,
                }
            )

        if isinstance(term_data, list):
            if term_data:
                term_ser_data = []
                for index, item in enumerate(term_data):
                    if isinstance(item, list) and len(item) == 5:
                        term_ser_data.append(
                            {
                                'unit_type': item[0],
                                'value': item[1],
                                'day_type': item[2],
                                'no_of_days': item[3],
                                'after': item[4],
                                'order': index + 1,
                            }
                        )
                    else:
                        raise serializers.ValidationError(
                            {
                                'term': BaseMsg.FORMAT_NOT_MATCH,
                            }
                        )

                term_ser = PaymentTermImportSubTermSerializer(data=term_ser_data, many=True)
                term_ser.is_valid(raise_exception=True)

                return term_ser
            raise serializers.ValidationError(
                {
                    'term': BaseMsg.REQUIRED,
                }
            )
        raise serializers.ValidationError(
            {
                'term': BaseMsg.FORMAT_NOT_MATCH,
            }
        )

    def create(self, validated_data):
        term_ser = validated_data.pop('term')
        validated_data['term'] = [dict(item) for item in term_ser.validated_data]
        instance = PaymentTerm.objects.create(**validated_data)
        if term_ser:
            term_ser.save(payment_term=instance)
        return instance

    class Meta:
        model = PaymentTerm
        fields = (
            'title',
            'code',
            'apply_for',
            'remark',
            'term',
        )


class SalutationImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('id', 'title')


class SalutationImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if value:
            if Salutation.objects.filter_current(fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": BaseMsg.CODE_IS_EXISTS})
            return value
        raise serializers.ValidationError({"code": BaseMsg.REQUIRED})

    title = serializers.CharField(max_length=100)

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": BaseMsg.REQUIRED})

    description = serializers.CharField(max_length=200, allow_blank=True)

    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')


class SaleDataContactImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'title', 'code')


class SaleDataContactImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, attrs):
        if not Contact.objects.filter_current(fill__company=True, code=attrs).exists():
            return attrs
        raise serializers.ValidationError(
            {
                'code': BaseMsg.CODE_IS_EXISTS,
            }
        )

    owner = serializers.CharField(allow_null=True, allow_blank=True)

    @classmethod
    def validate_owner(cls, attrs):
        if attrs:
            try:
                return Employee.objects.get_current(fill__company=True, code=attrs)
            except Employee.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'owner': HrMsg.EMPLOYEE_NOT_FOUND
                    }
                )
        return None

    salutation = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)

    @classmethod
    def validate_salutation(cls, attrs):
        if attrs:
            try:
                return Salutation.objects.get_current(fill__company=True, code=attrs)
            except Salutation.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'salutation': BaseMsg.CODE_NOT_EXIST,
                    }
                )
        return None

    email = serializers.EmailField(max_length=150, allow_blank=True, allow_null=True)

    @classmethod
    def validate_email(cls, attrs):
        if attrs:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    mobile = serializers.CharField(max_length=25, allow_blank=True, allow_null=True)

    @classmethod
    def validate_mobile(cls, attrs):
        if attrs:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None

    report_to = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)

    @classmethod
    def validate_report_to(cls, attrs):
        if attrs:
            try:
                return Contact.objects.get_current(fill__company=True, code=attrs)
            except Contact.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'report_to': BaseMsg.CODE_NOT_EXIST
                    }
                )
        return None

    account_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)

    @classmethod
    def validate_account_name(cls, attrs):
        if attrs:
            try:
                return Account.objects.get_current(fill__company=True, code=attrs)
            except Account.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'account_name': BaseMsg.CODE_NOT_EXIST,
                    }
                )
        return None

    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        if contact.account_name:
            contact.account_name.owner = contact
            contact.account_name.save(update_fields=['owner'])
        return contact

    class Meta:
        model = Contact
        fields = (
            "code",
            "owner",
            "job_title",
            "biography",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            'account_name',
            # "address_information",
            # "additional_information",
            # 'work_detail_address',
            # 'work_country',
            # 'work_city',
            # 'work_district',
            # 'work_ward',
            # 'home_detail_address',
            # 'home_country',
            # 'home_city',
            # 'home_district',
            # 'home_ward',
        )


class SaleDataAccountImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'title', 'code')


# ['Tinh/ThanhPho', 'Quan/Huyen', 'Xa/Phuong', 'Address', 'Default'],
class AddressDictSerializer(serializers.Serializer):  # noqa
    city = serializers.CharField()
    district = serializers.CharField()
    ward = serializers.CharField()
    address = serializers.CharField()
    is_default = serializers.BooleanField(default=False)


class AddressListAbstractSerializer(serializers.Serializer):  # noqa
    data = AddressDictSerializer(many=True)
    KEY_RAISING = None

    def validate(self, validate_data):
        default_amount = 0
        for item in validate_data['data']:
            if item.get('is_default', False) is True:
                default_amount += 1

        if default_amount > 1:
            raise serializers.ValidationError({self.KEY_RAISING: AccountsMsg.ADDRESS_ONLY_ONE_DEFAULT})

        return validate_data


class ShippingAddressListSerializer(AddressListAbstractSerializer):  # noqa
    KEY_RAISING = 'shipping_address_dict'


class BillingAddressListSerializer(AddressListAbstractSerializer):  # noqa
    KEY_RAISING = 'billing_address_dict'


class SaleDataAccountImportSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)

    @classmethod
    def validate_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"name": AccountsMsg.NAME_NOT_NULL})

    code = serializers.CharField(max_length=150)

    @classmethod
    def validate_code(cls, value):
        if value:
            if not Account.objects.filter_current(fill__company=True, code=value).exists():
                return value
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True)

    @classmethod
    def validate_tax_code(cls, value):
        if Account.objects.filter_current(fill__tenant=True, fill__company=True, tax_code=value).exists():
            raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_IS_EXIST})
        return value

    account_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    @classmethod
    def validate_account_group(cls, value):
        if value:
            try:
                return AccountGroup.objects.get_current(fill__company=True, code=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"account_group": BaseMsg.CODE_NOT_EXIST})
        raise serializers.ValidationError({'account_group': BaseMsg.REQUIRED})

    account_type = serializers.CharField()

    @classmethod
    def validate_account_type(cls, value):
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(",")]))
            objs = AccountType.objects.filter_current(fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return [{
                    'id': str(item.id),
                    'title': str(item.title),
                    'code': str(item.code),
                } for item in objs]
            raise serializers.ValidationError({'account_types_mapped': BaseMsg.CODE_NOT_EXIST})
        raise serializers.ValidationError({'account_types_mapped': BaseMsg.REQUIRED})

    manager = serializers.CharField()

    @classmethod
    def validate_manager(cls, value):
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(",")]))
            objs = Employee.objects.filter_current(fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return [{
                    'id': str(item.id),
                    'code': str(item.code),
                    'full_name': str(item.get_full_name())
                } for item in objs]
            raise serializers.ValidationError({'manager': BaseMsg.CODE_NOT_EXIST})
        raise serializers.ValidationError({'manager': BaseMsg.REQUIRED})

    parent_account_mapped = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_parent_account_mapped(cls, value):
        if value:
            try:
                return Account.objects.get_current(fill__company=True, code=value)
            except Account.DoesNotExist:
                raise serializers.ValidationError({"parent_account_mapped": BaseMsg.CODE_NOT_EXIST})
        return None

    industry = serializers.CharField()

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get_current(fill__company=True, code=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        raise serializers.ValidationError({"industry": AccountsMsg.INDUSTRY_NOT_NULL})

    # shipping_address_dict = serializers.CharField(allow_null=True, allow_blank=True)

    @classmethod
    def validate_shipping_address_dict(cls, value):
        if value:
            # [
            #     ['Tinh/ThanhPho', 'Quan/Huyen', 'Xa/Phuong', 'Address', 'Default'],
            #     ['Tinh/ThanhPho', 'Quan/Huyen', 'Xa/Phuong', 'Address', 'Default'],
            # ]
            try:
                arr_data = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({'shipping_address_dict': BaseMsg.FORMAT_NOT_MATCH})
            except Exception:
                raise serializers.ValidationError({'shipping_address_dict': BaseMsg.FORMAT_NOT_MATCH})

            ser = ShippingAddressListSerializer(
                data={
                    'data': [
                        {
                            'city': item[0],
                            'district': item[1],
                            'ward': item[2],
                            'address': item[3],
                            'is_default': item[4] in ['1', 1],
                        } for item in arr_data
                    ]
                }
            )
            ser.is_valid(raise_exception=True)

            return [dict(item) for item in ser.validated_data['data']]
        return []

    # billing_address_dict = serializers.CharField()

    @classmethod
    def validate_billing_address_dict(cls, value):
        if value:
            # [
            #     ['Tinh/ThanhPho', 'Quan/Huyen', 'Xa/Phuong', 'Address', 'Default'],
            #     ['Tinh/ThanhPho', 'Quan/Huyen', 'Xa/Phuong', 'Address', 'Default'],
            # ]
            try:
                arr_data = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({'shipping_address_dict': BaseMsg.FORMAT_NOT_MATCH})
            except Exception:
                raise serializers.ValidationError({'shipping_address_dict': BaseMsg.FORMAT_NOT_MATCH})

            ser = BillingAddressListSerializer(
                data={
                    'data': [
                        {
                            'city': item[0],
                            'district': item[1],
                            'ward': item[2],
                            'address': item[3],
                            'is_default': item[4] in ['1', 1],
                        } for item in arr_data
                    ]
                }
            )
            ser.is_valid(raise_exception=True)

            return [dict(item) for item in ser.validated_data['data']]

        return []

    def validate(self, validate_data):
        try:
            validate_data['price_list_mapped'] = Price.objects.get_current(fill__company=True, is_default=True)
        except Price.DoesNotExist:
            raise serializers.ValidationError({"price_list_mapped": AccountsMsg.PRICE_LIST_DEFAULT_NOT_EXIST})

        try:
            validate_data['currency'] = Currency.objects.get_current(fill__company=True, is_primary=True)
        except Currency.DoesNotExist:
            raise serializers.ValidationError({"currency": AccountsMsg.CURRENCY_DEFAULT_NOT_EXIST})

        account_type_selection = validate_data.get('account_type_selection', None)
        tax_code = validate_data.get('tax_code', None)
        total_employees = validate_data.get('total_employees', None)
        if account_type_selection:
            if tax_code:
                raise serializers.ValidationError({"tax_code": AccountsMsg.TAX_CODE_NOT_NONE})
            if total_employees:
                raise serializers.ValidationError({"total_employees": AccountsMsg.TOTAL_EMPLOYEES_NOT_NONE})
        else:
            validate_data['tax_code'] = None
            validate_data['total_employees'] = None

        return validate_data

    contact_mapped = serializers.ListSerializer(
        child=serializers.ListSerializer(
            child=serializers.CharField(),
            min_length=2, max_length=2,
        ),
        allow_empty=True, allow_null=True,
    )

    @classmethod
    def item_valid_contact_mapped(cls, value) -> dict[str, any]:
        if value and isinstance(value, list) and len(value) == 2:
            result = {
                'contact': None,
                'is_account_owner': False,
            }

            if value[0]:
                try:
                    obj_contact = Contact.objects.get_current(fill__company=True, code=value[0])
                    result['contact'] = obj_contact
                except Contact.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            'contact_mapped': BaseMsg.CODE_NOT_EXIST,
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {
                        'contact_mapped': BaseMsg.CODE_NOT_EXIST,
                    }
                )

            if value[1]:
                if value[1] in [1, '1']:
                    result['is_account_owner'] = True
                elif value[1] in [0, '0']:
                    result['is_account_owner'] = False
                else:
                    raise serializers.ValidationError(
                        {
                            'contact_mapped': BaseMsg.FORMAT_NOT_MATCH,
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {
                        'contact_mapped': BaseMsg.CODE_NOT_EXIST,
                    }
                )

            return result
        raise serializers.ValidationError(
            {
                'contact_mapped': BaseMsg.REQUIRED,
            }
        )

    @classmethod
    def validate_contact_mapped(cls, value):
        validated_data = []
        if value:
            if isinstance(value, list):
                for item in value:
                    item_data = cls.item_valid_contact_mapped(item)
                    if isinstance(item_data, dict):
                        validated_data.append(item_data)
                    else:
                        raise serializers.ValidationError(
                            {
                                'contact_mapped': BaseMsg.FORMAT_NOT_MATCH
                            }
                        )
                counter_true = [
                    item['is_account_owner'] for item in validated_data
                ].count(True)
                if counter_true <= 1:
                    return validated_data
                raise serializers.ValidationError(
                    {
                        'contact_mapped': AccountsMsg.ACCOUNT_RELATE_ONLY_ONE_OWNER
                    }
                )
            raise serializers.ValidationError(
                {
                    'contact_mapped': BaseMsg.FORMAT_NOT_MATCH,
                }
            )
        return validated_data

    def create(self, validated_data):
        contact_mapped = validated_data.pop('contact_mapped', [])
        shipping_address_dict = validated_data.pop('shipping_address_dict', [])
        billing_address_dict = validated_data.pop('billing_address_dict', [])

        account = Account.objects.create(**validated_data)

        create_employee_map_account(account)
        add_account_types_information(account)
        add_shipping_address_information(account, shipping_address_dict)
        add_billing_address_information(account, billing_address_dict)

        if contact_mapped:
            for item in contact_mapped:
                contact = item['contact']
                contact.is_primary = item['is_account_owner']
                contact.account_name = account
                contact.save()
                if item['is_account_owner']:
                    account.owner = contact
                    account.save()
        return account

    class Meta:
        model = Account
        fields = (
            'name',
            'code',
            'account_type',
            'account_group',
            'manager',
            'industry',
            'website',
            'phone',
            'email',
            'tax_code',
            'annual_revenue',
            'total_employees',
            'parent_account_mapped',
            'contact_mapped',
        )
