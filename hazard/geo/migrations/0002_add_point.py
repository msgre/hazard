# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Entry.dpoint'
        db.add_column('geo_entry', 'dpoint', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Entry.dpoint'
        db.delete_column('geo_entry', 'dpoint')


    models = {
        'geo.building': {
            'Meta': {'object_name': 'Building'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poly': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Zone']", 'null': 'True', 'blank': 'True'})
        },
        'geo.entry': {
            'Meta': {'object_name': 'Entry'},
            'area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'building_kml': ('django.db.models.fields.TextField', [], {}),
            'building_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dhell_count': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dok_hell_count': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dper_area': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dper_population': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dperc': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dpoint': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'hell_kml': ('django.db.models.fields.TextField', [], {}),
            'hell_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'wikipedia': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'geo.hell': {
            'Meta': {'object_name': 'Hell'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'uzone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Zone']", 'null': 'True', 'blank': 'True'}),
            'zones': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hells'", 'symmetrical': 'False', 'to': "orm['geo.Zone']"}),
            'zones_calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'geo.zone': {
            'Meta': {'object_name': 'Zone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poly': ('django.contrib.gis.db.models.fields.PolygonField', [], {})
        }
    }

    complete_apps = ['geo']
