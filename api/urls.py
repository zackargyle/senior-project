from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = patterns('api.views',
                       url(r'^games/(?P<pk>[0-9]+)$', views.GameDetail.as_view(), name='game-detail'),
                       url(r'^games$', views.GameList.as_view(), name='game-data'),
											 url(r'^guns$', views.GunList.as_view(), name='gun-list'),
                       url(r'^join/(?P<pk>[0-9]+)$', views.GameJoin.as_view(), name='game-join'),
                       url(r'^stats/(?P<username>[\w|\W]+)$', views.PlayerStats.as_view(), name='player-stats'),
                       url(r'^sync/(?P<pk>[0-9]+)$', views.Sync.as_view(), name='game-sync'),
                       url(r'^shots$', views.ShotList.as_view(), name='shot-list'),
                       url(r'^teams$', views.TeamList.as_view(), name='team-list'),
                       url(r'^start$', views.GameStart.as_view(), name='game-start'))

urlpatterns += patterns('',
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token')
)

urlpatterns = format_suffix_patterns(urlpatterns)
