from django.test import TestCase
from django.test import Client
import json

from api.models import *

'''
    Tests are run in alphabetical order. I use a single letter
    prefix to force the order of tests. Notice the naming of each
    test _a_, _b_ _c_. This is just for logical output order.
'''

def id_list(array):
    ids = []
    for obj in array:
        ids.append('{id: ' + str(obj['id']) + ', mode: ' + obj['mode'] + ', state: ' + obj['state'] + '}')
    return ','.join(ids)

class APITests(TestCase):

    def setUp(self):
        self.client = Client()

    # Testing starting various game modes
    def test_a_start_game(self):
        url = '/start'

        gun = Gun(id=1, frequency=1000)
        gun.save()

        player = {"gun_id":gun.id,"team_name":'empire',"username": "testDude"}

        # Free for all
        data = { "mode": "FREE", "player": player, "teams": None, "score_limit": None, "time_limit": None }
        print '\nStarting free-for-all game'
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print '    ' + str(response.data)
        print 'Free-for-all game successfully started'

        # Team Deathmatch
        data = { "mode": "TEAMS", "player": player, "teams": ['empire', 'alliance'], "score_limit": None, "time_limit": 600 }
        print '\nStarting team deathmatch with optional time limit'
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print '    ' + str(response.data)
        print 'Team deathmatch successfully started'

        # Future tests for juggernaut and capture the flag

    # Testing joining various game modes
    def test_b_join_game(self):
        gun = Gun(id=1, frequency=1000)
        gun.save()

        # Free for all join
        game1 = Game(mode="FREE", state="NEW", time_limit=None, score_limit=None)
        game1.save()
        data = { "team_id": None, "username": "testDude", "gun_id": gun.id }

        url = '/join/' + str(game1.id)
        print '\nJoining free-for-all'
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print '    ' + str(response.data)
        print 'Free-for-all successfully joined'

        # Join team deathmatch
        game2 = Game(mode="TEAMS", state="NEW", time_limit=None, score_limit=None)
        game2.save()
        team = Team(name="Empire", game=game2, score=0)
        team.save()
        data = { "team_id": team.id, "username": "testDude", "gun_id": gun.id }

        url = '/join/' + str(game2.id)
        print '\nJoining team deathmatch'
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print '    ' + str(response.data)
        print 'Team deathmatch successfully joined'

    # Newest version, no install, no device instance
    def test_c_get_games(self):
        game1 = Game(mode="FREE", state="NEW", time_limit=None, score_limit=None)
        game1.save()
        game2 = Game(mode="TEAMS", state="PLAYING", time_limit=None, score_limit=None)
        game2.save()
        game3 = Game(mode="TEAMS", state="FINISHED", time_limit=None, score_limit=None)
        game3.save()
        
        url = '/games'

        # Get games
        print '\nGetting all games: /games'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        print '    ' + id_list(response.data)
        print 'Obtained all games'

        # Get free for all games
        print '\nGetting free-for-all games: /games?mode=FREE'
        response = self.client.get(url + '?mode=FREE')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], game1.id)
        print '    ' + id_list(response.data)
        print 'Obtained free-for-all games'

        # All new/playing games
        print '\nGetting joinable games: /games?joinable'
        response = self.client.get(url + '?joinable')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        print '    ' + id_list(response.data)
        print 'Obtained joinable games'
