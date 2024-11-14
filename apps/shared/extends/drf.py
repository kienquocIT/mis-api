from rest_framework.permissions import AllowAny


class AllowAnyDisableOptionsPermission(AllowAny):
    """
    Global permission to disallow all requests for method OPTIONS.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return False
        return True
