# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Building'
        db.delete_table('gobjects_building')

        # Deleting model 'BuildingType'
        db.delete_table('gobjects_buildingtype')


    def backwards(self, orm):
        
        # Adding model 'Building'
        db.create_table('gobjects_building', (
            ('town', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Town'])),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.District'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bid', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['addresses.Address'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Region'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gobjects.BuildingType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('gobjects', ['Building'])

        # Adding model 'BuildingType'
        db.create_table('gobjects_buildingtype', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('gobjects', ['BuildingType'])


    models = {
        'addresses.address': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Address'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'town': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Town']"})
        },
        'gobjects.hell': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Hell'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['addresses.Address']"}),
            'counts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hells'", 'symmetrical': 'False', 'through': "orm['gobjects.MachineCount']", 'to': "orm['gobjects.MachineType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'town': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Town']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gobjects.machinecount': {
            'Meta': {'object_name': 'MachineCount'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gobjects.Hell']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gobjects.MachineType']"})
        },
        'gobjects.machinetype': {
            'Meta': {'ordering': "('title',)", 'object_name': 'MachineType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'territories.district': {
            'Meta': {'ordering': "('title',)", 'object_name': 'District'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'territories.region': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Region'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'territories.town': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Town'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['gobjects']
