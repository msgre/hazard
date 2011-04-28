# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Entry'
        db.create_table('geo_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('population', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('wikipedia', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('hell_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('hell_kml', self.gf('django.db.models.fields.TextField')()),
            ('building_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('building_kml', self.gf('django.db.models.fields.TextField')()),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('dperc', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dhell_count', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dok_hell_count', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dper_population', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dper_area', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('geo', ['Entry'])

        # Adding model 'Zone'
        db.create_table('geo_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('poly', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
        ))
        db.send_create_signal('geo', ['Zone'])

        # Adding model 'Building'
        db.create_table('geo_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Entry'])),
            ('poly', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Zone'], null=True, blank=True)),
        ))
        db.send_create_signal('geo', ['Building'])

        # Adding model 'Hell'
        db.create_table('geo_hell', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Entry'])),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('uzone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Zone'], null=True, blank=True)),
            ('zones_calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('geo', ['Hell'])

        # Adding M2M table for field zones on 'Hell'
        db.create_table('geo_hell_zones', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hell', models.ForeignKey(orm['geo.hell'], null=False)),
            ('zone', models.ForeignKey(orm['geo.zone'], null=False))
        ))
        db.create_unique('geo_hell_zones', ['hell_id', 'zone_id'])


    def backwards(self, orm):
        
        # Deleting model 'Entry'
        db.delete_table('geo_entry')

        # Deleting model 'Zone'
        db.delete_table('geo_zone')

        # Deleting model 'Building'
        db.delete_table('geo_building')

        # Deleting model 'Hell'
        db.delete_table('geo_hell')

        # Removing M2M table for field zones on 'Hell'
        db.delete_table('geo_hell_zones')


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
