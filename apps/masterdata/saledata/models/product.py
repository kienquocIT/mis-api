import logging
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.storages.aws.storages_backend import PublicMediaStorage
from apps.masterdata.saledata.models.periods import Periods
from apps.masterdata.saledata.models.inventory import WareHouse
from apps.masterdata.saledata.utils import ProductHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel, DisperseModel, SERIAL_STATUS


__all__ = [
    'ProductType', 'ProductCategory', 'UnitOfMeasureGroup', 'UnitOfMeasure', 'Product', 'Expense',
    'ExpensePrice', 'ExpenseRole', 'ProductMeasurements', 'ProductProductType',
    'ProductVariantAttribute', 'ProductVariant', 'Manufacturer', 'ProductComponent',
    'ProductSpecificIdentificationSerialNumber'
]


TRACEABILITY_METHOD_SELECTION = [
    (0, _('None')),
    (1, _('Batch/Lot number')),
    (2, _('Serial number'))
]


SUPPLIED_BY = [
    (0, _('Purchasing')),
    (1, _('Making')),
]


ATTRIBUTE_CONFIG = [
    (0, _('Dropdown List')),
    (1, _('Radio Select')),
    (2, _('Select (Fill by text)')),
    (3, _('Select (Fill by color)')),
    (4, _('Select (Fill by photo)'))
]


VALUATION_METHOD = [
    (0, _('FIFO')),
    (1, _('Weighted average')),
    (2, _('Specific identification'))
]


logger = logging.getLogger(__name__)


def generate_product_avatar_path(instance, filename):
    def get_ext():
        return filename.split(".")[-1].lower()

    if instance.id:
        company_path = str(instance.company_id).replace('-', '')
        product_id = str(instance.id).replace('-', '')
        return f"{company_path}/product/avatar/{product_id}.{get_ext()}"
    raise ValueError('Attachment require product related')


# Create your models here.
class ProductType(MasterDataAbstractModel):  # noqa
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    is_goods = models.BooleanField(
        default=False, help_text='flag to know this type is goods (purchased) of company'
    )
    is_finished_goods = models.BooleanField(
        default=False, help_text='flag to know this type is finished goods (production) of company'
    )
    is_material = models.BooleanField(
        default=False, help_text='flag to know this type is material of company'
    )
    is_tool = models.BooleanField(
        default=False, help_text='flag to know this type is tool of company'
    )
    is_service = models.BooleanField(
        default=False, help_text='flag to know this type is service of company'
    )

    class Meta:
        verbose_name = 'ProductType'
        verbose_name_plural = 'ProductTypes'
        ordering = ('-is_default', 'date_created',)
        default_permissions = ()
        permissions = ()


class ProductCategory(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ProductCategory'
        verbose_name_plural = 'ProductCategories'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class UnitOfMeasureGroup(MasterDataAbstractModel):
    is_default = models.BooleanField(default=False)
    uom_reference = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom reference",
        help_text="unit of measure in this group which is reference",
        related_name="uom_group_uom_reference",
        null=True
    )

    class Meta:
        verbose_name = 'UnitOfMeasureGroup'
        verbose_name_plural = 'UnitsOfMeasureGroup'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class UnitOfMeasure(MasterDataAbstractModel):
    group = models.ForeignKey(
        UnitOfMeasureGroup,
        verbose_name='unit of measure group',
        on_delete=models.CASCADE,
        null=False,
        related_name='unitofmeasure_group'
    )
    ratio = models.FloatField(default=1.0)
    rounding = models.IntegerField(default=4)
    is_referenced_unit = models.BooleanField(default=False, help_text='UoM Group Referenced Unit')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'UnitOfMeasure'
        verbose_name_plural = 'UnitsOfMeasure'
        ordering = ('-group',)
        default_permissions = ()
        permissions = ()


