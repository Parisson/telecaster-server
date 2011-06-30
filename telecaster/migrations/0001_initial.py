# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Organization'
        db.create_table('telecaster_organization', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('telecaster', ['Organization'])

        # Adding model 'Department'
        db.create_table('telecaster_department', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('telecaster', ['Department'])

        # Adding model 'Conference'
        db.create_table('telecaster_conference', (
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conferences', to=orm['telecaster.Department'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('telecaster', ['Conference'])

        # Adding model 'Session'
        db.create_table('telecaster_session', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('telecaster', ['Session'])

        # Adding model 'Professor'
        db.create_table('telecaster_professor', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('institution', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('telecaster', ['Professor'])

        # Adding model 'Station'
        db.create_table('telecaster_station', (
            ('conference', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['telecaster.Conference'])),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True)),
            ('started', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('professor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['telecaster.Professor'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['telecaster.Session'])),
            ('datetime_start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['telecaster.Department'])),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['telecaster.Organization'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime_stop', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('telecaster', ['Station'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Organization'
        db.delete_table('telecaster_organization')

        # Deleting model 'Department'
        db.delete_table('telecaster_department')

        # Deleting model 'Conference'
        db.delete_table('telecaster_conference')

        # Deleting model 'Session'
        db.delete_table('telecaster_session')

        # Deleting model 'Professor'
        db.delete_table('telecaster_professor')

        # Deleting model 'Station'
        db.delete_table('telecaster_station')
    
    
    models = {
        'telecaster.conference': {
            'Meta': {'object_name': 'Conference'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conferences'", 'to': "orm['telecaster.Department']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.department': {
            'Meta': {'object_name': 'Department'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.organization': {
            'Meta': {'object_name': 'Organization'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'telecaster.professor': {
            'Meta': {'object_name': 'Professor'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'telecaster.session': {
            'Meta': {'object_name': 'Session'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'telecaster.station': {
            'Meta': {'object_name': 'Station'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Conference']"}),
            'datetime_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'datetime_stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Organization']"}),
            'professor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Professor']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['telecaster.Session']"}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }
    
    complete_apps = ['telecaster']
