from django.conf.urls import url, include

from apps.accounts.views import ObtainJSONWebTokenClearBrusafeToken
from apps.accounts.views_jwt import RefreshJwtView, VerifyJwt

urlpatterns = [
    url('^accounts/', include('apps.accounts.urls', namespace='accounts')),
    url('^patients/', include('apps.patients.urls', namespace='patients')),
    url('^messages/', include('apps._messages.urls', namespace='messages')),
    url('^tasks/', include('apps.tasks.urls', namespace='tasks')),
    url('^units/', include('apps.units.urls', namespace='units')),
    url('^vitals/', include('apps.vitals.urls', namespace='vitals')),
    url('^wounds/', include('apps.wounds.urls', namespace='wounds')),
    url('^medications/', include('apps.medications.urls', namespace='medications')),
    url('^diagnostics/', include('apps.diagnostics.urls', namespace='diagnostics')),
    url('^journal/', include('apps.journal.urls', namespace='journal')),
    url('^evaluations/', include('apps.evaluations.urls', namespace='evaluations')),
    url('^brusafe/', include('apps.brusafe.urls', namespace='brusafe')),
    url('^reports/', include('apps.reports.urls', namespace='reports')),
    url('^wish/', include('apps.wish.urls', namespace='wish')),
    url('api-token-auth/', ObtainJSONWebTokenClearBrusafeToken.as_view(), name='login'),
    url('api-token-verify/', VerifyJwt.as_view(), name='verify'),
    url('api-token-refresh/', RefreshJwtView.as_view()),
    url('^documents/', include('apps.documents.urls', namespace='documents')),
]
