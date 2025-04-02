from apps.sales.apinvoice.models import APInvoiceItems
from apps.sales.asset.models import FixedAsset


class CommonHandler:
    @classmethod
    def create_use_department(cls, instance, use_departments, use_department_model):
        is_fixed_asset = isinstance(instance, FixedAsset)
        if is_fixed_asset:
            instance_field = 'fixed_asset'
        else:
            instance_field = 'instrument_tool'
        bulk_data = []
        for use_department in use_departments:
            bulk_data.append(use_department_model(
                **{instance_field: instance},
                use_department=use_department,
            ))
        use_department_model.objects.bulk_create(bulk_data)

    @classmethod
    def create_source(cls, instance, asset_sources, source_model):
        is_fixed_asset = isinstance(instance, FixedAsset)
        if is_fixed_asset:
            instance_field = 'fixed_asset'
        else:
            instance_field = 'instrument_tool'
        bulk_data = []
        for asset_source in asset_sources:
            bulk_data.append(source_model(
                **{instance_field: instance},
                description=asset_source.get('description'),
                code=asset_source.get('code'),
                document_no=asset_source.get('document_no'),
                transaction_type=asset_source.get('transaction_type'),
                value=asset_source.get('value')
            ))
        source_model.objects.bulk_create(bulk_data)

    @classmethod
    def create_ap_invoice_item(cls, instance, increase_fa_list, feature_ap_invoice_item_model):
        """Create FixedAssetAPInvoiceItems and update APInvoiceItems."""

        is_fixed_asset = isinstance(instance, FixedAsset)
        if is_fixed_asset:
            instance_field = 'fixed_asset'
        else:
            instance_field = 'instrument_tool'
        bulk_data = []
        # format of increase_fa_list: increase_fa_list = {
        #     apinvoiceid: {
        #         apinvoiceitemid : value
        #     }
        # }

        # loop through each item in increase_fa_list to get id and item
        for ap_invoice_id_key, items in increase_fa_list.items():
            # items = {
            #   apinvoiceitemid: value
            # }
            ap_invoice_items = APInvoiceItems.objects.filter(ap_invoice=ap_invoice_id_key)

            # reformat the ap_invoice_items list:
            # new format:
            #   {
            #       apinvoiceitemid: apinvoiceitem (instance)
            #   }
            ap_invoice_items_dict = {str(item.id): item for item in ap_invoice_items}

            # get apinvoiceitemid and value
            for ap_invoice_item_id_key, value in items.items():
                bulk_data.append(feature_ap_invoice_item_model(
                    **{instance_field: instance},
                    ap_invoice_item_id=ap_invoice_item_id_key,
                    increased_FA_value=value
                ))
                # if current apinvoiceitemid is in the id list, increase the FA value of that apinvoiceitem
                if ap_invoice_item_id_key in ap_invoice_items_dict:
                    item = ap_invoice_items_dict[ap_invoice_item_id_key]
                    item.increased_FA_value += value
                    item.save()
        feature_ap_invoice_item_model.objects.bulk_create(bulk_data)

    @classmethod
    def create_sub_data(cls, instance, **kwargs):
        use_departments = kwargs.get('use_departments', [])
        use_department_model = kwargs.get('use_department_model')
        asset_sources = kwargs.get('asset_sources', [])
        source_model = kwargs.get('source_model')
        increase_fa_list = kwargs.get('increase_fa_list', {})
        feature_ap_invoice_item_model = kwargs.get('feature_ap_invoice_item_model')

        cls.create_use_department(instance, use_departments, use_department_model)
        cls.create_source(instance, asset_sources, source_model)
        cls.create_ap_invoice_item(instance, increase_fa_list, feature_ap_invoice_item_model)
