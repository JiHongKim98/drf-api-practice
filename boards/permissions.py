from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # GET, HEAD, OPTION 메소드면 True 즉, SAFE_METHODS
        if request.method in SAFE_METHODS:
            return True
        
        # 나머지 메소드에 대해서는 인증된 사용자만 허용
        return request.user and request.user.is_authenticated
    
    
    # view 에서 check_object_permissions 메소드를 통해서 검사
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        return obj.owner == request.user