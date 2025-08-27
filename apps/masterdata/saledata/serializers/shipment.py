from rest_framework import serializers

from apps.masterdata.saledata.models.shipment import ContainerTypeInfo, PackageTypeInfo


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
            'title',
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


class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageTypeInfo
        fields = (
            'id',
            'code',
            'title'
        )


class PackageCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    def create(self, validated_data):
        package_obj = PackageTypeInfo.objects.create(**validated_data)
        return package_obj

    class Meta:
        model = PackageTypeInfo
        fields = (
            'title',
        )


class PackageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageTypeInfo
        fields = (
            'id',
            'code',
            'title',
        )


class PackageUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = PackageTypeInfo
        fields = (
            'title',
        )
