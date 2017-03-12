from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.balance, name='balance'),
    url(r'^spending$', views.spending, name='spending'),
]
