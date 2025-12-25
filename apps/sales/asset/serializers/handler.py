from apps.masterdata.saledata.models import Product, WareHouse, ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.apinvoice.models import APInvoiceItems, APInvoice
from apps.sales.asset.models.fixed_asset import FixedAssetInventoryItem, FixedAssetApInvoicePurchaseItem, \
    FixedAssetApInvoicePurchaseItemDetailProduct, FixedAssetCashOutPurchaseItem, FixedAssetDepreciation
from apps.sales.financialcashflow.models import CashOutflow


class CommonHandler:
    @classmethod
    def create_use_department(cls, instance, use_departments, use_department_model):
        bulk_data = []
        for use_department in use_departments:
            bulk_data.append(use_department_model(
                fixed_asset=instance,
                use_department=use_department,
            ))
        use_department_model.objects.bulk_create(bulk_data)


    @classmethod
    def create_source_detail(cls, instance, source_data):
        source_type = getattr(instance, 'source_type')

        # Route to appropriate handler based on source type
        if source_type == 0:
            cls._create_inventory_transfer_detail(instance, source_data)
        elif source_type == 1:
            ap_invoice_items = source_data.get('ap_invoice_items', [])
            cash_out_items = source_data.get('cash_out_items', [])
            cls._create_ap_invoice_purchase_detail(instance, ap_invoice_items)
            cls._create_cash_out_purchase_detail(instance, cash_out_items)

        # elif source_type == 2:
        #     cls._create_self_manufactured_detail(instance, source_data)
        # elif source_type == 3:
        #     cls._create_capital_construction_detail(instance, source_data)
        # elif source_type == 4:
        #     cls._create_donation_detail(instance, source_data)
        # elif source_type == 5:
        #     cls._create_capital_contribution_detail(instance, source_data)
        # else:
        #     logger.warning(f'Unknown source type: {source_type}')


    @staticmethod
    def _create_inventory_transfer_detail(instance, inventory_item_data):
        """Handle Transfer from Inventory (source_type=0)"""

        tracking_method = inventory_item_data.get('tracking_method')

        product_id = None
        if Product.objects.filter(id=inventory_item_data.get('product_id')).exists():
            product_id = Product.objects.filter(id=inventory_item_data.get('product_id')).first().id

        product_warehouse_serial_id = None
        product_warehouse_lot_id = None

        if int(tracking_method) == 1:
            if ProductWareHouseLot.objects.filter(id=inventory_item_data.get('product_warehouse_id')).exists():
                product_warehouse_lot_id = ProductWareHouseLot.objects.filter(
                    id=inventory_item_data.get('product_warehouse_id')).first().id

        if int(tracking_method) == 2:
            if ProductWareHouseSerial.objects.filter(id=inventory_item_data.get('product_warehouse_id')).exists():
                product_warehouse_serial_id = ProductWareHouseSerial.objects.filter(
                    id=inventory_item_data.get('product_warehouse_id')).first().id

        warehouse_id = None
        if WareHouse.objects.filter(id=inventory_item_data.get('warehouse_id')).exists():
            warehouse_id = WareHouse.objects.filter(id=inventory_item_data.get('warehouse_id')).first().id

        FixedAssetInventoryItem.objects.create(
            fixed_asset=instance,
            product_id=product_id,
            product_warehouse_lot_id=product_warehouse_lot_id,
            product_warehouse_serial_id=product_warehouse_serial_id,
            warehouse_id=warehouse_id,
            tracking_number=inventory_item_data.get('tracking_number', ''),
            tracking_method=inventory_item_data.get('tracking_method', 0),
            total_register_value=inventory_item_data.get('total_register_value', 0),
            company=instance.company,
            tenant=instance.tenant,
            employee_created=instance.employee_created,
        )


    @staticmethod
    def _create_ap_invoice_purchase_detail(instance, purchase_items_data):
        """Handle Purchase Fixed Assets (source_type=1)"""

        for purchase_item_data in purchase_items_data:

            ap_invoice_id=None
            if APInvoice.objects.filter(id=purchase_item_data.get('ap_invoice_id')).exists():
                ap_invoice_id = APInvoice.objects.filter(id=purchase_item_data.get('ap_invoice_id')).first().id

            # Create main purchase item
            purchase_item = FixedAssetApInvoicePurchaseItem.objects.create(
                fixed_asset=instance,
                ap_invoice_id=ap_invoice_id,
                total_register_value=purchase_item_data.get('total_register_value', 0)
            )

            # Create detail products if provided
            detail_products = purchase_item_data.get('detail_products', [])
            bulk_details = []
            for detail in detail_products:
                ap_invoice_item_id = None
                if APInvoiceItems.objects.filter(id=detail.get('ap_invoice_item_id')).exists():
                    ap_invoice_item_id = APInvoiceItems.objects.filter(id=detail.get('ap_invoice_item_id')).first().id

                bulk_details.append(FixedAssetApInvoicePurchaseItemDetailProduct(
                    title=detail.get('title'),
                    code=detail.get('code'),
                    ap_invoice_purchase_item=purchase_item,
                    quantity=detail.get('quantity', 0),
                    unit_price=detail.get('unit_price', 0),
                    amount=detail.get('amount', 0),
                    ap_invoice_item_id=ap_invoice_item_id
                ))

            if bulk_details:
                FixedAssetApInvoicePurchaseItemDetailProduct.objects.bulk_create(bulk_details)


    @staticmethod
    def _create_cash_out_purchase_detail(instance, cash_out_items_data):
        bulk_data = []
        for cash_out_item_data in cash_out_items_data:

            cash_out_id = None
            if CashOutflow.objects.filter(id=cash_out_item_data.get('cash_out_id')).exists():
                cash_out_id = CashOutflow.objects.filter(id=cash_out_item_data.get('cash_out_id')).first().id

            bulk_data.append(FixedAssetCashOutPurchaseItem(
                title= cash_out_item_data.get('title'),
                code=cash_out_item_data.get('code'),
                fixed_asset=instance,
                cash_out_id=cash_out_id,
                total_register_value=cash_out_item_data.get('total_register_value', 0)
            ))
        FixedAssetCashOutPurchaseItem.objects.bulk_create(bulk_data)


    @classmethod
    def create_depreciation_data(cls, instance, depreciation_data):
        if not depreciation_data:
            return

        depreciation_objects = []
        accumulated_months = 0

        for row in depreciation_data:
            # Calculate running total of months
            period_months = row.get('accumulative_month', 0)
            accumulated_months += period_months

            depreciation_objects.append(
                FixedAssetDepreciation(
                    fixed_asset=instance,
                    start_date=row['begin'],
                    end_date=row['end'],
                    period_months=period_months,
                    accumulated_months=accumulated_months,
                    period_depreciation=row['depreciation_value'],
                    accumulated_depreciation=row['accumulative_value'],
                    is_posted=False,
                    company=instance.company,
                    tenant=instance.tenant,
                    employee_created=instance.employee_created,
                )
            )

        FixedAssetDepreciation.objects.bulk_create(depreciation_objects)


    # @classmethod
    # def create_source(cls, instance, asset_sources, source_model):
    #     is_fixed_asset = isinstance(instance, FixedAsset)
    #     if is_fixed_asset:
    #         instance_field = 'fixed_asset'
    #     else:
    #         instance_field = 'instrument_tool'
    #     bulk_data = []
    #     for asset_source in asset_sources:
    #         bulk_data.append(source_model(
    #             **{instance_field: instance},
    #             description=asset_source.get('description'),
    #             code=asset_source.get('code'),
    #             document_no=asset_source.get('document_no'),
    #             transaction_type=asset_source.get('transaction_type'),
    #             value=asset_source.get('value')
    #         ))
    #     source_model.objects.bulk_create(bulk_data)

    # @classmethod
    # def create_ap_invoice_item(cls, instance, increase_fa_list, feature_ap_invoice_item_model):
    #     """Create FixedAssetAPInvoiceItems and update APInvoiceItems."""
    #
    #     is_fixed_asset = isinstance(instance, FixedAsset)
    #     if is_fixed_asset:
    #         instance_field = 'fixed_asset'
    #     else:
    #         instance_field = 'instrument_tool'
    #     bulk_data = []
    #     # format of increase_fa_list: increase_fa_list = {
    #     #     apinvoiceid: {
    #     #         apinvoiceitemid : value
    #     #     }
    #     # }
    #
    #     # loop through each item in increase_fa_list to get id and item
    #     for ap_invoice_id_key, items in increase_fa_list.items():
    #         # items = {
    #         #   apinvoiceitemid: value
    #         # }
    #         ap_invoice_items = APInvoiceItems.objects.filter(ap_invoice=ap_invoice_id_key)
    #
    #         # reformat the ap_invoice_items list:
    #         # new format:
    #         #   {
    #         #       apinvoiceitemid: apinvoiceitem (instance)
    #         #   }
    #         ap_invoice_items_dict = {str(item.id): item for item in ap_invoice_items}
    #
    #         # get apinvoiceitemid and value
    #         for ap_invoice_item_id_key, value in items.items():
    #             bulk_data.append(feature_ap_invoice_item_model(
    #                 **{instance_field: instance},
    #                 ap_invoice_item_id=ap_invoice_item_id_key,
    #                 increased_FA_value=value
    #             ))
    #             # if current apinvoiceitemid is in the id list, increase the FA value of that apinvoiceitem
    #             if ap_invoice_item_id_key in ap_invoice_items_dict:
    #                 item = ap_invoice_items_dict[ap_invoice_item_id_key]
    #                 item.increased_FA_value += value
    #                 item.save()
    #     feature_ap_invoice_item_model.objects.bulk_create(bulk_data)

    # @classmethod
    # def create_sub_data(cls, instance, **kwargs):
    #     use_departments = kwargs.get('use_departments', [])
    #     use_department_model = kwargs.get('use_department_model')
    #     asset_sources = kwargs.get('asset_sources', [])
    #     source_model = kwargs.get('source_model')
    #     increase_fa_list = kwargs.get('increase_fa_list', {})
    #     feature_ap_invoice_item_model = kwargs.get('feature_ap_invoice_item_model')
    #
    #     cls.create_use_department(instance, use_departments, use_department_model)
    #     cls.create_source(instance, asset_sources, source_model)
    #     cls.create_ap_invoice_item(instance, increase_fa_list, feature_ap_invoice_item_model)
