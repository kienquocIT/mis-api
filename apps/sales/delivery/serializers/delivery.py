from django.db import transaction
from django.utils import timezone

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.masterdata.saledata.models import ProductWareHouse, UnitOfMeasure, WareHouse, Product
from apps.shared import TypeCheck, HrMsg
from apps.shared.translations.base import AttachmentMsg
from ..models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct, OrderDeliveryAttachment
from ..utils import CommonFunc

__all__ = ['OrderDeliveryListSerializer', 'OrderDeliverySubListSerializer', 'OrderDeliverySubDetailSerializer',
           'OrderDeliverySubUpdateSerializer', 'DeliProductInformationHandle']

from ...acceptance.models import FinalAcceptance
from ...report.models import ReportInventorySub


class WarehouseQuantityHandle:
    @classmethod
    def minus_tock(cls, source, target, config):
        # sản phầm trong phiếu
        # source: dict { uom: uuid, quantity: number }
        # sản phẩm trong kho
        # target: object of warehouse has prod (all prod)
        # kiểm tra kho còn hàng và trừ kho nếu ko đủ return failure
        source_uom = UnitOfMeasure.objects.filter(id=source['uom'])
        if source_uom.exists():
            source_uom = source_uom.first()
            source_ratio = source_uom.ratio
        else:
            # return if source uom not found
            raise ValueError(
                {'detail': _('Products UoM not found please verify Sale Order or contact your admin')}
            )
        # số lượng prod đã quy đổi
        mediate_number = source['quantity'] * source_ratio

        if 'is_fifo_lifo' in config and config['is_fifo_lifo']:
            target = target.reverse()
        is_done = False
        list_update = []
        for item in target:
            if is_done:
                # nếu trừ đủ update vào warehouse, return true
                break
            target_ratio = item.uom.ratio
            if item.stock_amount > 0:
                # số lượng trong kho đã quy đổi
                in_stock_unit = item.stock_amount * target_ratio
                calc = in_stock_unit - mediate_number
                # item_sold = 0
                if calc >= 0:
                    # đủ hàng
                    is_done = True
                    item_sold = mediate_number / target_ratio
                    item.sold_amount += item_sold
                    item.stock_amount = item.receipt_amount - item.sold_amount
                    if config['is_picking']:
                        item.picked_ready = item.picked_ready - item_sold
                    list_update.append(item)
                elif calc < 0:
                    # else < 0 ko đù
                    # gán số còn thiếu cho số lượng cần trừ kho (mediate_number_clone)
                    # trừ kho tất cả của record này
                    mediate_number = abs(calc)
                    item.sold_amount += in_stock_unit
                    # item_sold = in_stock_unit
                    item.stock_amount = item.receipt_amount - item.sold_amount
                    if config['is_picking']:
                        item.picked_ready = item.picked_ready - in_stock_unit
                    list_update.append(item)

                # # update product wait_delivery_amount
                # item.product.save(**{
                #     'update_transaction_info': True,
                #     'quantity_delivery': item_sold,
                #     'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                # })
        ProductWareHouse.objects.bulk_update(list_update, fields=['sold_amount', 'picked_ready', 'stock_amount'])
        return True


