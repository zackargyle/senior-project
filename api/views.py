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
    permission_classes = ()
    authentication_classes = ()
    model = Game
    serializer_class = GameSerializer


class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Game."""
    permission_classes = ()
    authentication_classes = ()
    model = Game
    serializer_class = GameSerializer


class GunList(generics.ListCreateAPIView):
    """List all addresses or create a new Gun"""
    permission_classes = ()
    authentication_classes = ()
    model = Gun
    serializer_class = GunSerializer


class GunDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Gun."""
    permission_classes = ()
    authentication_classes = ()
    model = Gun
    serializer_class = GunSerializer


class PlayerList(generics.ListCreateAPIView):
    """List all addresses or create a new Player"""
    permission_classes = ()
    authentication_classes = ()
    model = Player
    serializer_class = PlayerSerializer


class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Player."""
    permission_classes = ()
    authentication_classes = ()
    model = Player
    serializer_class = PlayerSerializer


class PlayerInstanceList(generics.ListCreateAPIView):
    """List all addresses or create a new PlayerInstance"""
    permission_classes = ()
    model = PlayerInstance
    serializer_class = PlayerInstanceSerializer


class PlayerInstanceDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an PlayerInstance."""
    permission_classes = ()
    authentication_classes = ()
    model = PlayerInstance
    serializer_class = PlayerInstanceSerializer


class ShotList(generics.ListCreateAPIView):
    """List all addresses or create a new Shot"""
    permission_classes = ()
    authentication_classes = ()
    model = Shot
    serializer_class = ShotSerializer


class ShotDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Shot."""
    permission_classes = ()
    authentication_classes = ()
    model = Shot
    serializer_class = ShotSerializer


class TeamList(generics.ListCreateAPIView):
    """List all addresses or create a new Team"""
    permission_classes = ()
    authentication_classes = ()
    model = Team
    serializer_class = TeamSerializer


class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an Team."""
    permission_classes = ()
    authentication_classes = ()
    model = Team
    serializer_class = TeamSerializer


class GameJoin(generics.UpdateAPIView):
    permission_classes = ()
    authentication_classes = ()
    model = Game

    '''
        lasertag.byu.edu/join/<game_id>
        {
            "team": null,
            "username": "psycho",
            "gun": 4
        }
    '''

    def put(self, request, pk, format=None):
        data = request.DATA
        game = Game.objects.get(id=pk)

        team = None
        try:
            team = Team.objects.get(id=data["team"])
        except ObjectDoesNotExist:
            pass

        gun = None
        try:
            gun = Gun.objects.get(id=data["gun"])
        except ObjectDoesNotExist:
            pass

        player = None
        try:
            player = Player.objects.get(username=data["username"])
        except ObjectDoesNotExist:
            player = Player(username=data["username"])
            player.save()

        instance = PlayerInstance(gun=gun, player=player, team=team, game=game, num_shots=0, score=0)
        instance.save()

        return Response({'game': game.id})


class GameStart(APIView):
    permission_classes = ()
    authentication_classes = ()

    '''
        lasertag.byu.edu/start
        {
            "mode": "TEAMS",
            "players": [{
                    "gun": 3,
                    "team": "googlers",
                    "username": "mac the knife"
                },{
                    "gun": 4,
                    "team": "bingers",
                    "username": "jack the ripper"
                }
            ],
            "teams": ["googlers", "bingers"],
            "score_limit": null,
            "time_limit": null
        }
    '''

    def post(self, request):
        data = request.DATA
        players = data["players"]
        teams = data["teams"]

        game = Game(mode=data["mode"], state="PLAYING", time_limit=data["time_limit"], score_limit=data["score_limit"])
        game.save()

        if data["mode"] == "TEAMS":
            setupTeamsAndPlayers(teams, players, game)
        else:
            setupPlayersOnly(players, game)

        return Response({'game': game.id})

def setupTeamsAndPlayers(teams, players, game):
    for team_name in teams:
        team = Team(name=team_name, game=game, score=0)
        team.save()

        for p in players:
            if p["team"] == team_name:
                player = None
                try:
                    player = Player.objects.get(username=p["username"])
                except ObjectDoesNotExist:
                    player = Player(username=p["username"])
                    player.save()
                gun = Gun.objects.get(pk=p["gun"])
                instance = PlayerInstance(gun=gun, player=player, team=team, game=game, num_shots=0, score=0)
                instance.save()

def setupPlayersOnly(players, game):
    for p in players:
        player = None
        try:
            player = Player.objects.get(username=p["username"])
        except ObjectDoesNotExist:
            player = Player(username=p["username"])
            player.save()

        gun = Gun.objects.get(pk=p["gun"])

        instance = PlayerInstance(gun=gun, player=player, team=None, game=game, num_shots=0, score=0)
        instance.save()


class Sync(generics.UpdateAPIView):
    permission_classes = ()
    authentication_classes = ()
    model = Game

    '''
        lasertag.byu.edu/sync/<game_id>
        {
            "gun": 3,
            "shots_fired": 15,
            "hits_taken": [4,4,4]
        }
    '''

    def put(self, request, pk, format=None):
        game = Game.objects.get(id=pk)
        data = request.DATA
        print data

        try:
            player_instance = PlayerInstance.objects.get(game=game, gun__id=data["gun"])
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
        if player_hit.score <= 0:
            player_hit.score = 0
        player_hit.save()
