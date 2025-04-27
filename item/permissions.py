# item/permissions.py

from rest_framework import permissions

class IsOwnerPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.shop == request.user.shop
