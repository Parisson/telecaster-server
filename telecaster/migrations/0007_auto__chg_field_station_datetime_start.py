# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Station.datetime_start'
        db.alter_column('telecaster_station', 'datetime_start', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True))
    def backwards(self, orm):

        # Changing field 'Station.datetime_start'
        db.alter_column('telecaster_station', 'datetime_start', self.gf('django.db.models.fields.DateTimeField')(null=True))
    models = {
        'telecaster.conference': {
            'Meta': {'object_name': 'Conference'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conferences'", 'to': "orm['telecaster.Department']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.department': {
            'Meta': {'object_name': 'Department'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.organization': {
            'Meta': {'object_name': 'Organization'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.professor': {
            'Meta': {'object_name': 'Professor'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'telecaster.record': {
            'Meta': {'object_name': 'Record'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'records'", 'null': 'True', 'to': "orm['telecaster.Station']"})
        },
        'telecaster.session': {
            'Meta': {'object_name': 'Session'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'telecaster.station': {
            'Meta': {'object_name': 'Station'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'null': 'True', 'to': "orm['telecaster.Conference']"}),
            'datetime_start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'datetime_stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'null': 'True', 'to': "orm['telecaster.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'null': 'True', 'to': "orm['telecaster.Organization']"}),
            'professor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'null': 'True', 'to': "orm['telecaster.Professor']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'null': 'True', 'to': "orm['telecaster.Session']"}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['telecaster']