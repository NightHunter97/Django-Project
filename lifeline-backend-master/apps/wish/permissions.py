from django.core.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from apps.wish.models import HL7System


class WishPermission(BasePermission):
    """
    The request is user allowed to use wish connector
    """
    def has_permission(self, user, view=None):
        return user.groups.filter(permissions__codename='wish_connector').exists() or user.is_superuser


class OsAuthenticated(BasePermission):
    """
    The request is operating system is allowed to use wish connector
    """
    def has_permission(self, request, view=None):
        try:
            return HL7System.objects.filter(os=request.META['HTTP_AUTHORIZATION']).exists()
        except (KeyError, ValidationError):
            return False
