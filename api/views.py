import datetime

from api.models import *
from api.serializers import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

START_DELAY = 60 #seconds

def timeLeft(game):
    time_played = (datetime.datetime.utcnow() - game.time_played.replace(tzinfo=None)).total_seconds()
    time_remaining = int(round(game.time_limit + START_DELAY - time_played))
    return time_remaining if time_remaining > 0 else 0
    
def scoreLimitReached(game):
    if game.mode == 'TEAMS':
        teams = Team.objects.filter(game=game)
        for team in teams:
            if team.score >= game.score_limit:
                return True
    else:
        players = PlayerInstance.objects.filter(game=game)
        for player in players:
            if player.score >= game.score_limit:
                return True
    return False


class TeamList(generics.ListAPIView):
    model = Team
    serializer_class = TeamSerializer


class ShotList(generics.ListAPIView):
    model = Shot
    serializer_class = ShotSerializer

def getPlayerStats(player, rank):
    team_ = None

    if player.team is not None:
        team_ = player.team.name

    player_ = {
        'time_played': player.game.time_played, 
        'team_name': team_,
        'num_shots': player.num_shots,
        'hits_landed': player.hits_landed,
        'hits_taken': player.hits_taken,
        'score': player.score,
        'rank': rank
    }
    return player_

class GameStats(APIView):
    def get(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
            players = PlayerInstance.objects.filter(game=game).order_by('-score')

            game_ = {'mode': game.mode, 'players': [], 'high_score': -10000, 'low_score': 10000}

            for index, player in enumerate(players):
                instance = getPlayerStats(player, index + 1)

                if player.num_shots == 0:
                    instance['shot_perc'] = 100
                else:
                    instance['shot_perc'] = int(round(100 * player.hits_landed / float(player.num_shots)))

                if instance['score'] > game_['high_score']:
                    game_['high_score'] = instance['score']
                if instance['score'] < game_['low_score']:
                    game_['low_score'] = instance['score']

                game_['players'].append(instance)

            return Response(game_)
        except ObjectDoesNotExist:
            return Response("No game with that id")


class PlayerStats(APIView):
    def get(self, request, username):
        player_ = {'username': username, 'instances': [], 'score_total': 0, 'high_score': 0, 'shot_perc': 0}
        try:
            player = Player.objects.get(username=username)
            instances = PlayerInstance.objects.filter(player=player)

            total_hits = 0
            total_shots = 0

            for instance in instances:
                frenemies = PlayerInstance.objects.filter(game=instance.game).order_by('-score')

                rank = 0
                for index, dude in enumerate(frenemies):
                    if dude == instance:
                        rank = index + 1

                instance_ = getPlayerStats(instance, rank)

                player_['instances'].append(instance_)
                player_['score_total'] += instance.score
                total_hits += instance.hits_landed
                total_shots += instance.num_shots

                if instance.score > player_['high_score']:
                    player_['high_score'] = instance.score

            if total_shots == 0:
                player_['shot_perc'] = 100
            else:
                player_['shot_perc'] = int(round(100 * total_hits / float(total_shots),2))

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
    time_left = None
    if game.time_limit is not None:
        time_left = timeLeft(game);
            
    game_ = { 
        'id': game.id,
        'mode': game.mode, 
        'state': game.state,
        'teams': [], 
        'players': [],
        'time_limit': game.time_limit,
        'score_limit': game.score_limit,
        'time_played': game.time_played,
        'time_left': time_left
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
    ''' 
        Query Parameters
            - limitTo, startAt
            - joinable (filters all NEW or PLAYING games)
            - state (NEW, PLAYING, FINISHED)
            - mode (FREE, TEAMS)
    '''

    def get(self, request):
        games = Game.objects.all().order_by('-time_played')

        # Query Parameters
        limit = request.GET.get('limitTo')
        start = request.GET.get('startAt')
        state = request.GET.get('state')
        mode  = request.GET.get('mode')
        joinable = request.GET.get('joinable')

        if joinable is not None:
            games = games.exclude(state="FINISHED")
        elif state is not None:
            games = games.filter(state=state)

        if mode is not None:
            games = games.filter(mode=mode)

        if limit is not None:
            limit = int(limit)
            if start is not None:
                start = int(start)
                games = games[start:start+limit]
            else:
                games = games[0:limit]

        games_ = []
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
    def post(self, request, pk, format=None):
        data = request.DATA
        game = Game.objects.get(id=pk)

        # Cannot join completed games
        if game.state == "FINISHED":
            return Response("Cannot join finished games.")

        # Past Wait State
        if game.state == 'NEW':
            if (datetime.datetime.utcnow() - game.time_played.replace(tzinfo=None)).total_seconds() >= START_DELAY:
                game.state = 'PLAYING'
                game.save()

        team = None
        try:
            team = Team.objects.get(id=data["team_id"])
        except ObjectDoesNotExist:
            pass

        gun = None
        try:
            gun = Gun.objects.get(id=data["gun_id"])
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()

        player = None
        try:
            player = Player.objects.get(username=data["username"])
        except ObjectDoesNotExist:
            player = Player(username=data["username"])
            player.save()

        instance = PlayerInstance(gun=gun, player=player, team=team, game=game, num_shots=0, score=0)
        instance.save()

        team = instance.team.id if instance.team else None

        time_left = None
        if game.time_limit is not None:
            time_left = timeLeft(game);

        return Response({'game_id': game.id, 'player_id': instance.id, 'team_id': team, 'time_left': time_left, 'time_limit': game.time_limit})


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

        game = Game(mode=data["mode"], state="NEW", time_limit=data["time_limit"], score_limit=data["score_limit"])
        game.save()

        try:
            if data["mode"] == "TEAMS":
                setupTeams(teams, game)
            instance = setupPlayer(player, game)
        except ObjectDoesNotExist:
            game.delete()
            return HttpResponseBadRequest()

        team_id = instance.team.id if instance.team else None

        time_left = 60
        if game.time_limit is not None:
            time_left = timeLeft(game);

        return Response({'game_id': game.id, 'player_id': instance.id, 'team_id': team_id, 'time_left': time_left})

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

    team = None
    if game.mode == "TEAMS":
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
            "hits_taken": [4,4,4] -> gun_id
        }
    '''
    def post(self, request, pk, format=None):
        game = Game.objects.get(id=pk)
        data = request.DATA

        # Past wait state?
        if game.state == 'NEW':
            if (datetime.datetime.utcnow() - game.time_played.replace(tzinfo=None)).total_seconds() >= START_DELAY:
                game.state = 'PLAYING'
                game.save()
            else:
                return Response('Cannot sync. Currently in 60 second wait period.')

        # Game finished?
        if game.state == 'FINISHED':
            player_instance = PlayerInstance.objects.get(id=data["player_id"])
            return getUpdates(game, player_instance)
        elif game.time_limit is not None and timeLeft(game) <= 0:
            game.state = 'FINISHED'
            game.save()
            player_instance = PlayerInstance.objects.get(id=data["player_id"])
            return getUpdates(game, player_instance)
        elif game.score_limit is not None and scoreLimitReached(game):
            game.state = 'FINISHED'
            game.save()
            player_instance = PlayerInstance.objects.get(id=data["player_id"])
            return getUpdates(game, player_instance)

        # Ok, it is valid. Do stuff
        try:
            player_instance = PlayerInstance.objects.get(id=data["player_id"])
            player_instance.num_shots = data["shots_fired"]
            player_instance.save()

            updateShots(game, data["hits_taken"], player_instance)

            return getUpdates(game, player_instance)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()


def getUpdates(game, player_):
    teams = Team.objects.filter(game=game)
    team_scores = []

    for team in teams:
        score = {'name': team.name, 'score': team.score}
        team_scores.append(score)

    players = PlayerInstance.objects.filter(game=game)
    player_scores = []

    for player in players:
        player_scores.append({'username': player.player.username, 'score': player.score})

    return Response({'team_scores': team_scores,'player_scores': player_scores, 'score': player_.score, 'game_state': game.state})

def updateShots(game, hits, player_hit):
    for gun_id in hits:
        player_shooting = PlayerInstance.objects.get(game=game, gun=gun_id)

        # Cannot shoot yourself
        if player_shooting.id == player_hit.id:
            return

        # Cannot shoot teammates
        if game.mode == "TEAMS":
            if player_shooting.team == player_hit.team:
                return

        # Create the shot correlation
        shot = Shot(game=game, shooter=player_shooting, target=player_hit)
        shot.save()

        # Increase shooter's score
        player_shooting.score += 50
        player_shooting.hits_landed += 1;
        player_shooting.save()

        if game.mode == "TEAMS":
            player_shooting.team.score += 50
            player_shooting.team.save()

        # Decrease player_hit's score
        player_hit.score -= 25
        player_hit.hits_taken += 1
        player_hit.save()

        if game.mode == "TEAMS":
            player_hit.team.score -= 25
            player_hit.team.save()
