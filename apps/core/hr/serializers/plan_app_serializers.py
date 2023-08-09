from rest_framework import serializers


class PlanAppSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField()
    application = serializers.ListSerializer(
        child=serializers.UUIDField(), required=False
    )

    @classmethod
    def convert_to_simple(cls, plan_app):
        new_plan_app = []
        for item in plan_app:
            tmp = {}
            for key, value in item.items():
                if key == 'plan':
                    tmp['plan'] = str(value)
                elif key == 'application':
                    tmp['application'] = [str(x) for x in value]
            new_plan_app.append(tmp)
        return {
            x['plan']: x
            for x in new_plan_app
        }
