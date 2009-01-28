from django.db import models
from django.db.models.signals import post_save, post_delete
from django.conf import settings

from supertagging.modules import process, clean_up
from supertagging.utils import unicode_to_ascii

mod = getattr(settings, 'CALAIS_MODULES', {})
user_dir = getattr(settings, 'CALAIS_USER_DIRECTIVES', {})
proc_dir = getattr(settings, 'CALAIS_PROCESSING_DIRECTIVES', {})
proc_relations = getattr(settings, 'CALAIS_PROCESS_RELATIONS', True)
proc_topics = getattr(settings, 'CALAIS_PROCESS_TOPICS', True)
debug = getattr(settings, 'CALAUS_DEBUG', False)
exclusions = getattr(settings, 'CALAIS_ENTITY_TYPE_EXCLUSIONS', [])

def save_handler(sender, **kwargs):
    try:
        inst = kwargs['instance']
        params = mod['%s.%s' % (sender._meta.app_label, sender._meta.module_name)]
        
        defaut_cont_type = 'TEXT/RAW'
        if 'contentType' in proc_dir:
            defaut_cont_type = proc_dir['contentType']
            
        if 'fields' not in params:
            raise Exception('No "fields" found.')
            
        for item in params['fields']:
            d = item.copy()
            field = d.pop('name')
            content_type = d.pop('content_type', defaut_cont_type)
            
            data = getattr(inst, field)
            # This is really needed?
            if isinstance(data, unicode):
                data = unicode_to_ascii(data)
            else:
                data = unicode_to_ascii(unicode(data), 'utf-8')
            
            process(field, data, inst, content_type, user_dir, proc_dir, proc_relations, proc_topics, exclusions)
    except Exception, e:
        if debug: raise Exception(e)
        
def delete_handler(sender, **kwargs):
    if 'instance' in kwargs:
        inst = kwargs['instance']
        clean_up(inst)
    
def setup():
    for k,v in mod.items():
        app_label, model_name = k.split('.')
        model = models.get_model(app_label, model_name)
        # Setup post save and post delete handlers
        post_save.connect(save_handler, sender=model)
        post_delete.connect(delete_handler, sender=model)
        
