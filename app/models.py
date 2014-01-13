from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    ''' Creates a token whenever a User is created '''
    if created:
        Token.objects.create(user=instance)

class Gun(models.Model):
    frequency = models.IntegerField()

    def __unicode__(self):
        return u'%s' % self.frequency

class Player(models.Model):
    ''' Model features for a Player '''
    username = models.CharField(unique=True, max_length=20)

    def __unicode__(self):
        return u'%s' % self.username

class PlayerInstance(models.Model):
    ''' Model features for an PlayerSnapshot '''
    player = models.ForeignKey('Player')
    gun = models.ForeignKey('Gun')
    team = models.ForeignKey('Team', blank=True, null=True) #team-deathmatch
    game = models.ForeignKey('Game', blank=True, null=True) #juggernaut
    num_shots = models.IntegerField()
    x_coord = models.FloatField(blank=True, null=True)
    y_coord = models.FloatField(blank=True, null=True)
    score = models.IntegerField() #updated in send_updates

    def __unicode__(self):
        return u'%s' % self.player

class Shot(models.Model):
    game = models.ForeignKey('Game')
    shooter = models.ForeignKey('PlayerInstance', related_name="+")
    target = models.ForeignKey('PlayerInstance', related_name="+", blank=True, null=True)

    def __unicode__(self):
        return u'%s hit %s' %(self.shooter, self.target)

class Team(models.Model):
    ''' Model features for a Team '''
    name = models.CharField(max_length=20)
    game = models.ForeignKey('Game')

    def __unicode__(self):
        return u'Team %s' % self.name


class Game(models.Model):
    ''' Model features for a Game '''

    GAME_MODES = (
        ('JUGGERNAUT', 'Juggernaut'),
        ('TEAMS', 'Teams'),
        ('FLAG', 'Capture the Flag'),
    )

    GAME_STATES = (
        ('NEW', 'New'),
        ('PLAYING', 'In Progress'),
        ('FINISHED', 'Finished'),
    )

    mode = models.CharField(max_length=50, choices=GAME_MODES, default='TEAMS')
    state = models.CharField(max_length=20, choices=GAME_STATES, default='NEW')
    time_limit = models.IntegerField()
    time_played = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s, %s' % (self.mode, self.time_played)
