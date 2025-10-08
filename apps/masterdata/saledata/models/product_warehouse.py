from django.db import models
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel, TYPE_LOT_TRANSACTION, SERIAL_STATUS
from .product import UnitOfMeasure


__all__ = [
    'ProductWareHouse',
    'ProductWareHouseLot',
    'ProductWareHouseSerial',
    'PWModified',
    'PWModifiedComponent',
    'PWModifiedComponentDetail',
    'ProductSpecificIdentificationSerial'
]


class ProductWareHouse(MasterDataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product of WareHouse',
        related_name='product_warehouse_product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name='WareHouse of Product',
        related_name='product_warehouse_warehouse',
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='Unit Of Measure of Product',
        null=True,
    )
    unit_price = models.FloatField(
        default=0,
        verbose_name='Unit prices of Product',
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name='Tax of Product',
        null=True,
    )

    # stock
    stock_amount = models.FloatField(
        default=0,
        verbose_name="Stock",
        help_text="Physical amount product in warehouse, =(receipt_amount - sold_amount)",
    )
    receipt_amount = models.FloatField(
        default=0,
        verbose_name='Receipt Amount',
        help_text='Amount product receipted, update when goods receipt'
    )
    sold_amount = models.FloatField(
        default=0,
        verbose_name='Sold Amount',
        help_text='Amount product delivered, update when deliver'
    )
    picked_ready = models.FloatField(
        default=0,
        verbose_name='Picked Amount',
    )
    used_amount = models.FloatField(
        default=0,
        verbose_name='Used Amount',
        help_text='Amount product delivered for employee use'
    )

    # backup data
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product backup data',
    )
    warehouse_data = models.JSONField(
        default=dict,
        verbose_name='WareHouse backup data',
    )
    uom_data = models.JSONField(
        default=dict,
        verbose_name='Unit Of Measure backup data',
    )
    tax_data = models.JSONField(
        default=dict,
        verbose_name='Tax backup data',
    )

    @classmethod
    def push_from_receipt(
            cls,
            tenant_id,
            company_id,
            product_id,
            warehouse_id,
            uom_id,
            tax_id,
            amount: float,
            unit_price: float,
            lot_data=None,
            serial_data=None,
            **kwargs
    ):
        obj, _created = cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, product_id=product_id, warehouse_id=warehouse_id,
            defaults={
                'uom_id': uom_id,
                'tax_id': tax_id,
                'stock_amount': amount,
                'receipt_amount': amount,
                'unit_price': unit_price,
            }
        )
        if _created is False:  # created before => updates
            obj.receipt_amount += amount
            obj.stock_amount = obj.receipt_amount - obj.sold_amount
            obj.save(update_fields=['stock_amount', 'receipt_amount'])
        # push ProductWareHouseLot, ProductWareHouseSerial
        if lot_data and isinstance(lot_data, list):
            ProductWareHouseLot.push_pw_lot(
                tenant_id=tenant_id,
                company_id=company_id,
                product_warehouse_id=obj.id,
                lot_data=lot_data,
                type_transaction=0,
            )
        if serial_data and isinstance(serial_data, list):
            ProductWareHouseSerial.create(
                tenant_id=tenant_id,
                company_id=company_id,
                product_warehouse_id=obj.id,
                product_id=obj.product_id,
                serial_data=serial_data
            )

        return True

    @classmethod
    def get_stock(
            cls,
            product_id, warehouse_id, uom_id,
            tenant_id=None, company_id=None,
    ):
        try:
            uom = UnitOfMeasure.objects.get(id=uom_id)
            uom_ratio = uom.ratio
            if tenant_id and company_id:
                objs = cls.objects.filter(
                    product_id=product_id, warehouse_id=warehouse_id,
                    tenant_id=tenant_id, company_id=company_id,
                )
            else:
                objs = cls.objects.filter_current(
                    product_id=product_id, warehouse_id=warehouse_id,
                    fill__tenant=True, fill__company=True,
                )
            count = 0
            for obj in objs:
                count += ((obj.stock_amount - obj.sold_amount) * obj.uom.ratio) / uom_ratio
            count = round(count, uom.rounding)
            return count
        except cls.DoesNotExist:
            pass
        return 0

    @classmethod
    def get_picked_ready(
            cls,
            product_id, warehouse_id, uom_id,
            tenant_id=None, company_id=None,
    ):
        try:
            uom = UnitOfMeasure.objects.get(id=uom_id)
            uom_ratio = uom.ratio
            if tenant_id and company_id:
                objs = cls.objects.filter(
                    product_id=product_id, warehouse_id=warehouse_id,
                    tenant_id=tenant_id, company_id=company_id,
                )
            else:
                objs = cls.objects.filter_current(
                    product_id=product_id, warehouse_id=warehouse_id,
                    fill__tenant=True, fill__company=True,
                )
            count = 0
            for obj in objs:
                count += (obj.picked_ready * obj.uom.ratio) / uom_ratio
            count = round(count, uom.rounding)
            return count
        except cls.DoesNotExist:
            pass
        return 0

    @classmethod
    def pop_from_transfer(cls, product_warehouse_id, amount, data):
        try:
            prd_wh_obj = cls.objects.get(id=product_warehouse_id)

            prd_wh_obj.sold_amount += amount
            prd_wh_obj.stock_amount = prd_wh_obj.receipt_amount - prd_wh_obj.sold_amount
            prd_wh_obj.save(update_fields=['sold_amount', 'stock_amount'])

            prd_wh_obj.product.stock_amount -= amount
            prd_wh_obj.product.available_amount -= amount
            prd_wh_obj.product.save(update_fields=['stock_amount', 'available_amount'])

            if prd_wh_obj.product.general_traceability_method == 1:  # lot
                if len(data['lot_changes']) == 0:
                    raise ValueError('Lot data can not NULL')
                for each in data['lot_changes']:
                    lot = ProductWareHouseLot.objects.filter(id=each['lot_id']).first()
                    if lot and each['old_quantity'] - each['quantity'] > 0:
                        if lot.quantity_import >= amount:
                            lot.quantity_import -= amount
                            lot.save(update_fields=['quantity_import'])
                        else:
                            raise ValueError('Lot quantity must be > 0')
            elif prd_wh_obj.product.general_traceability_method == 2:  # sn
                if len(data['sn_changes']) == 0:
                    raise ValueError('Serial data can not NULL')
                sn_list = ProductWareHouseSerial.objects.filter(id__in=data['sn_changes'])
                for each in sn_list:
                    each.is_delete = 1
                    each.save(update_fields=['is_delete'])
            return True
        except cls.DoesNotExist:
            raise ValueError('Product is not found in warehouse with UOM')

    def before_save(self, **kwargs):
        if kwargs.get('force_insert', False):
            if self.product:
                self.product_data = {
                    'id': str(self.product.id),
                    'title': str(self.product.title),
                    'code': str(self.product.code),
                }
            if self.warehouse:
                self.warehouse_data = {
                    'id': str(self.warehouse.id),
                    'title': str(self.warehouse.title),
                    'code': str(self.warehouse.code),
                }
            if self.uom:
                self.uom_data = {
                    'id': str(self.uom.id),
                    'title': str(self.uom.title),
                    'code': str(self.uom.code),
                }
            if self.tax:
                self.tax_data = {
                    'id': str(self.tax.id),
                    'title': str(self.tax.title),
                    'code': str(self.tax.code),
                    'rate': str(self.tax.rate),
                    'category_id': str(self.tax.category),
                    'type': self.tax.tax_type,
                }
        return True

    def save(self, *args, **kwargs):
        self.before_save(**kwargs)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product mapping WareHouse'
        verbose_name_plural = 'Product mapping WareHouse'
        unique_together = ('company_id', 'warehouse_id', 'product_id', 'uom_id',)
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductWareHouseLot(MasterDataAbstractModel):
    product_warehouse = models.ForeignKey(
        ProductWareHouse,
        on_delete=models.CASCADE,
        verbose_name="product warehouse",
        related_name="product_warehouse_lot_product_warehouse",
    )
    lot_number = models.CharField(max_length=100, blank=True, null=True)
    quantity_import = models.FloatField(
        default=0,
        help_text='when GoodsReceipt this quantity +=, when Delivery this quantity -='
    )
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)

    @classmethod
    def push_pw_lot(
            cls,
            tenant_id,
            company_id,
            product_warehouse_id,
            lot_data,
            type_transaction,
    ):
        for lot in lot_data:
            goods_receipt_id = None
            purchase_request_id = None
            delivery_id = None
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id,
                product_warehouse_id=product_warehouse_id, lot_number=lot.get('lot_number', ''),
                defaults={
                    'quantity_import': lot.get('quantity_import', 0),
                    'expire_date': lot.get('expire_date', None),
                    'manufacture_date': lot.get('manufacture_date', None),
                }
            )
            if _created is False:  # created before => update
                if type_transaction == 0:  # Goods receipt
                    obj.quantity_import += lot.get('quantity_import', 0)
                if type_transaction == 1:  # Delivery
                    if obj.quantity_import > 0:
                        fn_quantity = 0
                        calc = obj.quantity_import - lot.get('quantity_import', 0)
                        if calc >= 0:
                            fn_quantity = lot.get('quantity_import', 0)
                        if calc < 0:
                            fn_quantity = lot.get('quantity_import', 0) + calc
                        obj.quantity_import -= fn_quantity
                # save
                if obj.quantity_import >= 0:
                    obj.save(update_fields=['quantity_import'])
            # create ProductWareHouseLotTransaction
            if type_transaction == 0:
                goods_receipt_id = lot.get('goods_receipt_id', None)
                purchase_request_id = lot.get('purchase_request_id', None)
            if type_transaction == 1:
                delivery_id = lot.get('delivery_id', None)
            data = {
                'pw_lot_id': obj.id,
                'goods_receipt_id': goods_receipt_id,
                'purchase_request_id': purchase_request_id,
                'delivery_id': delivery_id,
                'quantity': lot.get('quantity_import', 0),
                'type_transaction': type_transaction,
            }
            ProductWareHouseLotTransaction.create(data=data)
        return True

    class Meta:
        verbose_name = 'Product Warehouse Lot'
        verbose_name_plural = 'Product Warehouse Lots'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductWareHouseLotTransaction(SimpleAbstractModel):
    pw_lot = models.ForeignKey(
        ProductWareHouseLot,
        on_delete=models.CASCADE,
        verbose_name="product warehouse lot",
        related_name="pw_lot_transact_pw_lot",
    )
    goods_receipt = models.ForeignKey(
        'inventory.GoodsReceipt',
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="pw_lot_transact_goods_receipt",
        help_text="To know this lot was receipted by which GoodsReceipt",
        null=True,
    )
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="purchase request",
        related_name="pw_lot_purchase_request",
        help_text="To know this lot was receipted by which PurchaseRequest"
    )
    delivery = models.ForeignKey(
        'delivery.OrderDeliverySub',
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="pw_lot_transact_delivery",
        help_text="To know this lot was delivered by which OrderDeliverySub",
        null=True,
    )
    goods_return = models.ForeignKey(
        'inventory.GoodsReturn',
        on_delete=models.CASCADE,
        verbose_name="goods return",
        related_name="pw_lot_transact_goods_return",
        help_text="To know this lot was returned by which GoodsReturn",
        null=True,
    )
    goods_transfer = models.ForeignKey(
        'inventory.GoodsTransfer',
        on_delete=models.CASCADE,
        verbose_name="goods transfer",
        related_name="pw_lot_transact_goods_transfer",
        help_text="To know this lot was transferred by which GoodsTransfer",
        null=True,
    )
    transfer_type = models.BooleanField(null=True, help_text="transfer type: 1 is IN, 0 is OUT")
    goods_issue = models.ForeignKey(
        'inventory.GoodsIssue',
        on_delete=models.CASCADE,
        verbose_name="goods issue",
        related_name="pw_lot_transact_goods_issue",
        help_text="To know this lot was issued by which GoodsIssue",
        null=True,
    )
    quantity = models.FloatField(default=0)
    type_transaction = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(TYPE_LOT_TRANSACTION),
    )

    @classmethod
    def create(cls, data):
        cls.objects.create(**data)
        return True

    class Meta:
        verbose_name = 'Product Warehouse Lot Transaction'
        verbose_name_plural = 'Product Warehouse Lot Transactions'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ProductWareHouseSerial(MasterDataAbstractModel):
    product_warehouse = models.ForeignKey(
        ProductWareHouse,
        on_delete=models.CASCADE,
        verbose_name="product warehouse",
        related_name="product_warehouse_serial_product_warehouse",
    )
    vendor_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)
    warranty_start = models.DateTimeField(null=True)
    warranty_end = models.DateTimeField(null=True)
    goods_receipt = models.ForeignKey(
        'inventory.GoodsReceipt',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="goods receipt",
        related_name="pw_serial_goods_receipt",
        help_text="To know this serial was receipted by which GoodsReceipt"
    )
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="purchase request",
        related_name="pw_serial_purchase_request",
        help_text="To know this serial was receipted by which PurchaseRequest"
    )
    # Status of serial
    serial_status = models.SmallIntegerField(choices=SERIAL_STATUS, default=0, help_text="Flag to know current status")
    use_for_modification = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Warehouse Serial'
        verbose_name_plural = 'Product Warehouse Serials'
        ordering = ('serial_number',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            product_warehouse_id,
            product_id,
            serial_data
    ):
        serial_data_valid = [
            serial for serial in serial_data
            if not cls.objects.filter(
                serial_number=serial.get('serial_number', ''), product_warehouse__product_id=product_id,
            ).exists()
        ]
        cls.objects.bulk_create([cls(
            **data,
            tenant_id=tenant_id,
            company_id=company_id,
            product_warehouse_id=product_warehouse_id,
        ) for data in serial_data_valid])

        for serial_old in cls.objects.filter(
                serial_number__in=[serial.get('serial_number', '') for serial in serial_data],
                product_warehouse_id=product_warehouse_id,
                product_warehouse__product_id=product_id,
                serial_status=1,
        ):
            for serial in serial_data:
                if serial_old.serial_number == serial.get('serial_number', ''):
                    serial_old.serial_status = 0
                    serial_old.save(update_fields=['serial_status'])
                    break
        return True


