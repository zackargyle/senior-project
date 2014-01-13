from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from app import views

urlpatterns = patterns('app.views',
											 url(r'^games$', views.GameList.as_view(), name='game-list'),
                       url(r'^games/(?P<pk>[0-9]+)$', views.GameDetail.as_view(), name='game-detail'),
											 url(r'^guns$', views.GunList.as_view(), name='gun-list'),
                       url(r'^guns/(?P<pk>[0-9]+)$', views.GunDetail.as_view(), name='gun-detail'),
                       url(r'^players$', views.PlayerList.as_view(), name='player-list'),
                       url(r'^players/(?P<pk>[0-9]+)$', views.PlayerDetail.as_view(), name='player-detail'),
                       url(r'^playerinstances$', views.PlayerInstanceList.as_view(), name='playerInstance-list'),
                       url(r'^playerinstances/(?P<pk>[0-9]+)$', views.PlayerInstanceDetail.as_view(), name='playerInstance-detail'),
                       url(r'^shots$', views.ShotList.as_view(), name='shot-list'),
                       url(r'^shots/(?P<pk>[0-9]+)$', views.ShotDetail.as_view(), name='shot-detail'),
                       url(r'^sync/(?P<pk>[0-9]+)$', views.Sync.as_view(), name='game-sync'),
                       url(r'^teams$', views.TeamList.as_view(), name='team-list'),
                       url(r'^teams/(?P<pk>[0-9]+)$', views.TeamDetail.as_view(), name='team-detail'))

urlpatterns += patterns('',
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token')
)

urlpatterns = format_suffix_patterns(urlpatterns)
