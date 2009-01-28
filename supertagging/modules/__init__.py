"""
Django-SuperTagging

"""
import re
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify


from calais import Calais

from supertagging.models import SuperTag, SuperTagRelation, SuperTaggedItem, SuperTaggedRelationItem

API_KEY = getattr(settings, 'CALAIS_API_KEY')
REF_REGEX = "^http://d.opencalais.com/(?P<key>.*)$"

def process(field, data, obj, content_type, user_directives, processing_directives, process_relations, process_topics, exclusions):
    """
    Process the data.
    """
    # Create the instance of Calais and setup the parameters,
    # see open-calais.com for more information about user directives,
    # and processing directives
    c = Calais(API_KEY)
    c.user_directives.update(user_directives)
    c.processing_directives.update(processing_directives)
    c.processing_directives['contentType'] = content_type
    # Analyze the text (data)
    result = c.analyze(data)
    
    # Retrieve the Django content type for the obj
    cont_type = ContentType.objects.get_for_model(obj)
    # Remove existing items, this ensures tagged items are updated correctly
    SuperTaggedItem.objects.filter(content_type=cont_type, object_id=obj.pk, field=field).delete()
    SuperTaggedRelationItem.objects.filter(content_type=cont_type, object_id=obj.pk, field=field).delete()
    
    # Process entities, relations and topics
    if hasattr(result, 'entities'):
        entities = _processEntities(field, result.entities, obj, cont_type, exclusions)
        
    if hasattr(result, 'relations') and process_relations:
        relations = _processRelations(field, result.relations, obj, cont_type)
        
    if hasattr(result, 'topics') and process_topics:
        topics =  _processTopics(field, result.topics, obj, cont_type)
    
def clean_up(obj):
    """
    When an object is removed, remove all the super tagged items and super tagged relation items
    """
    cont_type = ContentType.objects.get_for_model(obj)
    SuperTaggedItem.objects.filter(content_type=cont_type, object_id=obj.pk).delete()
    SuperTaggedRelationItem.objects.filter(content_type=cont_type, object_id=obj.pk).delete()
    
    # TODO, clean up tags that are no related items?
    # Same for relations?
    
def _processEntities(field, data, obj, cont_type, exclusions):
    """
    Process Entities.
    """
    for entity in data:
        # Here we convert the given float value to an integer
        rel = int(float(str(entity.pop('relevance', '0'))) * 1000)
        inst = entity.pop('instances', {})
        
        pk = re.match(REF_REGEX, str(entity.pop('__reference'))).group('key')
        stype = entity.pop('_type', '')
        
        if stype.lower() not in exclusions:
            name = entity.pop('name', '').lower()
            slug = slugify(name)
            try:
                tag = SuperTag.objects.get(pk=pk)
            except SuperTag.DoesNotExist:
                tag = SuperTag.objects.create(id=pk, slug=slug, stype=stype, name=name)
        
            tag.properties = entity
            tag.save() 
            #TODO: check to make sure that the entity is not already attached
            # to the content object, if it is, just append the instances. This
            # should elimiate entities returned with different names such as 
            # 'Washington' and 'Washington DC' but same id
            try:
                mit = SuperTaggedItem.objects.get(tag=tag, content_type=cont_type, object_id=obj.pk, field=field)
                mit.instances.append(inst)
                mit.save()
            except SuperTaggedItem.DoesNotExist:
                # Create the record that will associate content to tags
                it = SuperTaggedItem.objects.create(tag=tag, content_type=cont_type, object_id=obj.pk, field=field, relevance=rel, instances=inst)
        
def _processRelations(field, data, obj, cont_type):
    """
    Process Relations
    """
    for di in data:
        di.pop('__reference')
        inst = di.pop('instances', {})
        rel_type = di.pop('_type', '')
        
        props = {}
        entities = {}
        # Loop all the items in searh of entities (SuperTags).
        for k,v in di.items():
            res = re.match(REF_REGEX, str(v))
            if res:
                entities[k] = res.group('key')
            else:
                props[k] = v
                
        # Make a copy of the found entities
        entities_temp = entities.copy()
        # This double loop builds a properties dict that includes entities as "Text" and not
        # as the "ID", since the SuperTagRelation needs one "entity" we take one and try to 
        # resolve the other found entities. Entities should already exist from the previous
        # opertaion "_processEntities"
        for entity_key,entity_value in entities.items():
            _vals = {}
            for entity_temp_key,entity_temp_value in entities_temp.items():
                if entity_key != entity_temp_key and entity_value != entity_temp_value:
                    _vals[entity_temp_key] = _getEntityText(entity_temp_value)
                    
            _vals.update(props)
            
            entity = SuperTag.objects.get(pk=entity_value)
            rel_item, rel_created = SuperTagRelation.objects.get_or_create(tag=entity, name=entity_key, stype=rel_type, properties=_vals)
            
            SuperTaggedRelationItem.objects.create(relation=rel_item, content_type=cont_type, object_id=obj.pk, field=field, instances=inst) 
            
def _processTopics(field, data, obj, cont_type):
    """
    Process Topics, this opertaion is similar to _processEntities, the only
    difference is that there are no instances
    """
    for di in data:
        di.pop('__reference')
        
        pk = re.match(REF_REGEX, str(di.pop('category'))).group('key')
        stype = 'Topic'
        name = di.pop('categoryName', '').lower()
        slug = slugify(name)
        try:
            tag = SuperTag.objects.get(pk=pk)
        except SuperTag.DoesNotExist:
            tag = SuperTag.objects.create(id=pk, slug=slug, stype=stype, name=name)
            
        tag.properties = di
        tag.save()
        
        SuperTaggedItem.objects.create(tag=tag, content_type=cont_type, object_id=obj.pk, field=field)
        
def _getEntityText(key):
    """
    Try to resolve the entity given the key
    """
    try:
        r = SuperTag.objects.get(pk=key)
        return r.name
    except SuperTag.DoesNotExist:
        return key
        