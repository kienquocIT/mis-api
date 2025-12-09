from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.leaseorder.utils.logical import LOHandler
from apps.sales.leaseorder.utils.logical_finish import LOFinishHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SALE_ORDER_DELIVERY_STATUS, \
    BastionFieldAbstractModel, RecurrenceAbstractModel, ASSET_TYPE, PRODUCT_CONVERT_INTO, SimpleAbstractModel


# CONFIG
class LeaseOrderAppConfig(MasterDataAbstractModel):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='lease_order_app_config',
    )
    asset_type = models.ForeignKey(
        'saledata.FixedAssetClassification',
        on_delete=models.CASCADE,
        related_name="lease_config_asset_type",
        null=True
    )
    asset_type_data = models.JSONField(default=dict, help_text="data json of asset_type")
    asset_group_manage = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="lease_config_asset_group_manage",
        null=True
    )
    asset_group_manage_data = models.JSONField(default=dict, help_text="data json of asset_group_manage")
    asset_group_using = models.ManyToManyField(
        'hr.Group',
        through="LeaseOrderConfigAssetGroupUsing",
        symmetrical=False,
        blank=True,
        related_name='lo_config_map_asset_group_using'
    )
    asset_group_using_data = models.JSONField(default=list, help_text="data json of asset_group_using")
    tool_type = models.ForeignKey(
        'saledata.ToolClassification',
        on_delete=models.CASCADE,
        related_name="lease_config_tool_type",
        null=True
    )
    tool_type_data = models.JSONField(default=dict, help_text="data json of tool_type")
    tool_group_manage = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="lease_config_tool_group_manage",
        null=True
    )
    tool_group_manage_data = models.JSONField(default=dict, help_text="data json of tool_group_manage")
    tool_group_using = models.ManyToManyField(
        'hr.Group',
        through="LeaseOrderConfigToolGroupUsing",
        symmetrical=False,
        blank=True,
        related_name='lo_config_map_tool_group_using'
    )
    tool_group_using_data = models.JSONField(default=list, help_text="data json of tool_group_using")

    class Meta:
        verbose_name = 'Lease order Config'
        verbose_name_plural = 'Lease order Configs'
        default_permissions = ()
        permissions = ()


class LeaseOrderConfigAssetGroupUsing(SimpleAbstractModel):
    lease_order_config = models.ForeignKey(
        LeaseOrderAppConfig,
        on_delete=models.CASCADE,
        verbose_name="lease order config",
        related_name="lo_config_asset_group_using_lo_config",
    )
    group_using = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="group",
        related_name="lo_config_asset_group_using_group",
    )

    class Meta:
        verbose_name = 'Lease Order Config Asset Group Using'
        verbose_name_plural = 'Lease Order Config Asset Groups Using'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LeaseOrderConfigToolGroupUsing(SimpleAbstractModel):
    lease_order_config = models.ForeignKey(
        LeaseOrderAppConfig,
        on_delete=models.CASCADE,
        verbose_name="lease order config",
        related_name="lo_config_tool_group_using_lo_config",
    )
    group_using = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="group",
        related_name="lo_config_tool_group_using_group",
    )

    class Meta:
        verbose_name = 'Lease Order Config Tool Group Using'
        verbose_name_plural = 'Lease Order Config Tool Groups Using'
        ordering = ()
        default_permissions = ()
        permissions = ()


