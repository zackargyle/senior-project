# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gun'
        db.create_table(u'api_gun', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'api', ['Gun'])

        # Adding model 'Player'
        db.create_table(u'api_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'api', ['Player'])

        # Adding model 'PlayerInstance'
        db.create_table(u'api_playerinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Player'])),
            ('gun', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Gun'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Team'], null=True, blank=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Game'], null=True, blank=True)),
            ('num_shots', self.gf('django.db.models.fields.IntegerField')()),
            ('x_coord', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('y_coord', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('hits_taken', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('hits_landed', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'api', ['PlayerInstance'])

        # Adding model 'Shot'
        db.create_table(u'api_shot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Game'])),
            ('shooter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['api.PlayerInstance'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['api.PlayerInstance'])),
        ))
        db.send_create_signal(u'api', ['Shot'])

        # Adding model 'Team'
        db.create_table(u'api_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Game'])),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'api', ['Team'])

        # Adding model 'Game'
        db.create_table(u'api_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(default='FREE', max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(default='NEW', max_length=20)),
            ('time_limit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('score_limit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time_played', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Game'])


    def backwards(self, orm):
        # Deleting model 'Gun'
        db.delete_table(u'api_gun')

        # Deleting model 'Player'
        db.delete_table(u'api_player')

        # Deleting model 'PlayerInstance'
        db.delete_table(u'api_playerinstance')

        # Deleting model 'Shot'
        db.delete_table(u'api_shot')

        # Deleting model 'Team'
        db.delete_table(u'api_team')

        # Deleting model 'Game'
        db.delete_table(u'api_game')


    models = {
        u'api.game': {
            'Meta': {'object_name': 'Game'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "'FREE'", 'max_length': '50'}),
            'score_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '20'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'api.gun': {
            'Meta': {'object_name': 'Gun'},
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'api.player': {
            'Meta': {'object_name': 'Player'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'api.playerinstance': {
            'Meta': {'object_name': 'PlayerInstance'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Game']", 'null': 'True', 'blank': 'True'}),
            'gun': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Gun']"}),
            'hits_landed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hits_taken': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_shots': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Player']"}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Team']", 'null': 'True', 'blank': 'True'}),
            'x_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'api.shot': {
            'Meta': {'object_name': 'Shot'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shooter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['api.PlayerInstance']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['api.PlayerInstance']"})
        },
        u'api.team': {
            'Meta': {'object_name': 'Team'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'score': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['api']