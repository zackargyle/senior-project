from api.models import *
from api.serializers import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

class TeamList(generics.ListAPIView):
    model = Team
    serializer_class = TeamSerializer


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
        'id': game.id,
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
            game_['teams'].append({"id": team.id, "name": team.name, "score": team.score})

    players = PlayerInstance.objects.filter(game=game)

    for player in players:
        team = None
        if player.team is not None:
            team = player.team.name
        game_['players'].append({
            'username': player.player.username,
            'team_name': team,
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

        return Response(games_)


class GameJoin(APIView):
    '''
        lasertag.byu.edu/join/<game_id>
        {
            "team_id": null,
            "username": "psycho",
            "gun_id": 4
        }
    '''
    def put(self, request, pk, format=None):
        data = request.DATA
        game = Game.objects.get(id=pk)

        team = None
        try:
            team = Team.objects.get(id=data["team_id"])
        except ObjectDoesNotExist:
            pass

        gun = None
        try:
            gun = Gun.objects.get(id=data["gun_id"])
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

        team = instance.team.id if instance.team else None

        return Response({'game_id': game.id, 'player_id': instance.id, 'team_id': team})


class GameStart(APIView):
    '''
        lasertag.byu.edu/start
        {
            "mode": "TEAMS",
            "player": {
                "gun_id": 3,
                "team_name": "googlers",
                "username": "mac the knife"
            },
            "teams": ["googlers", "bingers"],
            "score_limit": null,
            "time_limit": null
        }

    '''
    def post(self, request):
        data = request.DATA
        player = data["player"]
        teams = data["teams"]
        print data

        game = Game(mode=data["mode"], state="PLAYING", time_limit=data["time_limit"], score_limit=data["score_limit"])
        game.save()

        if data["mode"] == "TEAMS":
            setupTeams(teams, game)

        instance = setupPlayer(player, game)

        team_id = instance.team.id if instance.team else None

        return Response({'game_id': game.id, 'player_id': instance.id, 'team_id': team_id})

def setupTeams(teams, game):
    for team_name in teams:
        team = Team(name=team_name, game=game, score=0)
        team.save()

def setupPlayer(player, game):
    player_ = None
    try:
        player_ = Player.objects.get(username=player["username"])
    except ObjectDoesNotExist:
        player_ = Player(username=player["username"])
        player_.save()

    gun = Gun.objects.get(pk=player["gun_id"])

    team = Team.objects.get(game=game, name=player["team_name"])

    instance = PlayerInstance(gun=gun, player=player_, team=team, game=game, num_shots=0, score=0)
    instance.save()
    return instance


class Sync(APIView):
    '''
        lasertag.byu.edu/sync/<game_id>
        {
            "player_id": 3,
            "shots_fired": 15,
            "hits_taken": [4,4,4]
        }
    '''
    def put(self, request, pk, format=None):
        game = Game.objects.get(id=pk)
        data = request.DATA

        try:
            player_instance = PlayerInstance.objects.get(id=data["player_id"])
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
        score = {'name': team.name, 'score': team.score}
        team_scores.append(score)

    players = PlayerInstance.objects.filter(game=game)
    players_scores = []

    for player in players:
        player_scores.append({'username': player.username, 'score': player.score})

    return Response({'team_scores': team_scores,'player_scores': players_scores, 'score': player.score, 'game_state': game.state})


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

        # Increase shooter's score
        player_shooting.score += 50
        player_shooting.save()

        if game.mode == "TEAMS":
            player_shooting.team.score += 50
            player_shooting.team.save()

        # Decrease player_hit's score
        player_hit.score -= 25
        player_hit.save()

        if game.mode == "TEAMS":
            player_hit.team.score -= 25
            player_hit.team.save()
