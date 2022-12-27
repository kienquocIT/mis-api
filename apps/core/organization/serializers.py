# from rest_framework import serializers
#
# from apps.core.hr.models import Employee
# from apps.core.organization.models import GroupLevel, Group, GroupEmployee
#
#
# # Group Level Serializer
# class GroupLevelListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupLevel
#         fields = (
#             'id',
#             'level',
#             'description',
#             'first_manager_description',
#             'second_manager_description',
#             'user_created',
#             'user_modified',
#         )
#
#
# class GroupLevelDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupLevel
#         fields = (
#             'id',
#             'level',
#             'description',
#             'first_manager_description',
#             'second_manager_description',
#             'user_created',
#             'user_modified',
#         )
#
#
# class GroupLevelCreateSerializer(serializers.ModelSerializer):
#     level = serializers.IntegerField()
#     description = serializers.CharField(max_length=500)
#
#     class Meta:
#         model = GroupLevel
#         fields = (
#             'level',
#             'description',
#             'first_manager_description',
#             'second_manager_description',
#         )
#
#     def create(self, validated_data):
#         GroupLevel.objects.create(**validated_data)
#
#
# class GroupLevelUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupLevel
#         fields = (
#             'level',
#             'description',
#             'first_manager_description',
#             'second_manager_description',
#         )
#
#     def update(self, instance, validated_data):
#         for key, value in validated_data.items():
#             setattr(instance, key, value)
#         instance.save()
#
#
# # Group Serializer
# class GroupListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = (
#             'id',
#             'group_level',
#             'parent_n',
#             'description',
#             'group_employee',
#             'first_manager',
#             'first_manager_title',
#             'second_manager',
#             'second_manager_title',
#             'user_created',
#             'user_modified',
#         )
#
#
# class GroupDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = (
#             'id',
#             'group_level',
#             'parent_n',
#             'description',
#             'group_employee',
#             'first_manager',
#             'first_manager_title',
#             'second_manager',
#             'second_manager_title',
#             'user_created',
#             'user_modified',
#         )
#
#
# class GroupCreateSerializer(serializers.ModelSerializer):
#     group_level = serializers.UUIDField()
#     parent_n = serializers.UUIDField(required=False)
#     group_employee = serializers.ListField(
#         child=serializers.UUIDField(required=False),
#         required=False
#     )
#     first_manager = serializers.UUIDField()
#     second_manager = serializers.UUIDField(required=False)
#
#     class Meta:
#         model = Group
#         fields = (
#             'group_level',
#             'parent_n',
#             'title',
#             'code',
#             'description',
#             'group_employee',
#             'first_manager',
#             'first_manager_title',
#             'second_manager',
#             'second_manager_title'
#         )
#
#     def validate_group_level(self, value):
#         try:
#             return GroupLevel.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Group level does not exist.")
#
#     def validate_parent_n(self, value):
#         try:
#             return Group.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Group does not exist.")
#
#     def validate_group_employee(self, value):
#         if isinstance(value, list):
#             pass
#
#     def validate_first_manager(self, value):
#         try:
#             return Employee.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Employee does not exist.")
#
#     def validate_second_manager(self, value):
#         try:
#             return Employee.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Employee does not exist.")
#
#     def create(self, validated_data):
#         # create Group
#         group = Group.objects.create(**validated_data)
#         # create Group Employee
#         if 'group_employee' in validated_data:
#             bulk_info = []
#             for employee in validated_data['group_employee']:
#                 bulk_info.append(GroupEmployee(
#                     group=group,
#                     employee_id=employee
#                 ))
#             if bulk_info:
#                 GroupEmployee.object_normal.bulk_create(bulk_info)
#
#         return group
#
#
# class GroupUpdateSerializer(serializers.ModelSerializer):
#     group_level = serializers.UUIDField(required=False)
#     parent_n = serializers.UUIDField(required=False)
#     group_employee = serializers.ListField(
#         child=serializers.UUIDField(required=False),
#         required=False
#     )
#     first_manager = serializers.UUIDField(required=False)
#     second_manager = serializers.UUIDField(required=False)
#
#     class Meta:
#         model = Group
#         fields = (
#             'group_level',
#             'parent_n',
#             'title',
#             'code',
#             'description',
#             'group_employee',
#             'first_manager',
#             'first_manager_title',
#             'second_manager',
#             'second_manager_title'
#         )
#
#     def validate_group_level(self, value):
#         try:
#             return GroupLevel.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Group level does not exist.")
#
#     def validate_parent_n(self, value):
#         try:
#             return Group.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Group does not exist.")
#
#     def validate_group_employee(self, value):
#         if isinstance(value, list):
#             pass
#
#     def validate_first_manager(self, value):
#         try:
#             return Employee.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Employee does not exist.")
#
#     def validate_second_manager(self, value):
#         try:
#             return Employee.objects.get(id=value)
#         except Exception as e:
#             raise serializers.ValidationError("Employee does not exist.")
#
#     def update(self, instance, validated_data):
#         # update Group
#         for key, value in validated_data.items():
#             setattr(instance, key, value)
#         instance.save()
#         # delete old & update Group Employee
#         if 'group_employee' in validated_data:
#             group_employee_old = GroupEmployee.object_normal.filter(
#                 group=instance
#             )
#             if group_employee_old:
#                 group_employee_old.delete()
#             bulk_info = []
#             for employee in validated_data['group_employee']:
#                 bulk_info.append(GroupEmployee(
#                     group=instance,
#                     employee_id=employee
#                 ))
#             if bulk_info:
#                 GroupEmployee.object_normal.bulk_create(bulk_info)
#
#         return instance
#
#
#
#
