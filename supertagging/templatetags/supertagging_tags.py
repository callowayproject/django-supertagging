# Most template tags were borrowed from django-tagging.

from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError, Variable, resolve_variable
from django.utils.translation import ugettext as _

from supertagging.models import SuperTag, SuperTaggedItem, SuperTagRelation, SuperTaggedRelationItem
from supertagging.utils import LINEAR, LOGARITHMIC

register = Library()

class TagsForModelNode(Node):
    def __init__(self, model, context_var, counts):
        self.model = model
        self.context_var = context_var
        self.counts = counts

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('supertags_for_model tag was given an invalid model: %s') % self.model)
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

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits not in (4, 6):
        raise TemplateSyntaxError(_('%s tag requires either three or five arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    if len_bits == 6:
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

    Examples::

       {% supertag_cloud_for_model products.Widget as widget_tags %}
       {% supertag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distribution=log %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 9):
        raise TemplateSyntaxError(_('%s tag requires either three or between five and seven arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
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
                    raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
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
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = \
            SuperTagRelation.objects.get_for_tag(self.obj.resolve(context))
        return ''
        
        
class RelationsForObjectNode(Node):
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = \
            SuperTaggedRelationItem.objects.get_for_object(self.obj.resolve(context))
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
        

class EmbedSuperTagsNode(Node):
    def __init__(self, obj, field, rel):
        self.field = field.strip("'")
        self.rel = int(rel)
        self.obj = Variable(obj)
        
    def render(self, context):
        obj = self.obj.resolve(context)
        value = SuperTaggedItem.objects.embed_supertags(obj, self.field, self.rel)
        return value


def do_relations_for_tag(parser, token):
    """
    Retrieves a list of ``Relations`` for a given ``Tag``

    Usage::

        {% relations_for_tag [tag] as [varname] %}

    The tag must of an instance of a ``Tag``, not the name of a tag.

    Example::

        {% relations_for_tag state_tag as relations %}

    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return RelationsForTagNode(bits[1], bits[3])

def do_relations_for_object(parser, token):
    """
    Retrieves a list of ``Relations`` for a given object
    
    Useage::
        
        {% relations_for_object [object] as [varname] %}
        
    Example::
    
        {% relations_for_object story as story_relations %}
        
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
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
        raise TemplateSyntaxError(_("second argument to %s tag must be 'in'") % bits[0])
    if bits[4] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return RelationsForTagInObjectNode(bits[1], bits[3], bits[5])
 
def do_embed_supertags(parser, token):
    """
    Markup content, adds links to matched tags

    Usage::

        {% embed_supertags [object] for [field] [relavance] %}
        
    relavance (optional) should be between 0 and 1000, it will retreive 
        items with greater or equal relvance.
        
    Example::

        {% embed_supertags story for content 500 %}

    """
    bits = token.contents.split()
    if len(bits) < 4:
        raise template.TemplateSyntaxError(_('%s tag requires a minium of 4 arguments') % bits[0])
    if bits[2] != 'for':
        raise template.TemplateSyntaxError(_("second argument to %s tag must be 'for'") % bits[0])
    
    if len(bits) == 4:
        return EmbedSuperTagsNode(bits[1], bits[3])
    elif len(bits) == 5:
        return EmbedSuperTagsNode(bits[1], bits[3], bits[4])
    
    
register.tag('relations_for_supertag', do_relations_for_tag)
register.tag('relations_for_object', do_relations_for_object)
register.tag('relations_for', do_relations_for_tag_in_object)
register.tag('embed_supertags', do_embed_supertags)
