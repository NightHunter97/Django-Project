from django.conf.urls import url

from apps.units.views import UnitsView, DashboardView, TasksView

urlpatterns = [
    url('^list/', UnitsView.as_view({'get': 'list'}), name='units'),
    url('^tasks/', TasksView.as_view(), name='tasks'),
    url('^dashboard/', DashboardView.as_view({'get': 'list'}), name='dashboard')
]