class Manufacturer(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturers'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class Product(DataAbstractModel):
    title = models.TextField(blank=True)
    # import in quotation
    create_from_import = models.BooleanField(default=False)
    import_data_row = models.JSONField(default=dict)
    #
    has_bom = models.BooleanField(default=False)
    bom_data = models.JSONField(default=dict)
    # bom_data = {
    #     id: uuid,
    #     code: str,
    #     title: str,
    #     bom_type: int,
    #     for_outsourcing: bool,
    #     sum_price: float,
    #     sum_time: float,
    #     opp_data: dict
    # }
    part_number = models.CharField(max_length=150, null=True, blank=True)
    product_choice = models.JSONField(
        default=list,
        help_text='product for sale: 0, inventory: 1, purchase: 2'
    )
    description = models.TextField(blank=True)

    warehouses = models.ManyToManyField(
        'saledata.WareHouse',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='warehouses_of_product'
    )

    price_list = models.ManyToManyField(
        'saledata.Price',
        through='ProductPriceList',
        symmetrical=False,
        blank=True,
        related_name='product_map_price'
    )

    # General
    general_product_types_mapped = models.ManyToManyField(
        ProductType,
        through='ProductProductType',
        symmetrical=False,
        blank=True,
        related_name='product_map_product_types'
    )
    general_product_category = models.ForeignKey(
        ProductCategory,
        null=True,
        on_delete=models.CASCADE,
        related_name='product_category'
    )
    general_product_category_data = models.JSONField(default=dict)
    general_uom_group = models.ForeignKey(
        UnitOfMeasureGroup,
        null=True,
        on_delete=models.CASCADE,
        related_name='uom_group'
    )
    general_uom_group_data = models.JSONField(default=dict)
    general_manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        on_delete=models.CASCADE,
        related_name='manufacturer'
    )
    general_manufacturer_data = models.JSONField(default=dict)
    general_traceability_method = models.SmallIntegerField(choices=TRACEABILITY_METHOD_SELECTION, default=0)
    standard_price = models.FloatField(default=0, help_text="Standard price for BOM")

    width = models.FloatField(null=True)
    height = models.FloatField(null=True)
    length = models.FloatField(null=True)
    volume = models.JSONField(default=dict)
    weight = models.JSONField(default=dict)

    representative_product = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='product_representative_product'
    )
    is_representative_product = models.BooleanField(default=False)

    # Sale
    sale_default_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_default_uom'
    )
    sale_default_uom_data = models.JSONField(default=dict)
    sale_tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_tax'
    )
    sale_tax_data = models.JSONField(default=dict)
    sale_currency_using = models.ForeignKey(
        'saledata.Currency',
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_currency_using_for_cost'
    )
    sale_currency_using_data = models.JSONField(default=dict)
    sale_price = models.FloatField(default=0, help_text="General price in General price list")
    sale_product_price_list = models.JSONField(default=list)

    # Inventory
    inventory_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='inventory_uom'
    )
    inventory_uom_data = models.JSONField(default=dict)
    inventory_level_min = models.IntegerField(null=True)
    inventory_level_max = models.IntegerField(null=True)
    valuation_method = models.SmallIntegerField(choices=VALUATION_METHOD, default=1)

    # Purchase
    purchase_default_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='purchase_default_uom'
    )
    purchase_default_uom_data = models.JSONField(default=dict)
    purchase_tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.CASCADE,
        related_name='purchase_tax'
    )
    purchase_tax_data = models.JSONField(default=dict)
    supplied_by = models.SmallIntegerField(choices=SUPPLIED_BY, default=0)

    # Stock information
    stock_amount = models.FloatField(
        default=0,
        verbose_name="Stock Amount",
        help_text="Total physical amount product in all warehouse",
    )
    wait_delivery_amount = models.FloatField(
        default=0,
        verbose_name='Wait Delivery Amount',
        help_text='Amount product that ordered but not delivered, update when delivery for sale order'
    )
    wait_receipt_amount = models.FloatField(
        default=0,
        verbose_name='Wait Receipt Amount',
        help_text='Amount product that purchased but not receipted, update when goods receipt for purchase order'
    )
    production_amount = models.FloatField(
        default=0,
        verbose_name='Production Amount',
        help_text='Amount product that making by company - not purchase'
    )
    available_amount = models.FloatField(
        default=0,
        verbose_name='Available Stock',
        help_text='Theoretical amount product in warehouse, =(stock_amount - wait_delivery + wait_receipt)'
    )

    is_public_website = models.BooleanField(default=False)
    online_price_list = models.ForeignKey(
        'saledata.Price',
        null=True,
        on_delete=models.CASCADE,
        related_name='online_price_list'
    )
    online_price_list_data = models.JSONField(default=dict)
    available_notify = models.BooleanField(default=False)
    available_notify_quantity = models.IntegerField(null=True)
    account_deter_referenced_by = models.SmallIntegerField(
        choices=[(0, _('Warehouse')), (1, _('Product type')), (2, _('This product'))],
        default=0
    )

    # product attribute
    duration_unit = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.SET_NULL,
        related_name='duration_unit_uom'
    )
    duration_unit_data = models.JSONField(default=dict)

    # for Variants

    # image
    avatar_img = models.ImageField(
        storage=PublicMediaStorage, upload_to=generate_product_avatar_path, null=True,
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def is_used_in_other_model(self):
        """
            Kiểm tra sản phẩm đã được sử dụng bởi các model liên kết hay chưa.
            Trả về True nếu có, False nếu không.
        """
        ignore_models = {
            'productproducttype',
            'productuomgroup',
            'price',
            'productpricelist',
            'productcomponent'
        }

        related_fields = self._meta.get_fields()
        used_models = set()

        for field in related_fields:
            if field.is_relation and field.auto_created and not field.concrete:
                related_name = field.get_accessor_name()
                related_manager = getattr(self, related_name)
                if related_manager.exists():
                    first_record = related_manager.first()
                    if first_record:
                        used_models.add(first_record._meta.model_name)

        # Nếu có ít nhất một model liên kết không nằm trong danh sách bỏ qua => đang được sử dụng
        return any(model not in ignore_models for model in used_models)

    def is_used_in_inventory_activities(self, warehouse_obj):
        """
            Kiểm tra sản phẩm đã có hoạt động kho hay chưa.
            Trả về True nếu có, False nếu không.
        """
        # Nếu QL tồn kho theo project thì warehouse = None
        if hasattr(self.company, 'company_config'):
            if self.company.company_config.cost_per_project:
                warehouse_obj = None
        report_stock_log_model = DisperseModel(app_model='report.ReportStockLog').get_model()
        return report_stock_log_model.objects.filter(
            tenant=self.tenant, company=self.company, product=self, warehouse=warehouse_obj
        ).exclude(trans_title='Balance init input').exists()

    def get_current_cost_info(self, get_type=1, **kwargs):
        """
            Hàm lấy thông tin giá cost sản phẩm
            * param 'get_type':
                0: quantity
                1: cost (default)
                2: value
                3: [quantity, cost, value]
                else: 0
        """
        company_config = getattr(self.company, 'company_config')
        if company_config.cost_per_warehouse and 'warehouse_id' in kwargs:
            return self.get_cost_info_by_warehouse(kwargs.get('warehouse_id'), get_type=get_type)
        if company_config.cost_per_project and 'sale_order_id' in kwargs:
            return self.get_cost_info_by_project(kwargs.get('sale_order_id'), get_type=get_type)
        return 0

    def get_cost_info_by_warehouse(self, warehouse_id, get_type=1):
        """
            Hàm lấy thông tin giá cost sản phẩm theo từng kho
            * param 'get_type':
                0: quantity
                1: cost (default)
                2: value
                3: [quantity, cost, value]
                else: 0
        """
        this_period = Periods.get_current_period(self.tenant_id, self.company_id)
        if this_period:
            latest_trans = self.rp_inv_cost_product.filter(warehouse_id=warehouse_id).first()
            company_config = getattr(self.company, 'company_config')
            if latest_trans:
                if company_config.definition_inventory_valuation == 0:
                    value_list = [
                        latest_trans.latest_log.perpetual_current_quantity,
                        latest_trans.latest_log.perpetual_current_cost,
                        latest_trans.latest_log.perpetual_current_value
                    ]
                else:
                    opening_value_list_obj = self.report_inventory_cost_product.filter(
                        warehouse_id=warehouse_id, period_mapped=this_period,
                    ).first()
                    if opening_value_list_obj:
                        value_list = [
                            opening_value_list_obj.opening_balance_quantity,
                            opening_value_list_obj.opening_balance_cost,
                            opening_value_list_obj.opening_balance_value
                        ] if not opening_value_list_obj.periodic_closed else [
                            opening_value_list_obj.periodic_ending_balance_quantity,
                            opening_value_list_obj.periodic_ending_balance_cost,
                            opening_value_list_obj.periodic_ending_balance_value
                        ]
                    else:
                        value_list = [0, 0, 0]
            else:
                # lấy SDDK, nếu cũng không có SDDK, trả về [0, 0, 0]
                opening_value_list_obj = self.report_inventory_cost_product.filter(
                    warehouse_id=warehouse_id, period_mapped=this_period, for_balance_init=True
                ).first()
                value_list = [
                    opening_value_list_obj.opening_balance_quantity,
                    opening_value_list_obj.opening_balance_cost,
                    opening_value_list_obj.opening_balance_value
                ] if opening_value_list_obj else [0, 0, 0]
            if get_type != 3:
                return value_list[get_type]
            return value_list
        return 0

    def get_cost_info_by_project(self, sale_order_id, get_type=1):
        """
            Hàm lấy thông tin giá cost sản phẩm theo từng dự án
            * param 'get_type':
                0: quantity
                1: cost (default)
                2: value
                3: [quantity, cost, value]
                else: 0
        """
        this_period = Periods.get_current_period(self.tenant_id, self.company_id)
        if this_period:
            latest_trans = self.rp_inv_cost_product.filter(sale_order_id=sale_order_id).first()
            company_config = getattr(self.company, 'company_config')
            if latest_trans:
                if company_config.definition_inventory_valuation == 0:
                    value_list = [
                        latest_trans.latest_log.perpetual_current_quantity,
                        latest_trans.latest_log.perpetual_current_cost,
                        latest_trans.latest_log.perpetual_current_value
                    ]
                else:
                    opening_value_list_obj = self.report_inventory_cost_product.filter(
                        sale_order_id=sale_order_id, period_mapped=this_period,
                    ).first()
                    if opening_value_list_obj:
                        value_list = [
                            opening_value_list_obj.opening_balance_quantity,
                            opening_value_list_obj.opening_balance_cost,
                            opening_value_list_obj.opening_balance_value
                        ] if not opening_value_list_obj.periodic_closed else [
                            opening_value_list_obj.periodic_ending_balance_quantity,
                            opening_value_list_obj.periodic_ending_balance_cost,
                            opening_value_list_obj.periodic_ending_balance_value
                        ]
                    else:
                        value_list = [0, 0, 0]
            else:
                opening_value_list_obj = self.report_inventory_cost_product.filter(
                    sale_order_id=sale_order_id, period_mapped=this_period, for_balance_init=True
                ).first()
                value_list = [
                    opening_value_list_obj.opening_balance_quantity,
                    opening_value_list_obj.opening_balance_cost,
                    opening_value_list_obj.opening_balance_value
                ] if opening_value_list_obj else [0, 0, 0]
            if get_type != 3:
                return value_list[get_type]
            return value_list
        return 0

    def get_cost_info_of_all_warehouse(self):
        unit_cost_list = []
        warehouse_list = WareHouse.objects.filter_on_company()
        this_period = Periods.get_current_period(self.tenant_id, self.company_id)
        if this_period:
            sub_period_order = timezone.now().month - this_period.space_month
            company_config = getattr(self.company, 'company_config')
            for warehouse in warehouse_list:
                latest_trans = self.rp_inv_cost_product.filter(warehouse_id=warehouse.id).first()
                if latest_trans:
                    if company_config.definition_inventory_valuation == 0 and \
                            latest_trans.latest_log.perpetual_current_quantity > 0:
                        unit_cost_list.append({
                            'warehouse': {'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title},
                            'quantity': latest_trans.latest_log.perpetual_current_quantity,
                            'unit_cost': latest_trans.latest_log.perpetual_current_cost,
                            'value': latest_trans.latest_log.perpetual_current_value,
                        })
                else:
                    opening_value_list_obj = self.report_inventory_cost_product.filter(
                        warehouse_id=warehouse.id, period_mapped=this_period, sub_period_order=sub_period_order
                    ).first()
                    if opening_value_list_obj and opening_value_list_obj.opening_balance_quantity > 0:
                        unit_cost_list.append({
                            'warehouse': {'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title},
                            'quantity': opening_value_list_obj.opening_balance_quantity,
                            'unit_cost': opening_value_list_obj.opening_balance_cost,
                            'value': opening_value_list_obj.opening_balance_value,
                        })
        return unit_cost_list

    def get_product_account_deter_sub_data(self, account_deter_foreign_title, warehouse_id=None):
        """
            Lấy danh sách TK kế toán được xác định cho Sản Phẩm này:
            - Luôn luôn truyền account_deter_title: str
            - Nếu tham chiếu theo Kho (0): cần truyền 'warehouse_id'
            - Nếu tham chiếu theo Loại SP (1): không cần truyền tham số gì, tự động lấy theo product type của SP
            - Nếu xác định theo chính SP đó (2): không cần truyền tham số gì, tự động lấy theo SP
            Returns: obj hoặc None nếu không tìm thấy dữ liệu
        """
        account_deter_referenced_by = self.account_deter_referenced_by
        if account_deter_foreign_title:
            if account_deter_referenced_by == 0:
                warehouse_obj = WareHouse.objects.filter(id=warehouse_id).first()
                if warehouse_obj:
                    account_deter = warehouse_obj.wh_account_deter_warehouse_mapped.filter(
                        foreign_title=account_deter_foreign_title
                    ).first()
                    if account_deter:
                        return [item.account_mapped for item in account_deter.wh_account_deter_sub.all()]
                logger.error(msg='Get account deter by warehouse, but no warehouse found!')
            elif account_deter_referenced_by == 1:
                prd_type_list = self.general_product_types_mapped.all()
                if prd_type_list.count() == 1:
                    prd_type_obj = prd_type_list.first()
                    account_deter = prd_type_obj.prd_type_account_deter_product_type_mapped.filter(
                        foreign_title=account_deter_foreign_title
                    ).first()
                    if account_deter:
                        return [item.account_mapped for item in account_deter.prd_type_account_deter_sub.all()]
                logger.error(msg='Get account deter by product type, but there are more than 1 product type found!')
            elif account_deter_referenced_by == 2:
                account_deter = self.prd_account_deter_product_mapped.filter(
                    foreign_title=account_deter_foreign_title
                ).first()
                if account_deter:
                    return [item.account_mapped for item in account_deter.prd_account_deter_sub.all()]
        return []

    def save(self, *args, **kwargs):
        if 'update_stock_info' in kwargs:
            result = ProductHandler.update_stock_info(self, **kwargs)
            kwargs = result
        # hit DB
        super().save(*args, **kwargs)


class Expense(MasterDataAbstractModel):  # Internal Labor Item
    uom_group = models.ForeignKey(
        UnitOfMeasureGroup,
        verbose_name='Unit of Measure Group apply for expense',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_uom_group'
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        verbose_name='Unit of Measure apply for expense',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_uom'
    )
    price_list = models.ManyToManyField(
        'saledata.Price',
        through="ExpensePrice",
        symmetrical=False,
        blank=True,
        related_name='expenses_map_prices',
        default=None,
    )
    role = models.ManyToManyField(
        'hr.Role',
        through="ExpenseRole",
        symmetrical=False,
        blank=True,
        related_name='expenses_map_roles',
        default=None,
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="expense_expense_item",
        null=True
    )

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("S")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'S0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'S{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code(self.company_id)

        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ExpensePrice(SimpleAbstractModel):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='expense',
        null=True,
    )

    price = models.ForeignKey(
        'saledata.Price',
        on_delete=models.CASCADE,
    )
    currency = models.ForeignKey(
        'saledata.Currency',
        verbose_name='Currency using for expense in price list',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_price_currency',
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_price_uom'
    )
    is_auto_update = models.BooleanField(default=False)
    price_value = models.FloatField()

    class Meta:
        verbose_name = 'Expense Price'
        verbose_name_plural = 'Expense Prices'
        default_permissions = ()
        permissions = ()


class ExpenseRole(SimpleAbstractModel):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_role_expense'
    )
    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_role_role'
    )

    class Meta:
        verbose_name = 'Expense Role'
        verbose_name_plural = 'Expense Roles'
        default_permissions = ()
        permissions = ()


class ProductMeasurements(SimpleAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_measure'
    )
    measure = models.ForeignKey(
        'base.BaseItemUnit',
        on_delete=models.CASCADE,
        related_name="product_volume",
        limit_choices_to={'title__in': ['volume', 'weight']}
    )
    value = models.FloatField()


class ProductProductType(SimpleAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_product_types'
    )
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product ProductTypes'
        verbose_name_plural = 'Products ProductTypes'
        default_permissions = ()
        permissions = ()


class ProductVariantAttribute(SimpleAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_variant_attributes',
    )
    attribute_title = models.CharField(null=False, max_length=100)
    # attribute_value_list = [{
    # 'value': 'white',
    # 'color': '#ffffff',
    # }]
    attribute_value_list = models.JSONField(default=list)
    attribute_config = models.SmallIntegerField(choices=ATTRIBUTE_CONFIG)

    class Meta:
        verbose_name = 'Product ProductVariantAttribute'
        verbose_name_plural = 'Products ProductVariantAttributes'
        default_permissions = ()
        permissions = ()


class ProductVariant(MasterDataAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_variants'
    )
    # variant_value_list = ["green", "L"]
    variant_value_list = models.JSONField(default=list)
    variant_name = models.CharField(null=False, max_length=100)
    variant_des = models.CharField(null=False, max_length=100)
    variant_SKU = models.CharField(null=True, max_length=100)
    variant_extra_price = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Product ProductVariant'
        verbose_name_plural = 'Products ProductVariants'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class ProductComponent(MasterDataAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_components'
    )
    order = models.IntegerField(default=1)
    component_name = models.CharField(max_length=150, blank=True)
    component_des = models.CharField(max_length=500, blank=True)
    component_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Product Component'
        verbose_name_plural = 'Products Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ProductAttribute(MasterDataAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_attributes'
    )
    order = models.IntegerField(default=1)
    attribute = models.ForeignKey(
        'saledata.Attribute',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Products Attributes'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ProductSpecificIdentificationSerialNumber(MasterDataAbstractModel):
    """
    Model lưu trữ thông tin về giá của 1 serial quản lí tồn kho theo thực tế đích danh.
    Vì sản phẩm này được đính giá trị theo từng serial nên không phân biệt kho nào cả.
    chỉ đơn giản là mối quan hệ: product - serial number
    """
    product = models.ForeignKey(
        'saledata.Product', on_delete=models.CASCADE, related_name='product_si_serial_number',
    )
    product_warehouse_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial',
        on_delete=models.CASCADE,
        verbose_name="product warehouse serial",
        related_name="product_spec_product_warehouse_serial",
        null=True
    )
    vendor_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)
    warranty_start = models.DateTimeField(null=True)
    warranty_end = models.DateTimeField(null=True)
    # trường này lưu giá trị thực tế đích danh (PP này chỉ apply cho SP serial)
    specific_value = models.FloatField(default=0)
    serial_status = models.SmallIntegerField(choices=SERIAL_STATUS, default=0)
    from_pm = models.BooleanField(default=False)
    product_modification = models.ForeignKey(
        'productmodification.ProductModification',
        on_delete=models.CASCADE,
        related_name='product_si_pm',
        null=True,
    )

    @staticmethod
    def create_or_update_si_product_serial(
            product, serial_obj, specific_value, from_pm=False, product_modification=None
    ):
        """ Cập nhập hoặc tạo giá đich danh """
        si_serial_obj = ProductSpecificIdentificationSerialNumber.objects.filter(
            product=product,
            serial_number=serial_obj.serial_number
        ).first()
        if not si_serial_obj:
            ProductSpecificIdentificationSerialNumber.objects.create(
                product=product,
                product_warehouse_serial=serial_obj,
                vendor_serial_number=serial_obj.vendor_serial_number,
                serial_number=serial_obj.serial_number,
                expire_date=serial_obj.expire_date,
                manufacture_date=serial_obj.manufacture_date,
                warranty_start=serial_obj.warranty_start,
                warranty_end=serial_obj.warranty_end,
                specific_value=specific_value,
                from_pm=from_pm,
                product_modification=product_modification,
                employee_created=product.employee_created,
                tenant=product.tenant,
                company=product.company,
            )
            print(f"Created specific {serial_obj.serial_number} ({product.code}): value = {specific_value}")
        else:
            si_serial_obj.specific_value = specific_value
            si_serial_obj.save(update_fields=['specific_value'])
            print(f"Updated specific {serial_obj.serial_number} ({product.code}): value = {specific_value}")
        return True

    @staticmethod
    def get_specific_value(product, serial_number):
        """ Lấy giá đich danh """
        specific_value = 0
        si_product_serial_obj = ProductSpecificIdentificationSerialNumber.objects.filter(
            product=product, serial_number=serial_number
        ).first()
        if si_product_serial_obj:
            specific_value = si_product_serial_obj.specific_value
        return specific_value

    @staticmethod
    def on_off_specific_serial(product, serial_number, is_off=True):
        """ Tắt serial này nếu is_off===True else bật lại """
        si_product_serial_obj = ProductSpecificIdentificationSerialNumber.objects.filter(
            product=product, serial_number=serial_number
        ).first()
        if si_product_serial_obj:
            si_product_serial_obj.serial_status = is_off
            si_product_serial_obj.save(update_fields=['serial_status'])
        return True

    @classmethod
    def update_specific_value(cls, pw_serial):
        specific_obj = cls.objects.filter(product_warehouse_serial=pw_serial).first()
        if specific_obj:
            if specific_obj.product and pw_serial.goods_receipt:
                gr_product = specific_obj.product.goods_receipt_product_product.filter(
                    goods_receipt=pw_serial.goods_receipt
                ).first()
                if gr_product:
                    specific_obj.specific_value = gr_product.product_unit_price
                    specific_obj.save(update_fields=['specific_value'])
        return True

    class Meta:
        verbose_name = 'Product Specific Identification Serial'
        verbose_name_plural = 'Product Specific Identification Serials'
        ordering = ('serial_number',)
        default_permissions = ()
        permissions = ()
