# Setting Permissions
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to grant full control to Admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'

class IsStandardUser(permissions.BasePermission):
    """
    Custom permission to allow standard users limited access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'STANDARD'

class IsGuestUser(permissions.BasePermission):
    """
    Custom permission for guests to view only, without action.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'GUEST'

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Custom object-level permission to allow users to modify only their own data.
    Admins have access to all users.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN' or obj == request.user

