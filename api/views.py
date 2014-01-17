from api.models import *
from api.serializers import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response


class GameList(generics.ListCreateAPIView):
    """List all addresses or create a new Game"""
    permission_classes = (permissions.IsAuthenticated,)
    model = Game
    serializer_class = GameSerializer


class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Game."""
    permission_classes = (permissions.IsAuthenticated,)
    model = Game
    serializer_class = GameSerializer


class GunList(generics.ListCreateAPIView):
    """List all addresses or create a new Gun"""
    permission_classes = (permissions.IsAuthenticated,)
    model = Gun
    serializer_class = GunSerializer


class GunDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Gun."""
    permission_classes = (permissions.IsAuthenticated,)
    model = Gun
    serializer_class = GunSerializer


class PlayerList(generics.ListCreateAPIView):
    """List all addresses or create a new Player"""
    permission_classes = (permissions.IsAuthenticated,)
    model = Player
    serializer_class = PlayerSerializer


class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Player."""
    permission_classes = (permissions.IsAuthenticated,)
    model = Player
    serializer_class = PlayerSerializer


class PlayerInstanceList(generics.ListCreateAPIView):
    """List all addresses or create a new PlayerInstance"""
    permission_classes = (permissions.IsAuthenticated,)
    model = PlayerInstance
    serializer_class = PlayerInstanceSerializer


class PlayerInstanceDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an PlayerInstance."""
    permission_classes = (permissions.IsAuthenticated,)
    model = PlayerInstance
    serializer_class = PlayerInstanceSerializer


class ShotList(generics.ListCreateAPIView):
    """List all addresses or create a new Shot"""
    permission_classes = (permissions.IsAuthenticated,)
    model = Shot
    serializer_class = ShotSerializer


class ShotDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Shot."""
    permission_classes = (permissions.IsAuthenticated,)
    model = Shot
    serializer_class = ShotSerializer


class TeamList(generics.ListCreateAPIView):
    """List all addresses or create a new Team"""
    permission_classes = (permissions.IsAuthenticated,)
    model = Team
    serializer_class = TeamSerializer


class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Team."""
    permission_classes = (permissions.IsAuthenticated,)
    model = Team
    serializer_class = TeamSerializer

class GameStart(APIView):
    ''' Start game with posted game data '''
    permission_classes = ()

    def post(self, request):
        data = request.DATA
        players = data.players
        teams = data.teams
        print data
        print players
        print teams

        game = Game(mode=data.mode, state="PLAYING", time_limit=data.time_limit, score_limit=data.score_limit)
        game.save()
        print game

        if teams is not None:
            setupTeams(teams, players, game)
        else:
            setupPlayers(players, game)

        return Response({'game': game})

    def setupTeams(teams, players, game):
        for team_name in teams:
            team = Team(name=team_name, game=game, score=0)
            team.save()
            print team
            for p in players:
                if p.team == team_name:
                    player = Player.objects.get_or_create(username=p.username)
                    player.save()
                    instance = PlayerInstance(gun=p.gun, player=player, team=team, game=game, num_shots=0, score=0)
                    instance.save()
                    print instance

    def setupPlayersOnly(players, game):
        for p in players:
            player = Player.objects.get_or_create(username=p.username)
            player.save()
            print player
            instance = PlayerInstance(gun=p.gun, player=player, team=team, game=game, num_shots=0, score=0)
            instance.save()
            print instance


class Sync(generics.UpdateAPIView):
    ''' Sync game data with posted data, return game data '''
    permission_classes = (permissions.IsAuthenticated,)
    model = Game

    def put(self, request, pk, format=None):
        game = Game.objects.get(id=pk)
        data = request.DATA

        try:
            player = Player.objects.get(username=data["username"])
            player_instance = PlayerInstance.objects.get(game=game, player=player)
            player_instance.num_shots = data["shots_fired"]
            player_instance.save()

            updateShots(game, data["hits_taken"], player_instance)

            return getUpdates(game, player_instance)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()


def getUpdates(game, player):
    teams = Team.objects.filter(game=game)
    team_scores = []

    for team in teams:
        team_members = PlayerInstance.objects.filter(team=team)
        team_score = 0

        for member in team_members:
            team_score += member.score

        score = {'name': team.name, 'score': team_score if (team_score > 0) else 0}
        team_scores.append(score)

    team = player.team
    team_name = ""
    if team is not None:
        team_name = team.name

    return Response({'team_scores': team_scores, 'team': team_name, 'score': player.score, 'game_state': game.state})


def getPlayerByFrequency(game, frequency):
    guns = Gun.objects.all().order_by('frequency')
    gun_used = guns[0]

    # Get the gun that was used to shoot the player
    for gun in guns:
        if gun.frequency < frequency:
            gun_used = gun
        elif (gun.frequency - frequency) < (frequency - gun_used.frequency):
            gun_used = gun

    # Return the player using the gun
    return PlayerInstance.objects.get(game=game, gun=gun_used)

def updateShots(game, hits, player_hit):
    for hit in hits:
        player_shooting = getPlayerByFrequency(game, hit)

        shot = Shot(game=game, shooter=player_shooting, target=player_hit)
        shot.save()

        player_shooting.score += 20
        player_shooting.save()

        player_hit.score -= 10
        player_hit.save()

'''

lasertag.byu.edu/sync/<game_id>

{
    "username": "zack",
    "shots_fired": 15,
    "hits_taken": [110000,110000,110000,120000,130000,130000]
}

'''
