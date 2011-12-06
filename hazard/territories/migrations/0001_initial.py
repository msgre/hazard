# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Region'
        db.create_table('territories_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('territories', ['Region'])

        # Adding model 'District'
        db.create_table('territories_district', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Region'])),
            ('shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('territories', ['District'])

        # Adding model 'Town'
        db.create_table('territories_town', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.District'])),
            ('shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Region'])),
        ))
        db.send_create_signal('territories', ['Town'])

        # Adding model 'Zip'
        db.create_table('territories_zip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('town', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Town'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.Region'])),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['territories.District'])),
        ))
        db.send_create_signal('territories', ['Zip'])


    def backwards(self, orm):
        
        # Deleting model 'Region'
        db.delete_table('territories_region')

        # Deleting model 'District'
        db.delete_table('territories_district')

        # Deleting model 'Town'
        db.delete_table('territories_town')

        # Deleting model 'Zip'
        db.delete_table('territories_zip')


    models = {
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
        },
        'territories.zip': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Zip'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Region']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'town': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['territories.Town']"})
        }
    }

    complete_apps = ['territories']
