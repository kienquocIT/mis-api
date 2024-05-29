from rest_framework import serializers

from apps.core.diagram.models import DiagramDocument, DiagramPrefix, DiagramSuffix

DIAGRAM_APP_CONFIG = {
    'saleorder.saleorder': {
        'list_app_prefix': ['quotation.quotation'],
        'list_app_suffix': [
            'purchasing.purchaserequest', 'purchasing.purchaseorder',
            'inventory.goodsreceipt', 'delivery.orderdeliverysub',
        ],
    }
}


class DiagramPrefixListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiagramPrefix
        fields = (
            'id',
            'title',
            'code',
            'app_code',
            'doc_id',
            'doc_data',
        )


class DiagramSuffixListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiagramSuffix
        fields = (
            'id',
            'title',
            'code',
            'app_code',
            'doc_id',
            'doc_data',
        )


class DiagramListSerializer(serializers.ModelSerializer):
    prefix = serializers.SerializerMethodField()
    suffix = serializers.SerializerMethodField()

    class Meta:
        model = DiagramDocument
        fields = (
            'id',
            'title',
            'code',
            'app_code',
            'doc_id',
            'doc_data',
            'prefix',
            'suffix',
        )

    @classmethod
    def get_prefix_suffix_data(cls, app_code, list_record, type_get=0):
        result = {}
        config = DIAGRAM_APP_CONFIG[app_code]
        list_app_config = config.get('list_app_prefix', [])
        if type_get == 1:
            list_app_config = config.get('list_app_suffix', [])
        for app_config in list_app_config:
            app_record_data = []
            for record in list_record:
                if record.get('app_code', '') == app_config:
                    app_record_data.append(record.get('doc_data', {}))
            result.update({str(app_config): app_record_data})
        return result

    @classmethod
    def get_prefix(cls, obj):
        list_prefix = DiagramPrefixListSerializer(obj.diagram_prefix_diagram_document.all(), many=True).data
        return cls.get_prefix_suffix_data(app_code=obj.app_code, list_record=list_prefix, type_get=0)

    @classmethod
    def get_suffix(cls, obj):
        list_suffix = DiagramSuffixListSerializer(obj.diagram_suffix_diagram_document.all(), many=True).data
        return cls.get_prefix_suffix_data(app_code=obj.app_code, list_record=list_suffix, type_get=1)
