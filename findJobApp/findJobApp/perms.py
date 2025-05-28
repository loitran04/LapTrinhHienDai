from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class CommentOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and request.user == obj.user

class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_admin=getattr(request.user,'role',None) =='admin'
        is_superu=request.user.is_superuser
        is_owner = obj ==request.user

        return is_admin or is_superu or is_owner
class IsEmployerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.job.employer_id.user == request.user

class IsCandidateOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.candidate.user == request.user
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'