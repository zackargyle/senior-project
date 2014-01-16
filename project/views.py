from django.shortcuts import render_to_response
from api.models import *

def index(request):
		games = Game.objects.all().order_by('-time_played')
		if len(games) > 9:
			games = games[:9]
		return render_to_response('homepage.html', {'games': games})

def review(request, pk):

		game = Game.objects.get(pk=pk)
		teams = Team.objects.filter(game=game)
		playerInstances = PlayerInstance.objects.filter(game=game).order_by('-score')

		for team in teams:
			players = PlayerInstance.objects.filter(team=team).order_by('-score')
			for player in players:
				if player not in playerInstances:
					playerInstances.push(player)

		return render_to_response('gamereview.html', {'game': game, 'teams': teams, 'players': playerInstances})

def newgame(request):
		return render_to_response('newgame.html', {'modes': Game.getModes()})