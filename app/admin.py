from django.contrib import admin
from app.models import *


class GameAdmin(admin.ModelAdmin):
	pass

class GunAdmin(admin.ModelAdmin):
	pass

class PlayerAdmin(admin.ModelAdmin):
    pass

class PlayerInstanceAdmin(admin.ModelAdmin):
	pass

class ShotAdmin(admin.ModelAdmin):
	pass

class TeamAdmin(admin.ModelAdmin):
    pass


''' Register Admin layouts into django'''
admin.site.register(Game, GameAdmin)
admin.site.register(Gun, GunAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerInstance, PlayerInstanceAdmin)
admin.site.register(Shot, ShotAdmin)
admin.site.register(Team, TeamAdmin)