# BEGIN LEASE ORDER
class LeaseOrder(DataAbstractModel, BastionFieldAbstractModel, RecurrenceAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '010404b3-bb91-4b24-9538-075f5f00ef14'

    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="lease_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="lease_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    customer_data = models.JSONField(default=dict, help_text='data json of customer')
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="lease_contact",
        null=True
    )
    contact_data = models.JSONField(default=dict, help_text='data json of contact')
    sale_person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="sale person",
        related_name="lease_sale_person",
        null=True
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.CASCADE,
        verbose_name="payment term",
        related_name="lease_payment_term",
        null=True
    )
    payment_term_data = models.JSONField(
        default=dict,
        help_text="read data payment term, use for get list or detail sale order"
    )
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="lease_quotation",
        null=True
    )
    quotation_data = models.JSONField(default=dict, help_text='data json of quotation')
    lease_from = models.DateField(null=True)
    lease_to = models.DateField(null=True)
    # sale order tabs
    lease_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail sale order"
    )
    lease_logistic_data = models.JSONField(
        default=dict,
        help_text="read data logistics, use for get list or detail sale order"
    )
    customer_shipping = models.ForeignKey(
        'saledata.AccountShippingAddress',
        on_delete=models.SET_NULL,
        verbose_name="lease order shipping",
        related_name="lease_customer_shipping",
        null=True
    )
    customer_billing = models.ForeignKey(
        'saledata.AccountBillingAddress',
        on_delete=models.SET_NULL,
        verbose_name="lease order billing",
        related_name="lease_customer_billing",
        null=True
    )
    lease_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail lease order"
    )
    lease_costs_leased_data = models.JSONField(
        default=list,
        help_text="read data cost leased, use for get list or detail lease order"
    )
    lease_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail lease order"
    )
    lease_payment_stage = models.JSONField(
        default=list,
        help_text="read data payment stage, use for get list or detail lease order"
    )
    lease_invoice = models.JSONField(
        default=list,
        help_text="read data invoice, use for get list or detail lease order"
    )
    # total amount of products
    total_product_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab product")
    total_product_discount_rate = models.FloatField(default=0, help_text="total discount rate (%) of tab product")
    total_product_discount = models.FloatField(default=0, help_text="total discount of tab product")
    total_product_tax = models.FloatField(default=0, help_text="total tax of tab product")
    total_product = models.FloatField(default=0, help_text="total amount of tab product")
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
    )
    # total amount of costs
    total_cost_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab cost")
    total_cost_tax = models.FloatField(default=0, help_text="total tax of tab cost")
    total_cost = models.FloatField(default=0, help_text="total amount of tab cost")
    # total amount of expenses
    total_expense_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab expense")
    total_expense_tax = models.FloatField(default=0, help_text="total tax of tab expense")
    total_expense = models.FloatField(default=0, help_text="total amount of tab expense")
    delivery_call = models.BooleanField(
        default=False,
        verbose_name='Called delivery',
        help_text='State call delivery of this',
    )
    # sale order indicators
    lease_indicators_data = models.JSONField(
        default=list,
        help_text="read data indicators, use for get list or detail sale order, records in model SaleOrderIndicator"
    )
    indicator_revenue = models.FloatField(default=0, help_text="value of indicator revenue (IN0001)")
    indicator_gross_profit = models.FloatField(default=0, help_text="value of indicator gross profit (IN0003)")
    indicator_net_income = models.FloatField(default=0, help_text="value of indicator net income (IN0006)")
    # delivery status
    delivery_status = models.SmallIntegerField(choices=SALE_ORDER_DELIVERY_STATUS, default=0)
    has_regis = models.BooleanField(
        default=False,
        help_text='is True if linked with registration else False',
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='LeaseOrderAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_lease_order',
    )

    class Meta:
        verbose_name = 'Lease Order'
        verbose_name_plural = 'Lease Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_change_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        if not instance:
            return False
        return True

    @classmethod
    def check_reject_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        # check delivery (if LO was used for OrderDelivery => can't reject)
        if hasattr(instance, 'delivery_of_lease_order'):
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    LOFinishHandler.update_asset_status(instance=self)  # asset status => leased
                    LOFinishHandler.push_to_report_revenue(instance=self)  # reports
                    LOFinishHandler.push_to_report_customer(instance=self)
                    LOFinishHandler.push_to_report_lease(instance=self)

                    LOFinishHandler.push_final_acceptance_lo(instance=self)  # final acceptance
                    LOFinishHandler.push_to_payment_plan(instance=self)  # payment plan
                    LOFinishHandler.set_true_file_is_approved(instance=self)  # file
                    LOFinishHandler.update_recurrence_task(instance=self)  # recurrence

        if self.system_status in [4]:  # cancel
            ...
        # opportunity log
        LOHandler.push_opportunity_log(instance=self)
        # hit DB
        super().save(*args, **kwargs)


