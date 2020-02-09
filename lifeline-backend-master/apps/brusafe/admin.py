from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
import urllib.parse

from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from apps.brusafe.core import BrusafeConnector
from apps.brusafe.models import Connector, Relation


@admin.register(Connector)
class BrusafeAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">add_to_queue</i>'
    change_list_template = 'brusafe/authentication.html'
    api_template = 'brusafe/api.html'
    list_display = ('user', 'authenticated', 'expiration', 'created')
    readonly_fields = ('user', 'authenticated', 'expiration')
    search_fields = ('user__email', )

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        return [url(r'api/', self.api_view, name='brusafe_connector_api')] + super().get_urls()

    def api_view(self, request):
        if not BrusafeConnector.is_session_token_set(request) or BrusafeConnector.is_session_token_expired(request):
            return HttpResponseRedirect(reverse('admin:brusafe_connector_changelist'))
        context = {'token': jwt_encode_handler(jwt_payload_handler(request.user))}
        list_view = self.changelist_view(request, context)
        list_view.template_name = self.api_template
        return list_view

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        code = request.GET.get('code')
        state = request.GET.get('state')
        if request.GET.get('brusafe') == 'logout' or BrusafeConnector.is_session_token_expired(request):
            BrusafeConnector.flush_session(request)
            return HttpResponseRedirect(request.path)
        elif code and state:
            BrusafeConnector().connect(code, request)
            return HttpResponseRedirect(request.path)
        params = {
            'response_type': 'code',
            'client_id': settings.BRUSAFE_CLIENT_ID,
            'redirect_uri': settings.BRUSAFE_REDIRECT_URL
        }
        extra_context['auth'] = f'{settings.BRUSAFE_HOST}/{BrusafeConnector.auth_url}?{urllib.parse.urlencode(params)}'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Relation)
class BrusafeAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">code</i>'
    readonly_fields = ('user', 'patient')

    def has_add_permission(self, request):
        return False
