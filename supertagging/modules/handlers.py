from django.db import models
from django.db.models.signals import post_save, post_delete

from supertagging import settings
from supertagging.modules import process, clean_up

def save_handler(sender, **kwargs):
    if 'instance' in kwargs:
        process(kwargs['instance'])

def delete_handler(sender, **kwargs):
    if 'instance' in kwargs:
        clean_up(kwargs['instance'])
   
def setup():
    if not settings.AUTO_PROCESS:
        return

    try:
        for k,v in settings.MODULES.items():
            app_label, model_name = k.split('.')
            model = models.get_model(app_label, model_name)
            # Setup post save and post delete handlers
            post_save.connect(save_handler, sender=model)
            post_delete.connect(delete_handler, sender=model)

    except Exception, e:
        if settings.ST_DEBUG: raise Exception(e)
