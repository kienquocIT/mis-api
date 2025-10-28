from rest_framework import serializers
from deepdiff import DeepDiff


__all__ = [
    'ServiceOrderDiffSerializer',
]


class ServiceOrderDiffSerializer(serializers.Serializer):
    """
    Serializer for comparing two versions of a ServiceOrder document using DeepDiff.
    Returns the differences between the current state and a previous snapshot.
    """
    current_snapshot = serializers.JSONField(help_text="Current ServiceOrder snapshot")
    previous_snapshot = serializers.JSONField(help_text="Previous ServiceOrder snapshot for comparison")
    differences = serializers.SerializerMethodField(help_text="Detailed differences between snapshots")
    summary = serializers.SerializerMethodField(help_text="Summary of changes")

    def get_differences(self, obj) -> dict:
        """
        Compare current and previous snapshots using DeepDiff.
        Returns a dictionary with changes categorized by type.
        """
        current = obj.get('current_snapshot', {})
        previous = obj.get('previous_snapshot', {})

        if not previous:
            return {
                'message': 'No previous snapshot found for comparison',
                'current_snapshot': current
            }

        # Use DeepDiff to get detailed differences
        diff = DeepDiff(
            previous,
            current,
            ignore_order=False,
            verbose_level=2,
            view='tree'
        )

        # Convert to dictionary format for JSON serialization
        result = {}
        if diff:
            for key, value in diff.items():
                result[key] = [
                    {
                        'path': str(item.path()),
                        'old_value': item.t1 if hasattr(item, 't1') else None,
                        'new_value': item.t2 if hasattr(item, 't2') else None,
                    }
                    for item in value
                ]
        else:
            result['message'] = 'No differences found between snapshots'

        return result

    def get_summary(self, obj) -> dict:
        """
        Generate a summary of changes.
        Returns counts of different types of changes.
        """
        current = obj.get('current_snapshot', {})
        previous = obj.get('previous_snapshot', {})

        if not previous:
            return {
                'status': 'first_snapshot',
                'message': 'This is the first snapshot of the document'
            }

        diff = DeepDiff(
            previous,
            current,
            ignore_order=False,
            verbose_level=2,
        )

        summary = {
            'total_changes': len(diff) if diff else 0,
            'values_changed': len(diff.get('values_changed', {})) if diff else 0,
            'items_added': len(diff.get('items_added', {})) if diff else 0,
            'items_removed': len(diff.get('items_removed', {})) if diff else 0,
            'type_changes': len(diff.get('type_changes', {})) if diff else 0,
            'iterable_item_added': len(diff.get('iterable_item_added', {})) if diff else 0,
            'iterable_item_removed': len(diff.get('iterable_item_removed', {})) if diff else 0,
            'repetition_change': len(diff.get('repetition_change', {})) if diff else 0,
        }

        return summary

    def to_representation(self, instance):
        """
        Override to ensure proper serialization of diff results.
        """
        # Convert diff results to JSON-serializable format
        representation = super().to_representation(instance)
        return representation
