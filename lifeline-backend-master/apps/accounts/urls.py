from django.conf.urls import url
from django.contrib.auth.views import PasswordResetConfirmView
from rest_auth import views as rest_views

from apps.accounts.views import UsersViewSet, UserLanguageView, UserActivityView, UserCommonActivityView

urlpatterns = [
    url('update-profile', UserLanguageView.as_view({'post': 'create'}), name='update_profile'),
    url('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url('^password/reset/$', rest_views.PasswordResetView.as_view(), name='rest_password_reset'),
    url('^password/reset/confirm/$', rest_views.PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    url('^activity/$', UserActivityView.as_view(), name='user_activity'),
    url('^common/activity/$', UserCommonActivityView.as_view(), name='common_user_activity'),
    url('^$', UsersViewSet.as_view({'get': 'list'}), name='users')

]
