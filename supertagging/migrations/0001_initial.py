# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SuperTag'
        db.create_table('supertagging_supertag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calais_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('substitute', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='substitute_tagsubstitute', null=True, to=orm['supertagging.SuperTag'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=150, db_index=True)),
            ('stype', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('properties', self.gf('supertagging.fields.PickledObjectField')(null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('supertagging', ['SuperTag'])

        # Adding M2M table for field related on 'SuperTag'
        db.create_table('supertagging_supertag_related', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_supertag', models.ForeignKey(orm['supertagging.supertag'], null=False)),
            ('to_supertag', models.ForeignKey(orm['supertagging.supertag'], null=False))
        ))
        db.create_unique('supertagging_supertag_related', ['from_supertag_id', 'to_supertag_id'])

        # Adding model 'SuperTagRelation'
        db.create_table('supertagging_supertagrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supertagging.SuperTag'])),
            ('stype', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('properties', self.gf('supertagging.fields.PickledObjectField')(null=True, blank=True)),
        ))
        db.send_create_signal('supertagging', ['SuperTagRelation'])

        # Adding model 'SuperTaggedItem'
        db.create_table('supertagging_supertaggeditem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supertagging.SuperTag'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('process_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('relevance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('instances', self.gf('supertagging.fields.PickledObjectField')(null=True, blank=True)),
            ('item_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('supertagging', ['SuperTaggedItem'])

        # Adding model 'SuperTaggedRelationItem'
        db.create_table('supertagging_supertaggedrelationitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('relation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supertagging.SuperTagRelation'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('process_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('instances', self.gf('supertagging.fields.PickledObjectField')(null=True, blank=True)),
            ('item_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('supertagging', ['SuperTaggedRelationItem'])

        # Adding model 'SuperTagProcessQueue'
        db.create_table('supertagging_supertagprocessqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('supertagging', ['SuperTagProcessQueue'])


    def backwards(self, orm):
        
        # Deleting model 'SuperTag'
        db.delete_table('supertagging_supertag')

        # Removing M2M table for field related on 'SuperTag'
        db.delete_table('supertagging_supertag_related')

        # Deleting model 'SuperTagRelation'
        db.delete_table('supertagging_supertagrelation')

        # Deleting model 'SuperTaggedItem'
        db.delete_table('supertagging_supertaggeditem')

        # Deleting model 'SuperTaggedRelationItem'
        db.delete_table('supertagging_supertaggedrelationitem')

        # Deleting model 'SuperTagProcessQueue'
        db.delete_table('supertagging_supertagprocessqueue')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'supertagging.supertag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'SuperTag'},
            'calais_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'properties': ('supertagging.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_rel_+'", 'null': 'True', 'to': "orm['supertagging.SuperTag']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'db_index': 'True'}),
            'stype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'substitute': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'substitute_tagsubstitute'", 'null': 'True', 'to': "orm['supertagging.SuperTag']"})
        },
        'supertagging.supertaggeditem': {
            'Meta': {'object_name': 'SuperTaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instances': ('supertagging.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'item_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'process_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'relevance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supertagging.SuperTag']"})
        },
        'supertagging.supertaggedrelationitem': {
            'Meta': {'ordering': "['-item_date']", 'object_name': 'SuperTaggedRelationItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instances': ('supertagging.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'item_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'process_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'relation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supertagging.SuperTagRelation']"})
        },
        'supertagging.supertagprocessqueue': {
            'Meta': {'object_name': 'SuperTagProcessQueue'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'supertagging.supertagrelation': {
            'Meta': {'object_name': 'SuperTagRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'properties': ('supertagging.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'stype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supertagging.SuperTag']"})
        }
    }

    complete_apps = ['supertagging']
