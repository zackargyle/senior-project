from app.models import *
from app.serializers import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from rest_framework import generics
from rest_framework import permissions
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


class Sync(generics.UpdateAPIView):
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

    return Response({'team_scores': team_scores, 'team': player.team.name, 'score': player.score, 'game_state': game.state})


def getPlayerByFrequency(game, frequency):
    guns = Gun.objects.all().order_by('frequency')
    gun_used = None

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

        player_shooting.score += 2
        player_shooting.save()

        player_hit.score -= 1
        player_hit.save()

'''

lasertag.byu.edu/sync/<game_id>

{
    username: _______,
    shots_fired: ______, #total
    hits_taken: _______, #array of gun frequencies?
}

'''
