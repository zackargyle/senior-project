# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gun'
        db.create_table(u'app_gun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'app', ['Gun'])

        # Adding model 'Player'
        db.create_table(u'app_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'app', ['Player'])

        # Adding model 'PlayerInstance'
        db.create_table(u'app_playerinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Player'])),
            ('gun', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Gun'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Team'], null=True, blank=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Game'], null=True, blank=True)),
            ('num_shots', self.gf('django.db.models.fields.IntegerField')()),
            ('x_coord', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('y_coord', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'app', ['PlayerInstance'])

        # Adding model 'Shot'
        db.create_table(u'app_shot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Game'])),
            ('shooter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['app.PlayerInstance'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['app.PlayerInstance'])),
        ))
        db.send_create_signal(u'app', ['Shot'])

        # Adding model 'Team'
        db.create_table(u'app_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Game'])),
        ))
        db.send_create_signal(u'app', ['Team'])

        # Adding model 'Game'
        db.create_table(u'app_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(default='TEAMS', max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(default='NEW', max_length=20)),
            ('time_limit', self.gf('django.db.models.fields.IntegerField')()),
            ('time_played', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Game'])


    def backwards(self, orm):
        # Deleting model 'Gun'
        db.delete_table(u'app_gun')

        # Deleting model 'Player'
        db.delete_table(u'app_player')

        # Deleting model 'PlayerInstance'
        db.delete_table(u'app_playerinstance')

        # Deleting model 'Shot'
        db.delete_table(u'app_shot')

        # Deleting model 'Team'
        db.delete_table(u'app_team')

        # Deleting model 'Game'
        db.delete_table(u'app_game')


    models = {
        u'app.game': {
            'Meta': {'object_name': 'Game'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "'TEAMS'", 'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '20'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'app.gun': {
            'Meta': {'object_name': 'Gun'},
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.player': {
            'Meta': {'object_name': 'Player'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'app.playerinstance': {
            'Meta': {'object_name': 'PlayerInstance'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Game']", 'null': 'True', 'blank': 'True'}),
            'gun': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Gun']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_shots': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Player']"}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Team']", 'null': 'True', 'blank': 'True'}),
            'x_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'app.shot': {
            'Meta': {'object_name': 'Shot'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shooter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['app.PlayerInstance']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['app.PlayerInstance']"})
        },
        u'app.team': {
            'Meta': {'object_name': 'Team'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['app']