class DeliProductInformationHandle:

    @classmethod
    def main_handle(cls, instance, validated_product=None):
        if not validated_product:
            for deli_product in instance.delivery_product_delivery_sub.all():
                if deli_product.product:
                    deli_product.product.save(**{
                        'update_transaction_info': True,
                        'quantity_delivery': deli_product.picked_quantity,
                        'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                    })
        else:
            for product_data in validated_product:
                if all(key in product_data for key in ('product_id', 'done')):
                    product_obj = Product.objects.filter(
                        tenant_id=instance.tenant_id, company_id=instance.company_id, id=product_data['product_id']
                    ).first()
                    if product_obj:
                        product_obj.save(**{
                            'update_transaction_info': True,
                            'quantity_delivery': product_data['done'],
                            'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                        })
        return True


class DeliProductWarehouseHandle:

    @classmethod
    def main_handle(cls, instance):
        config = instance.config_at_that_point
        if not config:
            get_config = DeliveryConfig.objects.filter(company_id=instance.company_id).first()
            if get_config:
                config = {
                    "is_picking": get_config.is_picking,
                    "is_partial_ship": get_config.is_partial_ship
                }
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product and deli_product.delivery_data:
                for data in deli_product.delivery_data:
                    if all(key in data for key in ('warehouse', 'uom', 'stock')):
                        product_warehouse = ProductWareHouse.objects.filter(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_id=deli_product.product_id,
                            warehouse_id=data['warehouse'],
                        )
                        source = {
                            "uom": data['uom'],
                            "quantity": data['stock']
                        }
                        WarehouseQuantityHandle.minus_tock(source, product_warehouse, config)
        return True


class DeliSODeliveryStatusHandle:

    @classmethod
    def main_handle(cls, instance):
        if instance.order_delivery.sale_order:
            # update sale order delivery_status (Partially delivered)
            if instance.order_delivery.sale_order.delivery_status in [0, 1]:
                instance.order_delivery.sale_order.delivery_status = 2
                instance.order_delivery.sale_order.save(update_fields=['delivery_status'])
            # update sale order delivery_status (Delivered)
            if instance.order_delivery.sale_order.delivery_status in [2] and instance.order_delivery.state == 2:
                instance.order_delivery.sale_order.delivery_status = 3
                instance.order_delivery.sale_order.save(update_fields=['delivery_status'])
        return True


class DeliOpportunityStageHandle:

    @classmethod
    def main_handle(cls, instance):
        if instance.order_delivery.sale_order and instance.order_delivery.state == 2:
            if instance.order_delivery.sale_order.opportunity:
                instance.order_delivery.sale_order.opportunity.save(**{
                    'delivery_status': instance.order_delivery.state,
                })
        return True


class DeliFinalAcceptanceHandle:

    @classmethod
    def main_handle(cls, instance, validated_product):
        list_data_indicator = []
        for item in validated_product:
            # config final acceptance
            actual_value = 0
            if all(key in item for key in ('product_id', 'delivery_data')):
                for data_deli in item['delivery_data']:
                    if all(key in data_deli for key in ('warehouse', 'stock')):
                        pw_inventory = ReportInventorySub.objects.filter(
                            report_inventory__tenant_id=instance.tenant_id,
                            report_inventory__company_id=instance.company_id,
                            product_id=item['product_id'],
                            warehouse_id=data_deli['warehouse'],
                        ).first()
                        actual_value += pw_inventory.current_cost * data_deli['stock'] if pw_inventory else 0
                list_data_indicator.append({
                    'tenant_id': instance.tenant_id,
                    'company_id': instance.company_id,
                    'sale_order_id': instance.order_delivery.sale_order_id,
                    'delivery_sub_id': instance.id,
                    'product_id': item['product_id'],
                    'actual_value': actual_value,
                    'is_delivery': True,
                })
        FinalAcceptance.create_final_acceptance_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.order_delivery.sale_order_id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            opportunity_id=instance.order_delivery.sale_order.opportunity_id,
            list_data_indicator=list_data_indicator
        )
        return True


class OrderDeliveryProductListSerializer(serializers.ModelSerializer):
    is_not_inventory = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()

    @classmethod
    def get_is_not_inventory(cls, obj):
        if obj.product.product_choice:
            if 1 in obj.product.product_choice:
                return bool(True)
        return bool(False)

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
        } if obj.product else {}

    @classmethod
    def get_uom_data(cls, obj):
        if obj.product:
            so_product = obj.product.sale_order_product_product.first()
            if so_product:
                return {
                    'id': so_product.unit_of_measure_id,
                    'title': so_product.unit_of_measure.title,
                    'code': so_product.unit_of_measure.code,
                    'ratio': so_product.unit_of_measure.ratio,
                } if so_product.unit_of_measure else {}
        return {}

    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'uom_data',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'picked_quantity',
            'is_not_inventory'
        )


class OrderDeliverySubListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
        } if obj.employee_inherit else {}

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'code',
            'sale_order_data',
            'date_created',
            'estimated_delivery_date',
            'actual_delivery_date',
            'employee_inherit',
            'state',
        )


class OrderDeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_data',
            'state',
            'is_active',
        )


class OrderDeliverySubDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        prod = OrderDeliveryProductListSerializer(
            obj.delivery_product_delivery_sub.all(),
            many=True,
        ).data
        return prod

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    @classmethod
    def get_attachments(cls, obj):
        if obj.attachments:
            attach = OrderDeliveryAttachment.objects.filter(
                delivery_sub=obj,
                media_file=obj.attachments
            )
            if attach.exists():
                attachments = []
                for item in attach:
                    files = item.files
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

    class Meta:
        model = OrderDeliverySub
        fields = (
            'order_delivery',
            'id',
            'remarks',
            'times',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'is_updated',
            'products',
            'state',
            'code',
            'sale_order_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'customer_data',
            'contact_data',
            'config_at_that_point',
            'attachments',
            'delivery_logistic',
            'workflow_runtime_id',
            'employee_inherit'
        )


class ProductDeliveryUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField(allow_null=True)
    order = serializers.IntegerField(min_value=1)


class OrderDeliverySubUpdateSerializer(serializers.ModelSerializer):
    products = ProductDeliveryUpdateSerializer(many=True)
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'order_delivery',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'is_updated',
            'state',
            'estimated_delivery_date',
            'actual_delivery_date',
            'remarks',
            'products',
            'attachments',
            'delivery_logistic',
            'employee_inherit_id'
        )

    @classmethod
    def validate_state(cls, value):
        if value < 2:
            return value
        raise serializers.ValidationError(
            {
                'State': _('Can not update when status is Done!')
            }
        )

    def handle_attach_file(self, instance, validate_data):
        attachments = validate_data.get('attachments', None)
        if attachments and TypeCheck.check_uuid_list(attachments):
            user = self.context.get('user', None)
            relate_app = Application.objects.get(id="1373e903-909c-4b77-9957-8bcf97e8d6d3")
            delivery_sub_id = str(self.instance.id)

            employee_id = user.employee_current_id
            if not employee_id:
                raise serializers.ValidationError({'User': HrMsg.EMPLOYEE_WAS_LINKED})

            # check files
            state, att_objs = Files.check_media_file(file_ids=attachments, employee_id=employee_id, doc_id=instance.id)
            if state:
                # register file
                file_objs = Files.regis_media_file(
                    relate_app=relate_app, relate_doc_id=delivery_sub_id, file_objs_or_ids=att_objs,
                )

                # create m2m attachment
                m2m_obj = []
                for _counter, obj in enumerate(file_objs):
                    m2m_obj.append(
                        OrderDeliveryAttachment(
                            delivery_sub=self.instance,
                            files=obj,
                            date_created=getattr(obj, 'date_created', timezone.now()),
                        )
                    )
                OrderDeliveryAttachment.objects.bulk_create(m2m_obj)

                instance.attachments = validate_data['attachments']
                return validate_data
            raise serializers.ValidationError({'Attachment': AttachmentMsg.ERROR_VERIFY})
        return True

    @classmethod
    def update_self_info(cls, instance, validated_data):
        instance.estimated_delivery_date = validated_data['estimated_delivery_date']
        instance.actual_delivery_date = validated_data['actual_delivery_date']
        instance.remarks = validated_data['remarks']
        if 'delivery_logistic' in validated_data and validated_data['delivery_logistic']:
            instance.delivery_logistic = validated_data['delivery_logistic']

    @classmethod
    def minus_product_warehouse_stock(cls, tenant_com_info, product, stock_info, config):
        # sử dụng vòng for trong delivery data để đảm bảo nếu như pick từ nhiều kho khác nhau, thì có thể trừ đúng kho
        # bên picking đã pick, một trong các prod ko dc trừ sẽ trã vể lỗi phiếu
        for data in stock_info:
            product_warehouse = ProductWareHouse.objects.filter(
                tenant_id=tenant_com_info['tenant_id'],
                company_id=tenant_com_info['company_id'],
                product_id=product.product_id,
                warehouse_id=data['warehouse'],
            )
            if product_warehouse.exists():
                source = {
                    "uom": data['uom'],
                    "quantity": data['stock']
                }
                WarehouseQuantityHandle.minus_tock(source, product_warehouse, config)

    @classmethod
    def update_prod(cls, sub, product_done, config):
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=sub
        ):
            obj_key = str(obj.product_id) + "___" + str(obj.order)
            if obj_key in product_done:
                if 1 in obj.product.product_choice:
                    # kiểm tra product id và order trùng với product update ko
                    delivery_data = product_done[obj_key]['delivery_data']  # list format
                    obj.picked_quantity = product_done[obj_key]['picked_num']
                    obj.delivery_data = delivery_data

                    if (config['is_picking'] and config['is_partial_ship'] and
                            obj.picked_quantity > obj.remaining_quantity):
                        raise serializers.ValidationError(
                            {'detail': _('Products must have picked quantity equal to or less than remaining quantity')}
                        )

                    # config case 1, 2, 3
                    cls.minus_product_warehouse_stock(
                        {'tenant_id': sub.tenant_id, 'company_id': sub.company_id},
                        obj,
                        delivery_data,
                        config
                    )
                else:
                    obj.picked_quantity = product_done[obj_key]['picked_num']
                obj.save(update_fields=['picked_quantity', 'delivery_data'])

    @classmethod
    def create_prod(cls, new_sub, instance):
        # update to current product list of current sub
        prod_arr = []
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=instance
        ):
            delivery_before = obj.delivered_quantity_before + obj.picked_quantity
            remain = obj.delivery_quantity - delivery_before

            new_prod = OrderDeliveryProduct(
                delivery_sub=new_sub,
                product=obj.product,
                uom=obj.uom,
                delivery_quantity=obj.delivery_quantity,
                delivered_quantity_before=delivery_before,
                remaining_quantity=remain,
                ready_quantity=obj.ready_quantity - obj.picked_quantity if obj.ready_quantity > 0 else 0,
                picked_quantity=0,
                order=obj.order,
                delivery_data=obj.delivery_data
            )
            new_prod.before_save()
            prod_arr.append(new_prod)
        OrderDeliveryProduct.objects.bulk_create(prod_arr)

    @classmethod
    def create_new_code(cls):
        delivery = OrderDeliverySub.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "D"
        temper = delivery + 1
        new_code = f"{char}{temper:03d}"
        return new_code

    @classmethod
    def create_new_sub(cls, instance, total_done, case=0):
        new_code = OrderDeliverySubUpdateSerializer.create_new_code()
        delivered = instance.delivered_quantity_before + total_done
        remain = instance.delivery_quantity - delivered
        new_sub = OrderDeliverySub.objects.create(
            company_id=instance.company_id,
            tenant_id=instance.tenant_id,
            order_delivery=instance.order_delivery,
            date_done=None,
            code=new_code,
            previous_step=instance,
            times=instance.times + 1,
            delivery_quantity=instance.delivery_quantity,
            delivered_quantity_before=delivered,
            remaining_quantity=remain,
            ready_quantity=remain if case != 4 else instance.ready_quantity - total_done,
            delivery_data=None,
            is_updated=False,
            state=0 if case == 4 and instance.ready_quantity - total_done == 0 else 1,
            sale_order_data=instance.sale_order_data,
            estimated_delivery_date=instance.estimated_delivery_date,
            actual_delivery_date=instance.actual_delivery_date,
            customer_data=instance.customer_data,
            contact_data=instance.contact_data,
            config_at_that_point=instance.config_at_that_point,
            employee_inherit=instance.employee_inherit
        )
        return new_sub

    @classmethod
    def config_one(cls, instance, total_done, product_done, config):  # none_picking_one_delivery
        if instance.remaining_quantity == total_done:
            # update product and sub date_done
            cls.update_prod(instance, product_done, config)
            instance.date_done = timezone.now()
            instance.state = 2
            instance.is_updated = True
            instance.save(
                update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                               'actual_delivery_date', 'remarks', 'attachments', 'delivery_logistic']
            )
        else:
            raise serializers.ValidationError(
                {
                    'products': _('Done quantity not equal remain quantity!')
                }
            )

    @classmethod
    def config_two(cls, instance, total_done, product_done, config):  # none_picking_many_delivery
        # cho phep giao nhieu lan and tạo sub mới
        cls.update_prod(instance, product_done, config)
        instance.date_done = timezone.now()
        instance.state = 2
        instance.is_updated = True
        instance.save(
            update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                           'actual_delivery_date', 'remarks', 'attachments', 'delivery_logistic']
        )
        if instance.remaining_quantity > total_done:  # still not delivery all items, create new sub
            new_sub = cls.create_new_sub(instance, total_done, 2)
            cls.create_prod(new_sub, instance)
            delivery_obj = instance.order_delivery
            delivery_obj.sub = new_sub
            delivery_obj.save(update_fields=['sub'])
        else:  # delivery all items, not create new sub
            instance.order_delivery.state = 2
            instance.order_delivery.save(update_fields=['state'])
        return True

    @classmethod
    def config_three(cls, instance, total_done, product_done, config):  # many_picking_one_delivery
        order_delivery = instance.order_delivery
        if instance.remaining_quantity == total_done:
            cls.update_prod(instance, product_done, config)
            instance.date_done = timezone.now()
            instance.state = 2
            instance.is_updated = True
            instance.save(
                update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                               'actual_delivery_date', 'remarks', 'attachments', 'delivery_logistic']
            )
            order_delivery.state = 2
            order_delivery.save(update_fields=['state'])
        else:
            raise serializers.ValidationError(
                {
                    'products': _('Done quantity not equal remain quantity!')
                }
            )

    @classmethod
    def config_four(cls, instance, total_done, product_done, config):  # many_picking_many_delivery
        cls.update_prod(instance, product_done, config)
        order_delivery = instance.order_delivery
        if instance.remaining_quantity > total_done:
            new_sub = cls.create_new_sub(instance, total_done, 4)
            cls.create_prod(new_sub, instance)
            order_delivery.sub = new_sub
            # update sub cũ
            instance.date_done = timezone.now()
            instance.is_updated = True
            instance.state = 2
        elif instance.remaining_quantity == total_done:
            instance.date_done = timezone.now()
            instance.is_updated = True
            instance.state = 2
            order_delivery.state = 2
        instance.save(
            update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                           'actual_delivery_date', 'remarks', 'attachments', 'delivery_logistic']
        )
        order_delivery.save(update_fields=['sub', 'state'])

    @classmethod
    def prepare_data_for_logging(cls, instance, validated_product):
        activities_data = []
        for item in instance.delivery_product_delivery_sub.all():
            delivery_data = [temp for temp in validated_product if temp['product_id'] == item.product.id]
            if len(delivery_data) > 0:
                for child in delivery_data[0]['delivery_data']:
                    warehouse = child['warehouse']
                    quantity = child['stock']

                    activities_data.append({
                        'product': item.product,
                        'warehouse': WareHouse.objects.get(id=warehouse),
                        'system_date': instance.date_done,
                        'posting_date': None,
                        'document_date': None,
                        'stock_type': -1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'quantity': quantity,
                        'cost': item.product_unit_price,
                        'value': item.product_unit_price * quantity,
                    })
        ReportInventorySub.logging_when_stock_activities_happened(
            instance.date_done,
            activities_data
        )
        return True

    def update(self, instance, validated_data):
        # declare default object
        CommonFunc.check_update_prod_and_emp(instance, validated_data)

        validated_product = validated_data['products']
        config = instance.config_at_that_point
        if not config:
            get_config = DeliveryConfig.objects.get(company_id=instance.company_id)
            config = {
                "is_picking": get_config.is_picking,
                "is_partial_ship": get_config.is_partial_ship
            }
        is_picking = config['is_picking']
        is_partial = config['is_partial_ship']
        product_done = {}
        total_done = 0
        for item in validated_product:
            prod_key = str(item['product_id']) + "___" + str(item['order'])
            total_done += item['done']
            product_done[prod_key] = {}
            product_done[prod_key]['picked_num'] = item['done']
            product_done[prod_key]['delivery_data'] = item['delivery_data']

        if len(product_done) > 0:
            # update instance info
            self.update_self_info(instance, validated_data)
            # if product_done
            # to do check if not submit product so update common info only
            try:
                with transaction.atomic():
                    self.handle_attach_file(instance, validated_data)
                    if not is_partial and not is_picking:
                        # config 1 (one_picking_one_delivery)
                        self.config_one(instance, total_done, product_done, config)
                    elif is_partial and not is_picking:
                        # config 2 (one_picking_many_delivery)
                        self.config_two(instance, total_done, product_done, config)
                    elif is_picking and not is_partial:
                        # config 3 (many_picking_one_delivery)
                        self.config_three(instance, total_done, product_done, config)
                    else:
                        # config 4 (many_picking_many_delivery)
                        self.config_four(instance, total_done, product_done, config)
            except Exception as err:
                print(err)
                raise err
        else:
            del validated_data['products']
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            instance.order_delivery.employee_inherit = instance.employee_inherit
            instance.order_delivery.save()

        # update sale order
        DeliSODeliveryStatusHandle.main_handle(instance=instance)
        # update opportunity
        DeliOpportunityStageHandle.main_handle(instance=instance)
        # update product
        DeliProductInformationHandle.main_handle(instance=instance, validated_product=validated_product)
        # create final acceptance
        DeliFinalAcceptanceHandle.main_handle(instance=instance, validated_product=validated_product)
        if instance.state == 2:
            self.prepare_data_for_logging(instance, validated_product)

        return instance
