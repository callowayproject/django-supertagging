from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from supertagging.modules.fields import PickledObjectField

class SuperTag(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=100)
    properties = PickledObjectField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
        
        
class SuperTagRelation(models.Model):
    tag = models.ForeignKey(SuperTag)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    properties = PickledObjectField(null=True, blank=True)
    
    def __unicode__(self):
        return self.type
        
        
class SuperTaggedItemManager(models.Manager):
    #TODO
    pass
    
    
class SuperTaggedItem(models.Model):
    tag = models.ForeignKey(SuperTag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    field = models.CharField(max_length=100)
    relevance = models.IntegerField(null=True, blank=True)
    instances = PickledObjectField(null=True, blank=True)
    
    def __unicode__(self):
        return self.entity.name
        
        
class SuperTaggedRelationItemManager(models.Manager):
    #TODO
    pass
    
    
class SuperTaggedRelationItem(models.Model):
    relation = models.ForeignKey(SuperTagRelation)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    field = models.CharField(max_length=100)
    instances = PickledObjectField(null=True, blank=True)
    
    def __unicode__(self):
        return self.relation
        
        