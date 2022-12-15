from rest_framework import serializers

from apps.core.account.models import User


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'username',
            'email',
            'phone',
        )

    def get_full_name(self, obj):
        return User.get_full_name(obj, 2)
