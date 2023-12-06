from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS

class IsPostOrIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            # POST 일때만 허용
            return True

        return request.user and request.user.is_authenticated
