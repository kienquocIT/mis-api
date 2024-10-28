from unidecode import unidecode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.masterdata.saledata.models import Currency, Price
from apps.masterdata.saledata.models import UnitOfMeasure, UnitOfMeasureGroup, ProductType, Tax, TaxCategory
from apps.masterdata.saledata.models.product import Product, ProductCategory
from apps.masterdata.saledata.serializers import CommonCreateUpdateProduct, ProductCreateSerializer

PRODUCT_OPTION = [(0, _('Sale')), (1, _('Inventory')), (2, _('Purchase'))]


class ProductQuotationCreateSerializerLoadDB(serializers.ModelSerializer):
    quotation_product_import_data = serializers.DictField(required=True)
    create_new_list = serializers.ListField(required=False)
    get_old_list = serializers.ListField(required=False)

    class Meta:
        model = Product
        fields = ('quotation_product_import_data', 'create_new_list', 'get_old_list')

    @staticmethod
    def get_product_type(tenant, company, is_service):
        product_type = ProductType.objects.filter(
            tenant=tenant, company=company, is_service=True
        ).first() if is_service else ProductType.objects.filter(
            tenant=tenant, company=company, is_goods=True
        ).first()

        if not product_type:
            raise serializers.ValidationError({'product_type': _("Product type does not exist.")})
        return product_type

    @staticmethod
    def get_currency(tenant, company):
        currency = Currency.objects.filter(tenant=tenant, company=company, is_primary=True).first()
        if not currency:
            raise serializers.ValidationError({'product': _("Currency does not exist.")})
        return currency

    @staticmethod
    def get_uom_group(tenant, company):
        uom_group = UnitOfMeasureGroup.objects.filter(
            tenant=tenant, company=company, is_default=True, code='UG_import'
        ).first()
        if not uom_group:
            raise serializers.ValidationError({'uom_group': _("UOM group for import does not exist.")})
        return uom_group

    @staticmethod
    def get_tax_category(tenant, company):
        tax_category = TaxCategory.objects.filter(
            tenant=tenant, company=company, is_default=True, code='TC001'
        ).first()
        if not tax_category:
            raise serializers.ValidationError({'tax_category': _("Tax category does not exist.")})
        return tax_category

    @staticmethod
    def get_default_price_list(tenant, company):
        default_price_list = Price.objects.filter_current(tenant=tenant, company=company, is_default=True).first()
        if not default_price_list:
            raise serializers.ValidationError({'default_price_list': _("Default price list does not exisT.")})
        return default_price_list

    @staticmethod
    def get_product_category(tenant, company, product_category, create_new_list, get_old_list):
        value_format = unidecode(product_category if product_category else '').lower()
        product_category = None
        for item in ProductCategory.objects.filter(tenant=tenant, company=company):
            if any([unidecode(item.code).lower() == value_format, unidecode(item.title).lower() in value_format]):
                product_category = item
                break
        if not product_category:
            if 'product_category' not in create_new_list:
                raise serializers.ValidationError({'product_category': _("This category does not exist.")})
        else:
            if 'product_category' not in get_old_list:
                if 'product_category' not in create_new_list:
                    raise serializers.ValidationError({'product_category': _("This category may be already exist.")})
                product_category = None
        return product_category

    @staticmethod
    def get_uom(tenant, company, uom, create_new_list, get_old_list):
        value_format = unidecode(uom if uom else '').lower()
        uom = None
        for item in UnitOfMeasure.objects.filter(tenant=tenant, company=company):
            if any([unidecode(item.code).lower() == value_format, unidecode(item.title).lower() in value_format]):
                uom = item
                break
        if not uom:
            if 'uom' not in create_new_list:
                raise serializers.ValidationError({'uom': _("This uom does not exist.")})
        else:
            if 'uom' not in get_old_list:
                if 'uom' not in create_new_list:
                    raise serializers.ValidationError({'uom': _("This uom may be already exist.")})
                uom = None
        return uom

    @staticmethod
    def get_tax(tenant, company, tax_percent, create_new_list, get_old_list):
        tax = None
        if tax_percent:
            for item in Tax.objects.filter(tenant=tenant, company=company):
                if item.rate == float(tax_percent if tax_percent else 0):
                    tax = item
                    break
            if not tax:
                if 'tax_percent' not in create_new_list:
                    raise serializers.ValidationError({'tax': _("This tax does not exist.")})
            else:
                if 'tax_percent' not in get_old_list:
                    if 'tax_percent' not in create_new_list:
                        raise serializers.ValidationError({'tax_percent': _("This tax may be already exist.")})
                    tax = None
        return tax

    @classmethod
    def get_product(cls, tenant, company, product_code, product_title):
        code_format = unidecode(product_code if product_code else '').lower()
        title_format = unidecode(product_title).lower()
        product_obj = None
        for item in Product.objects.filter(tenant=tenant, company=company):
            if any([unidecode(item.code).lower() == code_format, unidecode(item.title).lower() in title_format]):
                product_obj = item
                break
        return product_obj

    def validate(self, validate_data):
        import_data = validate_data.get('quotation_product_import_data', {})
        create_new_list = validate_data.get('create_new_list', [])
        get_old_list = validate_data.get('get_old_list', [])
        required_keys = ['product_title', 'product_category', 'uom']
        missing_keys = [key for key in required_keys if key not in import_data]
        if missing_keys:
            raise serializers.ValidationError({key: _(f"{key} is required.") for key in missing_keys})

        tenant = self.context.get('tenant_current', None)
        company = self.context.get('company_current', None)
        employee = self.context.get('employee_current', None)

        product_obj = self.get_product(
            tenant, company, import_data.get('product_code'), import_data.get('product_title')
        )
        if not product_obj:
            if 'product_obj' not in create_new_list:
                raise serializers.ValidationError({'product_obj': _("This product does not exist.")})
        else:
            if 'product_obj' not in get_old_list:
                if 'product_obj' not in create_new_list:
                    raise serializers.ValidationError({'product_obj': _("This product may be already exist.")})
                product_obj = None

        if not product_obj:
            import_data['product_code'] = import_data.get('product_code') if import_data.get('product_code') else \
                f"PRD00{Product.objects.filter(tenant=tenant, company=company).count()}"
            ProductCreateSerializer.validate_code(import_data.get('product_code'))

        validate_data = {
            'tenant': tenant,
            'company': company,
            'employee': employee,

            'product_obj': product_obj,
            'product_category_obj': self.get_product_category(
                tenant, company, import_data.get('product_category'), create_new_list, get_old_list
            ),
            'uom_obj': self.get_uom(
                tenant, company, import_data.get('uom'), create_new_list, get_old_list
            ),
            'uom_group_obj': self.get_uom_group(tenant, company),
            'product_type_obj': self.get_product_type(tenant, company, import_data.get('is_service')),
            'currency_obj': self.get_currency(tenant, company),
            'tax_obj': self.get_tax(tenant, company, import_data.get('tax_percent'), create_new_list, get_old_list),
            'tax_category_obj': self.get_tax_category(tenant, company),

            'product_code': import_data.get('product_code'),
            'product_title': import_data.get('product_title'),
            'product_description': import_data.get('product_description'),
            'product_category': import_data.get('product_category'),
            'is_service': import_data.get('is_service'),
            'uom': import_data.get('uom'),
            'quantity': import_data.get('quantity', 0),
            'unit_price': import_data.get('unit_price', 0),
            'discount_percent': import_data.get('discount_percent', 0),
            'tax_percent': import_data.get('tax_percent'),
        }
        return validate_data

    def create(self, validated_data):
        tenant = validated_data.get('tenant')
        company = validated_data.get('company')
        employee = validated_data.get('employee')

        product_category_obj = validated_data.get('product_category_obj')
        if not product_category_obj:
            product_category_obj = ProductCategory.objects.create(
                tenant=tenant,
                company=company,
                employee_created=employee,
                code=f"PC00{ProductCategory.objects.filter(tenant=tenant, company=company).count()}",
                title=validated_data.get('product_category'),
            )

        uom_obj = validated_data.get('uom_obj')
        if not uom_obj:
            uom_obj = UnitOfMeasure.objects.create(
                tenant=tenant,
                company=company,
                employee_created=employee,
                code=f"UOM00{UnitOfMeasure.objects.filter(tenant=tenant, company=company).count()}",
                title=validated_data.get('uom'),
                group=validated_data.get('uom_group_obj'),
            )

        tax_obj = validated_data.get('tax_obj')
        if not tax_obj and validated_data.get('tax_percent'):
            tax_obj = Tax.objects.create(
                tenant=tenant,
                company=company,
                employee_created=employee,
                code=f"VAT-{validated_data.get('tax_percent')}",
                title=f"VAT-{validated_data.get('tax_percent')}",
                rate=validated_data.get('tax_percent'),
                category=validated_data.get('tax_category_obj'),
                tax_type=2
            )

        product_obj = validated_data.get('product_obj')
        product_type_obj = validated_data.get('product_type_obj')
        currency_obj = validated_data.get('currency_obj')
        if not product_obj:
            product_obj = Product.objects.create(
                tenant=tenant,
                company=company,
                employee_created=employee,
                employee_inherit=employee,
                code=validated_data.get('product_code'),
                title=validated_data.get('product_title'),
                description=validated_data.get('product_description'),
                product_choice=[0, 1, 2] if product_type_obj.is_goods else [0, 2],
                general_product_category=product_category_obj,
                general_uom_group=uom_obj.group,
                general_traceability_method=0,
                sale_default_uom=uom_obj,
                sale_tax=tax_obj,
                sale_currency_using=currency_obj,
                inventory_uom=uom_obj if product_type_obj.is_goods else None,
                purchase_default_uom=uom_obj,
                purchase_tax=tax_obj,
                supplied_by=0
            )

            CommonCreateUpdateProduct.create_product_types_mapped(
                product_obj,
                [str(product_type_obj.id)]
            )

            price_list_product_data = CommonCreateUpdateProduct.create_price_list_product(
                product_obj,
                self.get_default_price_list(tenant, company)
            )
            product_obj.sale_product_price_list = price_list_product_data
            product_obj.save(update_fields=['sale_product_price_list'])

        subtotal_price = float(validated_data.get('quantity', 0)) * float(validated_data.get('unit_price', 0))
        product_obj.import_data_row = {
            'product': {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title,
                'description': product_obj.description,
            } if product_obj else {},
            'product_category': {
                'id': str(product_obj.general_product_category_id),
                'code': product_obj.general_product_category.code,
                'title': product_obj.general_product_category.title
            } if product_obj.general_product_category else {},
            'uom': {
                'id': str(uom_obj.id),
                'code': uom_obj.code,
                'title': uom_obj.title,
                'uom_group': {
                    'id': str(uom_obj.group_id),
                    'title': uom_obj.group.title
                } if uom_obj.group else {}
            } if uom_obj else {},
            'quantity': validated_data.get('quantity', 0),
            'unit_price': validated_data.get('unit_price', 0),
            'subtotal_price': subtotal_price,
            'discount_percent': validated_data.get('discount_percent', 0),
            'discount_value': float(validated_data.get('discount_percent', 0)) * subtotal_price,
            'tax': {
                'id': str(tax_obj.id),
                'code': tax_obj.code,
                'title': tax_obj.title,
                'rate': tax_obj.rate
            } if tax_obj else {},
            'tax_value': float(tax_obj.rate) * subtotal_price if tax_obj else 0,
        }
        product_obj.save(update_fields=['import_data_row'])
        return product_obj


class ProductQuotationDetailSerializerLoadDB(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'code', 'title', 'import_data_row')
