"""
API Permissions
Custom permission classes for API endpoints
"""

from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    """
    Permission class for internal management APIs
    Only allows access to admin users and staff
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and is admin or staff
        """
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class AllowAny(BasePermission):
    """
    Permission class for public APIs
    Allows access to anyone (no authentication required)
    """
    
    def has_permission(self, request, view):
        """
        Allow all requests
        """
        return True
