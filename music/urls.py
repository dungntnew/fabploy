from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'music'

urlpatterns = [

    # /music/
    url(r'^$', views.IndexView.as_view(), name='index'),

    # /music/register
    url(r'^register/$', views.UserFormView.as_view(), name='register'),

    # /music/71/
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # /music/album/add/
    url(r'^album/add/$', views.AlbumCreate.as_view(), name='album-add'),

    # /music/album/1/
    url(r'^album/(?P<pk>[0-9]+)/$', views.AlbumUpdate.as_view(), name='album-update'),

    # /music/album/1/delete/
    url(r'^album/(?P<pk>[0-9]+)/delete/$', views.AlbumDelete.as_view(), name='album-delete'),

    # /music/71/favorite
    url(r'^(?P<album_id>[0-9]+)/favorite/$', views.favorite, name='favorite'),

    # rest
    url(r'^api/albums/$', views.AlbumList.as_view(), name='album-list'),
    url(r'^api/albums/(?P<pk>[0-9]+)/$', views.AlbumDetail.as_view(), name='album-one'),

]

urlpatterns = format_suffix_patterns(urlpatterns)