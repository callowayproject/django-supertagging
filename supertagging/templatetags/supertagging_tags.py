# Most template tags were borrowed from django-tagging.

from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError, Variable, resolve_variable
from django.utils.translation import ugettext as _

from supertagging.models import SuperTag, SuperTaggedItem, SuperTagRelation, SuperTaggedRelationItem
from supertagging.utils import LINEAR, LOGARITHMIC

register = Library()

class TagsForModelNode(Node):
    def __init__(self, model, context_var, counts, **kwargs):
        self.model = model
        self.context_var = context_var
        self.counts = counts
        self.kwargs = kwargs

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('supertags_for_model tag was given an invalid model: %s') % self.model)
        
        if 'filters' in self.kwargs and isinstance(self.kwargs['filters'], dict):
            for k,v in self.kwargs['filters'].items():
                try:
                    v = Variable(v).resolve(context)
                    self.kwargs['filters'][k] = v
                except:
                    continue
        context[self.context_var] = SuperTag.objects.usage_for_model(model, counts=self.counts)
        return ''

class TagCloudForModelNode(Node):
    def __init__(self, model, context_var, **kwargs):
        self.model = model
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('supertag_cloud_for_model tag was given an invalid model: %s') % self.model)
        
        if 'filters' in self.kwargs and isinstance(self.kwargs['filters'], dict):
            for k,v in self.kwargs['filters'].items():
                try:
                    v = Variable(v).resolve(context)
                    self.kwargs['filters'][k] = v
                except:
                    continue
        context[self.context_var] = \
            SuperTag.objects.cloud_for_model(model, **self.kwargs)
        return ''

class TagsForObjectNode(Node):
    def __init__(self, obj, context_var, **kwargs):
        self.obj = Variable(obj)
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        context[self.context_var] = \
            SuperTag.objects.get_for_object(self.obj.resolve(context), **self.kwargs)
        return ''

class TaggedObjectsNode(Node):
    def __init__(self, tag, model, context_var):
        self.tag = Variable(tag)
        self.context_var = context_var
        self.model = model

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('supertagged_objects tag was given an invalid model: %s') % self.model)
        context[self.context_var] = \
            SuperTaggedItem.objects.get_by_model(model, self.tag.resolve(context))
        return ''

class RelatedObjectsForObjectNode(Node):
    def __init__(self, obj, model, context_var, **kwargs):
        self.obj = Variable(obj)
        self.context_var = context_var
        self.model = model
        self.kwargs = kwargs

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('supertagged_objects tag was given an invalid model: %s') % self.model)
        context[self.context_var] = \
            SuperTaggedItem.objects.get_related(self.obj.resolve(context), model, **self.kwargs)
        return ''

