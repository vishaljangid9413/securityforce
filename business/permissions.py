from rest_framework import permissions

class IsBusinessAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a business admin
        return request.user and request.user.is_authenticated and request.user.business.role == 'admin'

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a manager or business admin
        return request.user and request.user.is_authenticated and request.user.business.role in ['admin', 'manager']

class IsFieldOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a field officer, manager, or business admin
        return request.user and request.user.is_authenticated and request.user.business.role in ['admin', 'manager', 'field_officer']
