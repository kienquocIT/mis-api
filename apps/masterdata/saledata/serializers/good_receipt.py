from rest_framework import serializers

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.shared import GRMsg, BaseMsg

from apps.masterdata.saledata.models import (
    GoodReceipt, Account, GoodReceiptProduct, ProductWareHouse, GoodReceiptAttachment
)

__all__ = ['GoodReceiptListSerializer', 'GoodReceiptCreateSerializer', 'GoodReceiptDetailSerializer',
           'GoodReceiptUpdateSerializer']


class ProductListUtil:

    @staticmethod
    def create_update_product_list(product_list, instance):
        """
        step 1: kiểm tra ds theo good_receipt ko có thì delete đi
        step 2: tạo objs mới gọi func before_save add thêm field_data cho các Foreign key
        step 3: sau đó save bulk_create (do bulk_create ko chạy qua hàm before_save
        """
        if product_list and isinstance(product_list, list):
            check_pro_list = GoodReceiptProduct.objects.filter(good_receipt=instance)
            if check_pro_list.count():
                check_pro_list.delete()
            objs = []
            for prod in product_list:
                obj = GoodReceiptProduct(**prod, good_receipt=instance)
                obj.before_save()
                objs.append(obj)

            GoodReceiptProduct.objects.bulk_create(objs)

            # push data to ProductWareHouse
            for prod_receipt in objs:
                ProductWareHouse.push_from_receipt(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    product_id=prod_receipt.product_id,
                    warehouse_id=prod_receipt.warehouse_id,
                    uom_id=prod_receipt.uom_id,
                    tax_id=prod_receipt.tax_id,
                    amount=prod_receipt.quantity,
                    unit_price=prod_receipt.unit_price,
                )


# def handle_attach_file(user, instance, validated_attach, create_method):
#     # attachments: list -> danh sách id từ cloud trả về, tạm thời chi có 1 nên lấy [0]
#     relate_app = Application.objects.get(id="47e538a8-17e7-43bb-8c7e-dc936ccaf474")
#     relate_app_code = 'goodreceipt'
#     instance_id = str(instance.id)
#     attachment = validated_attach[0] if validated_attach else None
#     # check file trong API
#     current_attach = GoodReceiptAttachment.objects.filter(good_receipt=instance)
#
#     # kiểm tra current attach trùng media_id với attachments gửi lên
#     if current_attach.exists():
#         attach = current_attach.first()
#         if not str(attach.media_file) == attachment:
#             # this case update new file
#             current_attach.delete()
#         else:
#             # current and update file are the same or attachments is empty
#             return True
#
#     if not user.employee_current:
#         raise serializers.ValidationError(
#             {'User': BaseMsg.USER_NOT_MAP_EMPLOYEE}
#         )
#     # check file trên cloud
#     if not attachment:
#         return False
#     is_check, attach_check = Files.check_media_file(
#         media_file_id=attachment,
#         media_user_id=str(user.employee_current.media_user_id)
#     )
#     if not is_check:
#         raise serializers.ValidationError({'Attachment': BaseMsg.UPLOAD_FILE_ERROR})
#
#     # step 1: tạo mới file trong File API
#     files = Files.regis_media_file(
#         relate_app, instance_id, relate_app_code, user, media_result=attach_check
#     )
#     # step 2: tạo mới file trong table M2M
#     GoodReceiptAttachment.objects.create(
#         good_receipt=instance,
#         attachment=files,
#         media_file=attachment
#     )
#     instance.attachments = validated_attach
#     if create_method:
#         instance.save(update_fields=['attachments'])
#     return True


class GoodReceiptListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = GoodReceipt
        fields = (
            'id',
            'code',
            'title',
            'supplier',
            'posting_date',
            'system_status'
        )

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code
            }
        return {}


class GoodReceiptProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodReceiptProduct
        fields = (
            'product',
            'warehouse',
            'uom',
            'quantity',
            'unit_price',
            'tax',
            'subtotal_price',
            'order'
        )