class PWModified(MasterDataAbstractModel):
    product_warehouse = models.ForeignKey(
        ProductWareHouse,
        on_delete=models.CASCADE,
        related_name="pw_modified_pw",
    )
    product_warehouse_serial = models.ForeignKey(
        ProductWareHouseSerial,
        on_delete=models.CASCADE,
        related_name="pw_modified_pw_serial",
        null=True
    )
    product_warehouse_lot = models.ForeignKey(
        ProductWareHouseLot,
        on_delete=models.CASCADE,
        related_name="pw_modified_pw_lot",
        null=True
    )
    modified_number = models.CharField(max_length=100)
    new_description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Product Warehouse Modified'
        verbose_name_plural = 'Products Warehouses Modified'
        ordering = ('-modified_number',)
        default_permissions = ()
        permissions = ()


class PWModifiedComponent(SimpleAbstractModel):
    pw_modified = models.ForeignKey(
        PWModified,
        on_delete=models.CASCADE,
        related_name="pw_modified_components",
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict)  # {'title': ...; 'description':...}
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.FloatField()

    class Meta:
        verbose_name = 'Product Warehouse Modified Component'
        verbose_name_plural = 'Products Warehouses Modified Component'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class PWModifiedComponentDetail(SimpleAbstractModel):
    pw_modified_component = models.ForeignKey(
        PWModifiedComponent,
        on_delete=models.CASCADE,
        related_name='pw_modified_component_detail',
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Product Warehouse Modified Component Detail'
        verbose_name_plural = 'Products Warehouses Modified Component Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ProductSpecificIdentificationSerial(SimpleAbstractModel):
    """
    Model lưu trữ thông tin về giá của 1 serial quản lí tồn kho theo thực tế đích danh.
    Vì sản phẩm này được đính giá trị theo từng serial nên không phân biệt kho nào cả, chỉ đơn giản: product - serial
    """
    product = models.ForeignKey(
        'saledata.Product', on_delete=models.CASCADE, related_name='pw_si_serial_product',
    )
    vendor_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)
    warranty_start = models.DateTimeField(null=True)
    warranty_end = models.DateTimeField(null=True)
    # trường này lưu giá trị thực tế đích danh (PP này chỉ apply cho SP serial)
    specific_value = models.FloatField(default=0)

    @staticmethod
    def create_or_update_si_product_serial(product, serial_obj, specific_value):
        """ Cập nhập hoặc tạo giá đich danh """
        si_serial_obj = ProductSpecificIdentificationSerial.objects.filter(
            product=product,
            serial_number=serial_obj.serial_number
        ).first()
        if not si_serial_obj:
            ProductSpecificIdentificationSerial.objects.create(
                product=product,
                vendor_serial_number=serial_obj.vendor_serial_number,
                serial_number=serial_obj.serial_number,
                expire_date=serial_obj.expire_date,
                manufacture_date=serial_obj.manufacture_date,
                warranty_start=serial_obj.warranty_start,
                warranty_end=serial_obj.warranty_end,
                specific_value=specific_value
            )
        else:
            si_serial_obj.specific_value = specific_value
            si_serial_obj.save(update_fields=['specific_value'])
        return True

    @staticmethod
    def get_specific_value(product, serial_number):
        """Lấy giá đich danh """
        si_product_serial_obj = ProductSpecificIdentificationSerial.objects.filter(
            product=product, serial_number=serial_number
        ).first()
        return si_product_serial_obj.specific_value if si_product_serial_obj else 0

    class Meta:
        verbose_name = 'Product Specific Identification Serial'
        verbose_name_plural = 'Product Specific Identification Serials'
        ordering = ('serial_number',)
        default_permissions = ()
        permissions = ()
