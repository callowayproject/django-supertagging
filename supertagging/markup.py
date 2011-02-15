from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string, get_template
from django.core.cache import cache
from django.db.models import get_model

from supertagging import settings
from supertagging.models import SuperTaggedItem

class MarkupHandler(object):
    """
    Default Markup handler
    """
    def __init__(self, model, field):
        self.field = field
        self.model = model
        self.content_type = ContentType.objects.get_for_model(model)
        
    def __get__(self, instance, owner):
        if not instance:
            return
            
        data = self._get_cached_value(instance)
        if data:
            return data
            
        try:
            data = self.handle(instance)
        except Exception, e:
            data = getattr(instance, self.field)
            if settings.ST_DEBUG: raise Exception(e)
        
        cache.set(self._get_cache_key(instance), data, settings.MARKUP_CONTENT_CACHE_TIMEOUT)
        return data
        
    def _get_cache_key(self, instance=None):
        if instance:
            return "ST_HANDLER.%s.%s.%s" % (self.content_type.pk, instance.pk, self.field)
        return None
    
    def _get_cached_value(self, instance=None):
        if instance and self._get_cache_key(instance):
            key = self._get_cache_key(instance)
            return cache.get(key)
        return None
        
    def handle(self, instance=None):
        if instance:
            return markup_content(instance, self.field)
        return ""
       
       
def invalidate_markup_cache(obj, field):
    if not obj:
        return
        
    ctype = ContentType.objects.get_for_model(obj)
    key = "ST_HANDLER.%s.%s.%s" % (ctype.pk, obj.pk, field)
    cache.delete(key)
    
def get_handler_module(module):
    if not module:
        return MarkupHandler
        
    mod, f, i, fn = None, None, None, None
    msplit = module.split(".")
    if len(msplit) == 1:
        mod = msplit[0]
    else:
        f = msplit[:-1]
        i = msplit[-1:]
        fn = ".".join(f)
        
    if mod:
        try:
            return __import__(mod)
        except ImportError:
            return MarkupHandler
    else:
        try:
            mod = __import__(fn, fromlist=f)
            return getattr(mod, i[0])
        except:
            return MarkupHandler
    
class FailedMarkupValidation(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)

def tag_instance_cmp(x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        return cmp(x['offset'],y['offset'])
    return cmp(1, 1)

def markup_content(obj, field, markup_template='supertagging/markup.html'):
    """
    Takes all the items (SuperTaggedItems), and retrieves all the 'instances' to 
    embed the markup_template.
    """
    ctype = ContentType.objects.get_for_model(obj)
    items = SuperTaggedItem.objects.filter(
        content_type__pk=ctype.pk, object_id=obj.pk, 
        relevance__gte=settings.MIN_RELEVANCE_MARKUP).select_related()
    
    value = getattr(obj, field, '')
    full = []
    for item in items:
        if not item.instances:
            continue
        i = item.instances
        skip = False
        for v in i:
            if isinstance(v, list):
                # TODO: figure out a better way to handle list of dicts
                skip = True
                continue
            if isinstance(v, dict):
                v['supertag'] = item.tag
                
        if not skip:
            full.extend(i)

    # Sort the list by the inner dict offset value in reverse
    full.sort(tag_instance_cmp, reverse=True)
    
    for n, i in enumerate(full):
        if 'offset' in i and 'length' in i and 'exact' in i:
            off, le, act_val = i['offset'], i['length'], i['exact']
            if act_val.lower() in settings.MARKUP_EXCLUDES:
                continue
        else:
            continue
            
        # This tests to make sure the next tag does
        # not overlap the current tag
        if n != 0:
            if 'offset' in full[n-1]:
                prev_off = full[n-1]['offset']
                if ((off+1)+le) > prev_off:
                    continue
                    
        # Validate that the data matches the data returned by calais
        if not value[off:(off+le)] == act_val:
            raise FailedMarkupValidation(
                "Markup failed validation: Offset: %s: \"%s\" didn't match \"%s\"" % (off, value[off:(off+le)], act_val))
            break
            
        tag = i['supertag']
        val = render_to_string(markup_template, {'tag': tag, 'actual_value': act_val})
        pre, suf, repl = '','',''
        
        pre = value[:off]
        suf = value[(off+le):]
        repl = value[off:(off+le)]
        
        value = pre+val+suf
        
    return value