# SUPPORT PRODUCTS
class LeaseOrderProduct(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_product_lease_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset_type = models.SmallIntegerField(null=True, help_text='choices= ' + str(ASSET_TYPE))
    # offset = models.ForeignKey(
    #     'saledata.Product',
    #     on_delete=models.CASCADE,
    #     verbose_name="offset",
    #     related_name="lease_order_product_offset",
    #     null=True
    # )
    offset_data = models.JSONField(default=list, help_text='data json of offset')
    tool_data = models.JSONField(default=list, help_text='data json of tool')
    asset_data = models.JSONField(default=list, help_text='data json of asset')
    offset_show = models.TextField(verbose_name="offset show", blank=True)
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_product_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_product_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # product information
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_discount_value = models.FloatField(default=0)
    product_discount_amount = models.FloatField(default=0)
    product_discount_amount_total = models.FloatField(default=0)
    product_tax_title = models.CharField(max_length=100, blank=True, null=True)
    product_tax_value = models.FloatField(default=0)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_promotion = models.BooleanField(
        default=False,
        help_text="flag to know this product is for promotion (discount, gift,...)"
    )
    promotion = models.ForeignKey(
        'promotion.Promotion',
        on_delete=models.CASCADE,
        verbose_name="promotion",
        related_name="lease_order_product_promotion",
        null=True
    )
    promotion_data = models.JSONField(default=dict, help_text='data json of promotion')
    is_shipping = models.BooleanField(default=False, help_text="flag to know this product is for shipping fee")
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="lease_order_product_shipping",
        null=True
    )
    shipping_data = models.JSONField(default=dict, help_text='data json of shipping')
    remain_for_purchase_request = models.FloatField(default=0)
    remain_for_purchase_order = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not purchased order yet, update when PO finish"
    )
    is_group = models.BooleanField(default=False, help_text="flag to know product group not product")
    group_title = models.CharField(max_length=100, blank=True, null=True)
    group_order = models.IntegerField(default=1)
    quantity_wo_remain = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not work ordered yet, update when WO finish"
    )

    class Meta:
        verbose_name = 'Lease Order Product'
        verbose_name_plural = 'Lease Order Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class LeaseOrderProductOffset(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_product_offset_lease_order",
        null=True
    )
    lease_order_product = models.ForeignKey(
        LeaseOrderProduct,
        on_delete=models.CASCADE,
        verbose_name="lease order product",
        related_name="lease_order_product_offset_lo_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_offset_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    offset = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="offset",
        related_name="lease_order_product_offset_offset",
        null=True
    )
    offset_data = models.JSONField(default=dict, help_text='data json of offset')
    product_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Lease Order Product Offset'
        verbose_name_plural = 'Lease Order Products Offsets'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class LeaseOrderProductTool(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_product_tool_lease_order",
        null=True
    )
    lease_order_product = models.ForeignKey(
        LeaseOrderProduct,
        on_delete=models.CASCADE,
        verbose_name="lease order product",
        related_name="lease_order_product_tool_lo_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_tool_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="lease_order_product_tool_tool",
        null=True
    )
    tool_data = models.JSONField(default=dict, help_text='data json of tool')
    product_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Lease Order Product Tool'
        verbose_name_plural = 'Lease Order Products Tools'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class LeaseOrderProductAsset(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_product_asset_lease_order",
        null=True
    )
    lease_order_product = models.ForeignKey(
        LeaseOrderProduct,
        on_delete=models.CASCADE,
        verbose_name="lease order product",
        related_name="lease_order_product_asset_lo_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_asset_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        verbose_name="asset",
        related_name="lease_order_product_asset_asset",
        null=True
    )
    asset_data = models.JSONField(default=dict, help_text='data json of asset')
    product_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Lease Order Product Asset'
        verbose_name_plural = 'Lease Order Products Assets'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class LeaseOrderLogistic(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
    )
    shipping_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Lease Order Logistic'
        verbose_name_plural = 'Lease Order Logistics'
        default_permissions = ()
        permissions = ()


