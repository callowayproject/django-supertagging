from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string, get_template
from django.core.cache import cache
from django.db.models import get_model

from supertagging import settings
from supertagging.models import SuperTag, SuperTaggedItem

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
            
        _cache_key = "ST_HANDLER.%s.%s" % (self.content_type.pk, instance.pk)
        val = cache.get(_cache_key)
        
        # Check to make sure the original cached field data is the 
        # same as the current field data, if it is not the same
        # re-cache the new values, this may result in the data being
        # out of sync with calais
        if val and isinstance(val, dict):
            if val["original"] == getattr(instance, self.field):
                return val["markup"]
                
        # Retreive the current field data and the marked up version
        o_data = getattr(instance, self.field)
        try:
            # If the handle method breaks, use the original content,
            # raise error if debug is True
            m_data = self.handle(instance)
        except Exception, e:
            if settings.ST_DEBUG: raise Exception(e)
            m_data = o_data
        
        val = {'original': o_data, 'markup': m_data}
        cache.set(_cache_key, val, 3600)
        
        return m_data
        
    # TODO:
    # Should the handle method be a place were users can call there own markup?
    # Should it be a place where users can view original and marked up content?
        
    def handle(self, instance=None):
        if instance:
            return markup_content(instance, self.field)
        return ""
        

def register_for_markup():
    for k,v in settings.MODULES.items():
        app_label, model_name = k.split('.')
        model = get_model(app_label, model_name)
        for f in v.get('fields', []):
            field = f.get('name', None)
            markup = f.get('markup', True)
            if markup and settings.MARKUP and field:
                handler = _get_handler_module(f.get('markup_handler', None))
                nfield = "%s__%s" % (field, settings.MARKUP_FIELD_SUFFIX)
                setattr(model, nfield, handler(model, field))
    
def _get_handler_module(module):
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
    items = SuperTaggedItem.objects.filter(content_type__pk=ctype.pk, object_id=obj.pk)
    
    value = getattr(obj, field, '')
    full = []
    for item in items:
        if not item.instances:
            continue
        i = item.instances
        for v in i:
            if isinstance(v, dict):
                v['supertag'] = item.tag
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
        # This tests to make sure the next tag does not overlap 
        # the current tag
        if n != 0:
            if 'offset' in full[n-1]:
                prev_off = full[n-1]['offset']
                if ((off+1)+le) > prev_off:
                    continue
        value = pre+val+suf
        
    return value