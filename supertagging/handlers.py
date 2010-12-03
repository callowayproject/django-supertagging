from django.db.models import get_model
from django.db.models.signals import post_save, post_delete

from supertagging.settings import USE_QUEUE, MODULES, AUTO_PROCESS, ST_DEBUG, MARKUP, MARKUP_FIELD_SUFFIX, REGISTER_MODELS
from supertagging import register

def save_handler(sender, instance, **kwargs):
    if instance:
        from supertagging.modules import process, add_to_queue 
        if USE_QUEUE:
            add_to_queue(instance)
        else:
            process(instance)

def delete_handler(sender, instance, **kwargs):
    if instance:
        from supertagging.modules import clean_up, remove_from_queue
        if USE_QUEUE:
            remove_from_queue(instance)
        else:
            clean_up(instance)

def setup_handlers():
    try:
        for k,v in MODULES.items():
            app_label, model_name = k.split('.')
            model = get_model(app_label, model_name)
            
            # Add a tag attribute to the instance.
            if REGISTER_MODELS:
                register(model)
            
            # Setup post save and post delete handlers if model exists
            if model and AUTO_PROCESS:
                post_save.connect(save_handler, sender=model)
                post_delete.connect(delete_handler, sender=model)
            
            if MARKUP: 
                # Add a custom attribute to a model with a marked up
                # version of the field specified.
                for f in v.get('fields', []):
                    field = f.get('name', None)
                    markup = f.get('markup', True)
                    if markup and MARKUP and field:
                        from supertagging.markup import get_handler_module
                        handler = get_handler_module(f.get('markup_handler', None))
                        nfield = "%s__%s" % (field, MARKUP_FIELD_SUFFIX)
                        setattr(model, nfield, handler(model, field))
                        
    except Exception, e:
        if ST_DEBUG: raise Exception(e)