# SUPPORT COST
class LeaseOrderCost(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_cost_lease_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_cost_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset_type = models.SmallIntegerField(null=True, help_text='choices= ' + str(ASSET_TYPE))
    offset = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="offset",
        related_name="lease_order_cost_offset",
        null=True
    )
    offset_data = models.JSONField(default=dict, help_text='data json of offset')
    tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="lease_order_cost_tool",
        null=True
    )
    tool_data = models.JSONField(default=dict, help_text='data json of tool')
    asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        verbose_name="asset",
        related_name="lease_order_cost_asset",
        null=True
    )
    asset_data = models.JSONField(default=dict, help_text='data json of asset')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="lease_order_cost_warehouse",
        null=True
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="lease_order_cost_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="lease_order_cost_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_cost_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # cost information
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_cost_price = models.FloatField(default=0)
    product_tax_title = models.CharField(max_length=100, blank=True, null=True)
    product_tax_value = models.FloatField(default=0)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_shipping = models.BooleanField(default=False, help_text="flag to know this cost is for shipping fee")
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="lease_order_cost_shipping",
        null=True
    )
    shipping_data = models.JSONField(default=dict, help_text='data json of shipping')
    supplied_by = models.SmallIntegerField(default=0)  # (0: 'purchasing', 1: 'making')

    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')
    depreciation_lease_data = models.JSONField(default=list, help_text='data json of depreciation lease')

    product_convert_into = models.SmallIntegerField(choices=PRODUCT_CONVERT_INTO, null=True)
    asset_type_data = models.JSONField(default=dict, help_text="data json of asset_type")
    asset_group_manage_data = models.JSONField(default=dict, help_text="data json of asset_group_manage")
    asset_group_using_data = models.JSONField(default=list, help_text="data json of asset_group_using")
    tool_type_data = models.JSONField(default=dict, help_text="data json of tool_type")
    tool_group_manage_data = models.JSONField(default=dict, help_text="data json of tool_group_manage")
    tool_group_using_data = models.JSONField(default=list, help_text="data json of tool_group_using")

    # End depreciation fields

    class Meta:
        verbose_name = 'Lease Order Cost'
        verbose_name_plural = 'Lease Order Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class LeaseOrderExpense(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_expense_lease_order",
        null=True
    )
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        verbose_name="expense",
        related_name="lease_order_expense_expense",
        null=True
    )
    expense_data = models.JSONField(default=dict, help_text='data json of expense')
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="lease_order_expense_expense_item",
        null=True
    )
    expense_item_data = models.JSONField(default=dict, help_text='data json of expense_item')
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_expense_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_expense_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_expense_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # expense information
    expense_title = models.CharField(max_length=100, blank=True, null=True)
    expense_code = models.CharField(max_length=100, blank=True, null=True)
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    expense_type_title = models.CharField(max_length=100, blank=True, null=True)
    expense_uom_title = models.CharField(max_length=100, blank=True, null=True)
    expense_uom_code = models.CharField(max_length=100, blank=True, null=True)
    expense_quantity = models.FloatField(default=0)
    expense_price = models.FloatField(default=0)
    expense_tax_title = models.CharField(max_length=100, blank=True, null=True)
    expense_tax_value = models.FloatField(default=0)
    expense_tax_amount = models.FloatField(default=0)
    expense_subtotal_price = models.FloatField(default=0)
    expense_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_product = models.BooleanField(
        default=False,
        help_text='flag to check if record is MasterData Expense or Product, if True is Product'
    )
    is_labor = models.BooleanField(
        default=False,
        help_text="flag to check if record is MasterData Internal Labor Item (model Expense)"
    )

    class Meta:
        verbose_name = 'Lease Order Expense'
        verbose_name_plural = 'Lease Order Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT PAYMENT TERM STAGE
class LeaseOrderPaymentStage(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_payment_stage_lease_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    term = models.ForeignKey(
        'saledata.Term',
        on_delete=models.SET_NULL,
        verbose_name="payment term",
        related_name="lease_order_payment_stage_term",
        null=True
    )
    term_data = models.JSONField(default=dict)
    date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    date_type = models.CharField(max_length=200, blank=True)
    ratio = models.FloatField(null=True)
    invoice = models.IntegerField(null=True)
    invoice_data = models.JSONField(default=dict, help_text='data json of invoice')
    value_before_tax = models.FloatField(default=0)
    value_reconcile = models.FloatField(default=0)
    reconcile_data = models.JSONField(default=list, help_text='data json of reconcile')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_payment_stage_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    value_tax = models.FloatField(default=0)
    value_total = models.FloatField(default=0)
    is_ar_invoice = models.BooleanField(default=False)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Lease Order Payment Stage'
        verbose_name_plural = 'Lease Order Payment Stages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class LeaseOrderInvoice(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_invoice_lease_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    date = models.DateTimeField(null=True)
    term_data = models.JSONField(default=list, help_text='data json of terms')
    ratio = models.FloatField(null=True)
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_invoice_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    total = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Lease Order Invoice'
        verbose_name_plural = 'Lease Order Invoices'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class LeaseOrderAttachment(M2MFilesAbstractModel):
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_attachment_lease_order",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'lease_order'

    class Meta:
        verbose_name = 'Lease order attachment'
        verbose_name_plural = 'Lease order attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