class GoodReceiptCreateSerializer(serializers.ModelSerializer):
    supplier = serializers.UUIDField(required=False)
    product_list = GoodReceiptProductSerializer(many=True)

    class Meta:
        model = GoodReceipt
        fields = (
            'title',
            'supplier',
            'posting_date',
            'product_list',
            'pretax_amount',
            'taxes',
            'total_amount',
            'po_code',
            'attachments'
        )

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.TITLE)
        return value

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError(GRMsg.SUPPLIER)

    @classmethod
    def validate_product_list(cls, value):
        if not value:
            raise serializers.ValidationError(GRMsg.PRODUCT_LIST)
        return value

    @staticmethod
    def reparse_product_list(data):
        """
        parse data từ object của GoodReceiptProductSerializer sang json và trả vể cho hàm create hoặc update
        """
        arr = []
        for item in data:
            item = dict(item)
            arr.append(
                {
                    'product': str(item['product']) if 'product' in item else None,
                    'warehouse': str(item['warehouse']) if 'warehouse' in item else None,
                    'uom': str(item['uom']) if 'uom' in item else None,
                    'tax': str(item['tax']) if 'tax' in item else None,
                    "quantity": item['quantity'] if 'quantity' in item else None,
                    "unit_price": item['unit_price'] if 'unit_price' in item else None,
                    "subtotal_price": item['subtotal_price'] if 'subtotal_price' in item else None,
                    "order": item['order'] if 'order' in item else None,
                }
            )
        return arr

    def create(self, validated_data):
        """
        do product_list được valid từ serializer nên khi trả vể validate sẽ là object
        trước khi save data thì cần parse lại json đồng thời tạo mới bảng phụ bằng func create_update_product_list.
        """
        user = self.context.get('user', None)
        product_list = validated_data.pop('product_list', [])
        instance = GoodReceipt.objects.create(
            **validated_data, product_list=self.reparse_product_list(self.data['product_list'])
        )
        if instance:
            ProductListUtil.create_update_product_list(product_list, instance)
            # handle_attach_file(user, instance, validated_data.get('attachments', None), True)
        return instance


class GoodReceiptDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField(required=False)
    product_list = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = GoodReceipt
        fields = (
            'id',
            'code',
            'title',
            'supplier',
            'date_created',
            'posting_date',
            'product_list',
            'pretax_amount',
            'taxes',
            'total_amount',
            'attachments',
            'po_code'
        )

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code,
            }
        return {}

    @classmethod
    def get_product_list(cls, obj):
        pd_list = GoodReceiptProduct.objects.filter(good_receipt=obj.id)
        if pd_list:
            parse_list = []
            for item in pd_list:
                parse_list.append(
                    {
                        'product': item.product_data,
                        'warehouse': item.warehouse_data,
                        'uom': item.uom_data,
                        'tax': item.tax_data,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'subtotal_price': item.subtotal_price,
                        'order': item.order
                    }
                )
            return parse_list
        return []

    @classmethod
    def get_attachments(cls, obj):
        if obj.attachments:
            one_attach = obj.attachments[0]
            file = GoodReceiptAttachment.objects.filter(
                good_receipt=obj,
                media_file=one_attach
            )
            if file.exists():
                # obj.attachments = list((lambda x: x.files, attach))
                attachments = []
                # obj.attachments = list(map(lambda x: x['files'], attach))
                for item in file:
                    files = item.attachment
                    attachments.append(
                        {
                            'files': {
                                "id": str(files.id),
                                "relate_app_id": str(files.relate_app_id),
                                "relate_app_code": files.relate_app_code,
                                "relate_doc_id": str(files.relate_doc_id),
                                "media_file_id": str(files.media_file_id),
                                "file_name": files.file_name,
                                "file_size": int(files.file_size),
                                "file_type": files.file_type
                            }
                        }
                    )
                return attachments
        return []


class GoodReceiptUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodReceipt
        fields = (
            'attachments',
        )

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        # handle_attach_file(user, instance, validated_data.get('attachments', None), False)
        instance.save()
        return instance
