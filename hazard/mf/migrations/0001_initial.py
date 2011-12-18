# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BuildingType'
        db.create_table('mf_buildingtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('mf', ['BuildingType'])

        # Adding model 'BuildingSurround'
        db.create_table('mf_buildingsurround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('poly', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('mf', ['BuildingSurround'])

        # Adding model 'Building'
        db.create_table('mf_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('distance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('line', self.gf('django.contrib.gis.db.models.fields.LineStringField')(null=True, blank=True)),
            ('poly', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(related_name='buildings', to=orm['addresses.Address'])),
            ('surround', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='buildings_surrounds', null=True, to=orm['mf.BuildingSurround'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mf.BuildingType'])),
            ('bid', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Region'])),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.District'])),
            ('town', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Town'])),
        ))
        db.send_create_signal('mf', ['Building'])

        # Adding model 'BuildingConflict'
        db.create_table('mf_buildingconflict', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['campaigns.Campaign'])),
            ('hell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gobjects.Hell'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('mf', ['BuildingConflict'])


    def backwards(self, orm):
        
        # Deleting model 'BuildingType'
        db.delete_table('mf_buildingtype')

        # Deleting model 'BuildingSurround'
        db.delete_table('mf_buildingsurround')

        # Deleting model 'Building'
        db.delete_table('mf_building')

        # Deleting model 'BuildingConflict'
        db.delete_table('mf_buildingconflict')


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
        'campaigns.campaign': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Campaign'},
            'app': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
        'mf.building': {
            'Meta': {'object_name': 'Building'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'buildings'", 'to': "orm['addresses.Address']"}),
            'bid': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.contrib.gis.db.models.fields.LineStringField', [], {'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'poly': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'surround': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'buildings_surrounds'", 'null': 'True', 'to': "orm['mf.BuildingSurround']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'town': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Town']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mf.BuildingType']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'mf.buildingconflict': {
            'Meta': {'object_name': 'BuildingConflict'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['campaigns.Campaign']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gobjects.Hell']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'mf.buildingsurround': {
            'Meta': {'object_name': 'BuildingSurround'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poly': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'mf.buildingtype': {
            'Meta': {'ordering': "('title',)", 'object_name': 'BuildingType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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

    complete_apps = ['mf']
