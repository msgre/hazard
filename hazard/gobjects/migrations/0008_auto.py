# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field campaigns on 'Hell'
        db.create_table('gobjects_hell_campaigns', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hell', models.ForeignKey(orm['gobjects.hell'], null=False)),
            ('campaign', models.ForeignKey(orm['campaigns.campaign'], null=False))
        ))
        db.create_unique('gobjects_hell_campaigns', ['hell_id', 'campaign_id'])

        # Removing M2M table for field counts on 'Hell'
        db.delete_table('gobjects_hell_counts')


    def backwards(self, orm):
        
        # Removing M2M table for field campaigns on 'Hell'
        db.delete_table('gobjects_hell_campaigns')

        # Adding M2M table for field counts on 'Hell'
        db.create_table('gobjects_hell_counts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hell', models.ForeignKey(orm['gobjects.hell'], null=False)),
            ('campaign', models.ForeignKey(orm['campaigns.campaign'], null=False))
        ))
        db.create_unique('gobjects_hell_counts', ['hell_id', 'campaign_id'])


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
            'campaigns': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['campaigns.Campaign']", 'symmetrical': 'False'}),
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
