from rest_framework.permissions import DjangoModelPermissions

from apps.brusafe.core import BrusafeConnector


class LifeLinePermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        perms = super().has_permission(request, view)
        if not perms and request.method in ['DELETE', 'PATCH', 'PUT']:
            instance = view.get_object()
            user = self._get_user(instance)
            return user and user.pk == request.user.pk
        return perms

    @staticmethod
    def _get_user(instance):
        return getattr(instance, 'user', None) or getattr(instance, 'creator', None)


class BrusafePermissions(DjangoModelPermissions):

    def has_permission(self, request, view):
        if BrusafeConnector.is_session_token_set(request) and not BrusafeConnector.is_session_token_expired(request):
            view.api_headers['Authorization'] = request.session['brusafe_token']
            return True
