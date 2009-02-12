from django.db import models
from django.db.models.signals import post_save, post_delete

from supertagging import settings
from supertagging.modules import process, clean_up
from supertagging.utils import unicode_to_ascii

def save_handler(sender, **kwargs):
    try:
        if not settings.API_KEY:
            raise ValueError('Calais API KEY is missing.')
            
        inst = kwargs['instance']
        params = settings.MODULES['%s.%s' % (sender._meta.app_label, sender._meta.module_name)]
        
        d_proc_type = settings.DEFAULT_PROCESS_TYPE
        if 'contentType' in settings.PROCESSING_DIR:
            d_proc_type = proc_dir['contentType']
            
        if 'fields' not in params:
            raise Exception('No "fields" found.')
            
        for item in params['fields']:
            d = item.copy()
            field = d.pop('name')
            proc_type = d.pop('process_type', d_proc_type)
            
            data = getattr(inst, field)
            # Is this really needed?
            if isinstance(data, unicode):
                data = unicode_to_ascii(data)
            else:
                data = unicode_to_ascii(unicode(data), 'utf-8')
            
            process(field, data, inst, process_type)
    except Exception, e:
        if settings.ST_DEBUG: raise Exception(e)
        
def delete_handler(sender, **kwargs):
    try:
        if 'instance' in kwargs:
            inst = kwargs['instance']
            clean_up(inst)
    except Exception, e:
        if settings.ST_DEBUG: raise Exception(e)
    
def setup():
    try:
        for k,v in settings.MODULES.items():
            app_label, model_name = k.split('.')
            model = models.get_model(app_label, model_name)
            # Setup post save and post delete handlers
            post_save.connect(save_handler, sender=model)
            post_delete.connect(delete_handler, sender=model)
            
    except Exception, e:
        if settings.ST_DEBUG: raise Exception(e)
        
