from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owners of an object (the seller) to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user and request.user.is_staff:
            return True

        if hasattr(obj, 'seller'):
            if hasattr(obj.seller, 'user') and obj.seller.user:
                return obj.seller.user == request.user

        return False


class IsAdminOnly(permissions.BasePermission):
    """
    Strict permission: Only authenticated staff / administrator users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Read allowed to all; write/modify allowed only to staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsUnlockParticipant(permissions.BasePermission):
    """
    Only allows access to the buyer or seller associated with a ContactUnlock.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return False

        return obj.buyer == user_profile or obj.seller == user_profile
