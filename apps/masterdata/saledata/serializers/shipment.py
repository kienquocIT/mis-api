from rest_framework import serializers

from apps.masterdata.saledata.models.shipment import ContainerTypeInfo


class ContainerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerTypeInfo
        fields = (
            'id',
            'code',
            'title',
        )


class ContainerCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    def create(self, validated_data):
        container_obj = ContainerTypeInfo.objects.create(**validated_data)
        return container_obj

    class Meta:
        model = ContainerTypeInfo
        fields = (
            'title'
        )


class ContainerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerTypeInfo
        fields = (
            'id',
            'code',
            'title',
        )


class ContainerUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = ContainerTypeInfo
        fields = (
            'title',
        )
