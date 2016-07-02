from django.conf.urls import url

from . import views

app_name = 'music'

urlpatterns = [

    # /music/
    url(r'^$', views.IndexView.as_view(), name='index'),

    # /music/71/
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # /music/71/favorite
    url(r'^(?P<album_id>[0-9]+)/favorite/$', views.favorite, name='favorite')
]
