# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Session.description'
        db.alter_column('telecaster_session', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Department.description'
        db.alter_column('telecaster_department', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Organization.description'
        db.alter_column('telecaster_organization', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Professor.institution'
        db.alter_column('telecaster_professor', 'institution', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Professor.telephone'
        db.alter_column('telecaster_professor', 'telephone', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Professor.address'
        db.alter_column('telecaster_professor', 'address', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Professor.email'
        db.alter_column('telecaster_professor', 'email', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Station.comment'
        db.alter_column('telecaster_station', 'comment', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Conference.description'
        db.alter_column('telecaster_conference', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=255))
    def backwards(self, orm):

        # Changing field 'Session.description'
        db.alter_column('telecaster_session', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Department.description'
        db.alter_column('telecaster_department', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Organization.description'
        db.alter_column('telecaster_organization', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Professor.institution'
        db.alter_column('telecaster_professor', 'institution', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Professor.telephone'
        db.alter_column('telecaster_professor', 'telephone', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Professor.address'
        db.alter_column('telecaster_professor', 'address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Professor.email'
        db.alter_column('telecaster_professor', 'email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Station.comment'
        db.alter_column('telecaster_station', 'comment', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Conference.description'
        db.alter_column('telecaster_conference', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
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
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Conference']"}),
            'datetime_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datetime_stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Organization']"}),
            'professor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Professor']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Session']"}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['telecaster']