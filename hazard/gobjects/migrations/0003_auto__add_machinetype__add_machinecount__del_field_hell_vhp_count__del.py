# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MachineType'
        db.create_table('gobjects_machinetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gobjects', ['MachineType'])

        # Adding model 'MachineCount'
        db.create_table('gobjects_machinecount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gobjects.Hell'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gobjects.MachineType'])),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('gobjects', ['MachineCount'])

        # Deleting field 'Hell.vhp_count'
        db.delete_column('gobjects_hell', 'vhp_count')

        # Deleting field 'Hell.emr_count'
        db.delete_column('gobjects_hell', 'emr_count')

        # Deleting field 'Hell.vlt_count'
        db.delete_column('gobjects_hell', 'vlt_count')

        # Deleting field 'Hell.ivt_count'
        db.delete_column('gobjects_hell', 'ivt_count')

        # Deleting field 'Hell.vtz_count'
        db.delete_column('gobjects_hell', 'vtz_count')


    def backwards(self, orm):
        
        # Deleting model 'MachineType'
        db.delete_table('gobjects_machinetype')

        # Deleting model 'MachineCount'
        db.delete_table('gobjects_machinecount')

        # Adding field 'Hell.vhp_count'
        db.add_column('gobjects_hell', 'vhp_count', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Hell.emr_count'
        db.add_column('gobjects_hell', 'emr_count', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Hell.vlt_count'
        db.add_column('gobjects_hell', 'vlt_count', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Hell.ivt_count'
        db.add_column('gobjects_hell', 'ivt_count', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Hell.vtz_count'
        db.add_column('gobjects_hell', 'vtz_count', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


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
        'gobjects.building': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Building'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['addresses.Address']"}),
            'bid': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'town': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Town']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gobjects.BuildingType']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gobjects.buildingtype': {
            'Meta': {'ordering': "('title',)", 'object_name': 'BuildingType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'gobjects.hell': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Hell'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['addresses.Address']"}),
            'counts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hells'", 'symmetrical': 'False', 'through': "orm['gobjects.MachineCount']", 'to': "orm['gobjects.MachineType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