def do_tags_for_model(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with a given model
    and stores them in a context variable.

    Usage::

       {% supertags_for_model [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    Extended usage::

       {% supertags_for_model [model] as [varname] with counts %}

    If specified - by providing extra ``with counts`` arguments - adds
    a ``count`` attribute to each tag containing the number of
    instances of the given model which have been tagged with it.

    Examples::

       {% supertags_for_model products.Widget as widget_tags %}
       {% supertags_for_model products.Widget as widget_tags with counts %}
       
       {% supertags_for_model products.Widget as widget_tags with counts product__category__pk=1 %}
       {% supertags_for_model products.Widget as widget_tags with counts product__category__pk=category.pk %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if not len_bits > 3:
        raise TemplateSyntaxError(_('%s tag requires more than two arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    if len_bits > 6:
        for i in range(5, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'counts':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    # The remaining bits should be consider extra query params
                    kwargs['filters'][name] = value
                    
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
        if bits[4] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        if bits[5] != 'counts':
            raise TemplateSyntaxError(_("if given, fifth argument to %s tag must be 'counts'") % bits[0])
    if len_bits == 4:
        return TagsForModelNode(bits[1], bits[3], counts=False)
    else:
        return TagsForModelNode(bits[1], bits[3], counts=True)

def do_tag_cloud_for_model(parser, token):
    """
    Retrieves a list of ``Tag`` objects for a given model, with tag
    cloud attributes set, and stores them in a context variable.

    Usage::

       {% supertag_cloud_for_model [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    Extended usage::

       {% supertag_cloud_for_model [model] as [varname] with [options] %}

    Extra options can be provided after an optional ``with`` argument,
    with each option being specified in ``[name]=[value]`` format. Valid
    extra options are:

       ``steps``
          Integer. Defines the range of font sizes.

       ``min_count``
          Integer. Defines the minimum number of times a tag must have
          been used to appear in the cloud.

       ``distribution``
          One of ``linear`` or ``log``. Defines the font-size
          distribution algorithm to use when generating the tag cloud.
          
        If anything else is speficied in the options, it will be consider 
        extra filter params

    Examples::

       {% supertag_cloud_for_model products.Widget as widget_tags %}
       {% supertag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distribution=log %}
       
       {% supertag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distrubution=log product__category__pk=1 %}
       {% supertag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distrubution=log product__category__pk=category.pk %}
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if not len_bits > 3:
        raise TemplateSyntaxError(_('%s tag requires more than two arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {'filters': {}}
    if len_bits > 5:
        if bits[4] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(5, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'steps' or name == 'min_count':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                elif name == 'distribution':
                    if value in ['linear', 'log']:
                        kwargs[str(name)] = {'linear': LINEAR, 'log': LOGARITHMIC}[value]
                    else:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid choice: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    # The remaining bits should be consider extra query params
                    kwargs['filters'][name] = value
                    
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return TagCloudForModelNode(bits[1], bits[3], **kwargs)

def do_tags_for_object(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with an object and
    stores them in a context variable.

    Usage::

       {% supertags_for_object [object] as [varname] with [options] %}

    Example::

        {% supertags_for_object foo_object as tag_list %}
        
        {% supertags_for_object foo_object as tag_list with field=story %}
        
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 7):
        raise TemplateSyntaxError(_('%s tag requires either three or five arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits > 5:
        if bits[4] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(5, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'field':
                    try:
                        kwargs[str(name)] = str(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not valid: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return TagsForObjectNode(bits[1], bits[3], **kwargs)

def do_tagged_objects(parser, token):
    """
    Retrieves a list of instances of a given model which are tagged with
    a given ``Tag`` and stores them in a context variable.

    Usage::

       {% supertagged_objects [tag] in [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    The tag must be an instance of a ``Tag``, not the name of a tag.

    Example::

        {% supertagged_objects comedy_tag in tv.Show as comedies %}

    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise TemplateSyntaxError(_('%s tag requires exactly five arguments') % bits[0])
    if bits[2] != 'in':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'in'") % bits[0])
    if bits[4] != 'as':
        raise TemplateSyntaxError(_("fourth argument to %s tag must be 'as'") % bits[0])
    return TaggedObjectsNode(bits[1], bits[3], bits[5])

def do_related_objects_for_object(parser, token):
    """
    Retrieves a list of related objects of a given model which shares tags
     with the given ``obj`` and stores them in a context variable.

    Usage::

       {% related_objects_for_object [obj] in [model] as [varname] with [options] %}

    The model is specified in ``[appname].[modelname]`` format.

    The obj must be an instance of the ``model``.

    Example::

        {% related_objects_for_object show in tv.Show as related_objects %}
        
        {% related_objects_for_object show in tv.Show as related_objects with min_relevance=500 %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 6 and len_bits not in range(7, 10):
        raise TemplateSyntaxError(_('%s tag requires either five or between 7 and 8 arguments') % bits[0])
    if bits[2] != 'in':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'in'") % bits[0])
    if bits[4] != 'as':
        raise TemplateSyntaxError(_("fourth argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits > 6:
        if bits[6] != 'with':
            raise TemplateSyntaxError(_("if given, 6th argument to %s tag must be 'with'") % bits[0])
        for i in range(7, len_bits):
            try:
                name, value = bits[i].split('=')
                if name in ['min_relevance', 'num']:
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return RelatedObjectsForObjectNode(bits[1], bits[3], bits[5], **kwargs)

register.tag('supertags_for_model', do_tags_for_model)
register.tag('supertag_cloud_for_model', do_tag_cloud_for_model)
register.tag('supertags_for_object', do_tags_for_object)
register.tag('supertagged_objects', do_tagged_objects)
register.tag('related_objects_for_object', do_related_objects_for_object)


class RelationsForTagNode(Node):
    def __init__(self, obj, context_var, stype=None):
        self.obj = Variable(obj)
        self.stype = stype
        self.context_var = context_var

    def render(self, context):
        kwargs = {}
        if self.stype:
            kwargs['stype__iexact'] = self.stype
        context[self.context_var] = \
            SuperTagRelation.objects.get_for_tag(
                self.obj.resolve(context), **kwargs)
        return ''
        
        
class RelationsForObjectNode(Node):
    def __init__(self, obj, context_var, stype=None):
        self.obj = Variable(obj)
        self.stype = stype
        self.context_var = context_var

    def render(self, context):
        kwargs = {}
        if self.stype:
            kwargs['stype__iexact'] = self.stype
        context[self.context_var] = \
            SuperTaggedRelationItem.objects.get_for_object(
                self.obj.resolve(context), **kwargs)
        return ''
        
        
class RelationsForTagInObjectNode(Node):
    def __init__(self, tag, obj, context_var):
        self.obj = Variable(obj)
        self.tag = Variable(tag)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = \
            SuperTaggedRelationItem.objects.get_for_tag_in_object(
                tag=self.tag.resolve(context), obj=self.obj.resolve(context))
        return ''


def do_relations_for_tag(parser, token):
    """
    Retrieves a list of ``Relations`` for a given ``Tag``

    Usage::

        {% relations_for_supertag [tag] as [varname] %}
        {% relations_for_supertag [tag] as [varname] with type=[TYPE] %}

    The tag must of an instance of a ``Tag``, not the name of a tag.

    Example::

        {% relations_for_supertag state_tag as relations %}
        {% relations_for_supertag state_tag as relations with type=Quotation %}

    """
    bits = token.contents.split()
    if len(bits) < 4 or len(bits) > 6:
        raise TemplateSyntaxError(_('%s tag requires at least three arguments and at most six arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("Second argument for %s tag must be 'as'") % bits[0])
        
    if len(bits) > 4:
        if bits[4] != "with":
            raise TemplateSyntacError(_("Fouth argument for %s tag must be 'with'") % bits[0])
        
        if len(bits[5].split("=")) == 2 and bits[5].split("=")[0] == 'type':
             return RelationsForTagNode(bits[1], bits[3], bits[5].split("=")[1])
        else:
            raise TemplateSyntacError(_("Last argument for %s tag must be in the format type=[TYPE]") % bits[0])
    return RelationsForTagNode(bits[1], bits[3])
  

def do_relations_for_object(parser, token):
    """
    Retrieves a list of ``Relations`` for a given object
    
    Useage::
        
        {% relations_for_object [object] as [varname] %}
        {% relations_for_object [object] as [varname] with [type=TYPE]}
        
    Example::
    
        {% relations_for_object story as story_relations %}
        {% relations_for_object story as story_relations with type=Quotation %}
        
    """
    bits = token.contents.split()
    if len(bits) < 4 or len(bits) > 6:
        raise TemplateSyntaxError(_('%s tag requires at least three arguments and at most six arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("Second argument for %s tag must be 'as'") % bits[0])
        
    if len(bits) > 4:
        if bits[4] != "with":
            raise TemplateSyntacError(_("Fouth argument for %s tag must be 'with'") % bits[0])
        
        if len(bits[5].split("=")) == 2 and bits[5].split("=")[0] == 'type':
             return RelationsForObjectNode(bits[1], bits[3], bits[5].split("=")[1])
        else:
            raise TemplateSyntacError(_("Last argument for %s tag must be in the format type=[TYPE]") % bits[0])
    return RelationsForObjectNode(bits[1], bits[3])
    
def do_relations_for_tag_in_object(parser, token):
    """
    Retrieves a list of ``Relations`` for a given tag that is also in object
    
    Useage::
        
        {% relations_for [tag] in [object] as [varname] %}
        
    Example::
    
        {% relations_for state_tag in obj as obj_relations %}
        
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise TemplateSyntaxError(_('%s tag requires exactly five arguments') % bits[0])
    if bits[2] != 'in':
        raise TemplateSyntaxError(_("Second argument to %s tag must be 'in'") % bits[0])
    if bits[4] != 'as':
        raise TemplateSyntaxError(_("Second argument to %s tag must be 'as'") % bits[0])
    return RelationsForTagInObjectNode(bits[1], bits[3], bits[5])
 

    
    
register.tag('relations_for_supertag', do_relations_for_tag)
register.tag('relations_for_object', do_relations_for_object)
register.tag('relations_for', do_relations_for_tag_in_object)


class RenderItemNode(Node):
    def __init__(self, obj, template=None, suffix=None):
        self.obj = obj
        self.template = template
        self.suffix = suffix
        
    def render(self, context):
        suffix, template = self.suffix, self.template
        try:
            obj = Variable(self.obj).resolve(context)
            isinst = False
            for c in [SuperTag, SuperTaggedItem, SuperTagRelation, SuperTaggedRelationItem]:
                if isinstance(obj, c):
                    isinst = True
                    break
                    
            if not isinst:
                return None
        except:
            return None
            
        return obj.render(template=template, suffix=suffix)
        
        
def do_render_item(parser, token):
    """
    {% supertag_render [SuperTag or SuperTaggedItem or SuperTagRelation or SuperTaggedRelationItem] [with] [suffix=S] [template=T] %}
    {% supertag_render tag %}
    {% supertag_render tagged_item with suffix=custom %}
    {% supertag_render rel_item with template=mycustomtemplates/supertags/custom.html %}
    
    Only suffix OR template can be specified, but not both.
    """
    argv = token.contents.split()
    argc = len(argv)
    
    if argc < 2 or argc > 4:
        raise TemplateSyntaxError, "Tag %s takes either two or four arguments." % argv[0]
        
    if argc == 2:
        return RenderItemNode(argv[1])
    else:
        if argv[2] != 'with':
            raise TemplateSyntaxError, 'Second argument must be "with" for tag %s.' % argv[0]
        extra = argv[3].split('=')
        if len(extra) != 2:
            raise TemplateSyntaxError, "Last argument must be formated correctly for tag %s." % argv[0]
        if not extra[0] in ['suffix', 'template']:
            raise TemplateSyntaxError, "Last argment must of either suffix or template for tag %s." % argv[0]
            
        kwargs = {str(extra[0]): extra[1],}
        return RenderItemNode(argv[1], **kwargs)
        
register.tag('supertag_render', do_render_item)