from django.db.models import get_model
from django.db.models.signals import post_save, post_delete

from supertagging.settings import USE_QUEUE, MODULES, AUTO_PROCESS, ST_DEBUG, MARKUP, MARKUP_FIELD_SUFFIX
from supertagging.modules import process, clean_up, add_to_queue, remove_from_queue
from supertagging.markup import get_handler_module

def save_handler(sender, **kwargs):
    if 'instance' in kwargs:
        if USE_QUEUE:
            add_to_queue(kwargs['instance'])
        else:
            process(kwargs['instance'])

def delete_handler(sender, **kwargs):
    if 'instance' in kwargs:
        if USE_QUEUE:
            remove_from_queue(kwargs['instance'])
        else:
            clean_up(kwargs['instance'])

def setup_handlers():
    if not AUTO_PROCESS:
        return
    
    try:
        for k,v in MODULES.items():
            app_label, model_name = k.split('.')
            model = get_model(app_label, model_name)
            # Setup post save and post delete handlers if model exists
            if model:
                post_save.connect(save_handler, sender=model)
                post_delete.connect(delete_handler, sender=model)
            
            if MARKUP: 
                for f in v.get('fields', []):
                    field = f.get('name', None)
                    markup = f.get('markup', True)
                    if markup and MARKUP and field:
                        handler = get_handler_module(f.get('markup_handler', None))
                        nfield = "%s__%s" % (field, MARKUP_FIELD_SUFFIX)
                        setattr(model, nfield, handler(model, field))
                        
    except Exception, e:
        if ST_DEBUG: raise Exception(e)
