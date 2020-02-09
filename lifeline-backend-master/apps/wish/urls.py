from django.conf.urls import url

from apps.wish.views import WishView

urlpatterns = [
    url('upload/', WishView.as_view(), name='wish')
]
