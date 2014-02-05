from api.models import *
from api.serializers import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


class ShotList(generics.ListAPIView):
    model = Shot
    serializer_class = ShotSerializer


class PlayerStats(APIView):
    def get(self, request, username):
        player_ = {'instances': [], 'score_total': 0, 'high_score': 0, 'num_shots': 0}
        try:
            player = Player.objects.get(username=username)
            instances = PlayerInstance.objects.filter(player=player)

            for instance in instances:
                team_ = None

                if instance.team is not None:
                    team_ = instance.team.id

                frenemies = PlayerInstance.objects.filter(game=instance.game).order_by('-score')

                rank = None
                for index, dude in enumerate(frenemies):
                    if dude == instance:
                        rank = index

                instance_ = {
                    'time': instance.game.time_played, 
                    'team': team_, 
                    'gun': instance.gun.id, 
                    'num_shots': instance.num_shots, 
                    'score': instance.score,
                    'rank': rank + 1
                }

                player_['instances'].append(instance_)
                player_['score_total'] += instance.score
                player_['num_shots'] += instance.num_shots

                if instance.score > player_['high_score']:
                    player_['high_score'] = instance.score

            return Response(player_)
        except ObjectDoesNotExist:
            return Response("No player with that username")

class GunList(APIView):
    ''' Return a list of guns not currently in use '''
    def get(self, request):
        guns = Gun.objects.all()
        games = Game.objects.filter(state='PLAYING')

        for game in games:
            players = PlayerInstance.objects.filter(game=game)

            for player in players:
                guns = guns.exclude(id=player.gun.id)

        guns_ = []
        for gun in guns:
            guns_.append({'id': gun.id, 'frequency': gun.frequency})

        return Response(guns_)


def getGameData(game):
    game_ = { 
        'mode': game.mode, 
        'state': game.state,
        'teams': [], 
        'players': [],
        'time_limit': game.time_limit,
        'score_limit': game.score_limit,
        'time_played': game.time_played
    }

    teams, players = None, None

    if game.mode == "TEAMS":

        teams = Team.objects.filter(game=game)

        for team in teams:
            game_['teams'].append(team.name)

    players = PlayerInstance.objects.filter(game=game)

    for player in players:
        team = None
        if player.team is not None:
            team = player.team.name
        game_['players'].append({
            'username': player.player.username,
            'gun': player.gun.id,
            'team': team,
            'num_shots': player.num_shots,
             'score': player.score
        })

    return game_


class GameDetail(APIView):
    ''' Get data for a game, its teams, and its players '''

    def get(self, request, pk):
        try:
            game = Game.objects.get(id=pk)
            return Response(getGameData(game))

        except ObjectDoesNotExist:
            return Response("No game with id: " + pk + " exists.")


class GameList(APIView):
    ''' Get data for all games, its teams, and its players '''

    def get(self, request):
        games_ = []

        games = Game.objects.all()

        for game in games:
            games_.append(getGameData(game))

        return Response({'games': games_})


class GameJoin(generics.UpdateAPIView):
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

        return Response({'game': game.id, 'player': instance.id})


class GameStart(APIView):
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
            "time_limit": null,
            "username": "mac the knife"
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

        instance = PlayerInstance.objects.get(game=game,username=data["username"])

        return Response({'game': game.id, 'player': instance.id})

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


class Sync(APIView):
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
