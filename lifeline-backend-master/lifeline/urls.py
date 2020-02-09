"""lifeline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import render
from django.views.generic import RedirectView

from lifeline.swagger import get_swagger_view


def handler404(request):
    return render(request, '404.html')


urlpatterns = [
    url('api/v1/', include('lifeline.api_v1_urls')),
    url('docs/', get_swagger_view(title='Lifeline API'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    url('admin/', include(admin.site.urls)),
    url('^$', RedirectView.as_view(url='admin/', permanent=False), name='index'),
    prefix_default_language=False
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
