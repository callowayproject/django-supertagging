#####################################
#   Borrowed from django-tagging    #
#####################################

import math
import types
from django.db.models.query import QuerySet
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string, get_template
from supertagging import settings
# Python 2.3 compatibility
try:
    set
except NameError:
    from sets import Set as set

from operator import itemgetter

def tag_instance_cmp(x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        return cmp(x['offset'],y['offset'])
    return cmp(1, 1)

def get_queryset_and_model(queryset_or_model):
    """
    Given a ``QuerySet`` or a ``Model``, returns a two-tuple of
    (queryset, model).

    If a ``Model`` is given, the ``QuerySet`` returned will be created
    using its default manager.
    """
    try:
        return queryset_or_model, queryset_or_model.model
    except AttributeError:
        return queryset_or_model._default_manager.all(), queryset_or_model

def get_tag_list(tags):
    """
    Utility function for accepting tag input in a flexible manner.

    If a ``Tag`` object is given, it will be returned in a list as
    its single occupant.

    If given, the tag names in the following will be used to create a
    ``Tag`` ``QuerySet``:

       * A string, which may contain multiple tag names.
       * A list or tuple of strings corresponding to tag names.
       * A list or tuple of integers corresponding to tag ids.

    If given, the following will be returned as-is:

       * A list or tuple of ``Tag`` objects.
       * A ``Tag`` ``QuerySet``.

    """
    from supertagging.models import SuperTag
    if isinstance(tags, SuperTag):
        return [tags]
    elif isinstance(tags, QuerySet) and tags.model is SuperTag:
        return tags
    elif isinstance(tags, types.StringTypes):
        return SuperTag.objects.filter(name__in=parse_tag_input(tags))\
                |SuperTag.objects.filter(slug__in=parse_tag_input(tags))
    elif isinstance(tags, (types.ListType, types.TupleType)):
        if len(tags) == 0:
            return tags
        contents = set()
        for item in tags:
            if isinstance(item, types.StringTypes):
                contents.add('string')
            elif isinstance(item, Tag):
                contents.add('tag')
            elif isinstance(item, (types.IntType, types.LongType)):
                contents.add('int')
        if len(contents) == 1:
            if 'string' in contents:
                return SuperTag.objects.filter(name__in=[force_unicode(tag) for tag in tags])\
                        |SuperTag.objects.filter(slug__in=[force_unicode(tag) for tag in tags])
            elif 'tag' in contents:
                return tags
            elif 'int' in contents:
                return SuperTag.objects.filter(id__in=tags)
        else:
            raise ValueError(_('If a list or tuple of tags is provided, they must all be tag names, Tag objects or Tag ids.'))
    else:
        raise ValueError(_('The tag input given was invalid.'))

def get_tag(tag):
    """
    Utility function for accepting single tag input in a flexible
    manner.

    If a ``Tag`` object is given it will be returned as-is; if a
    string or integer are given, they will be used to lookup the
    appropriate ``Tag``.

    If no matching tag can be found, ``None`` will be returned.
    """
    from supertagging.models import SuperTag
    if isinstance(tag, SuperTag):
        return tag

    try:
        if isinstance(tag, types.StringTypes):
            return SuperTag.objects.get(name=tag)
        elif isinstance(tag, (types.IntType, types.LongType)):
            return SuperTag.objects.get(id=tag)
    except SuperTag.DoesNotExist:
        pass

    return None

# Font size distribution algorithms
LOGARITHMIC, LINEAR = 1, 2

def _calculate_thresholds(min_weight, max_weight, steps):
    delta = (max_weight - min_weight) / float(steps)
    return [min_weight + i * delta for i in range(1, steps + 1)]

def _calculate_tag_weight(weight, max_weight, distribution):
    """
    Logarithmic tag weight calculation is based on code from the
    `Tag Cloud`_ plugin for Mephisto, by Sven Fuchs.

    .. _`Tag Cloud`: http://www.artweb-design.de/projects/mephisto-plugin-tag-cloud
    """
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        return math.log(weight) * max_weight / math.log(max_weight)
    raise ValueError(_('Invalid distribution algorithm specified: %s.') % distribution)

def calculate_cloud(tags, steps=4, distribution=LOGARITHMIC):
    """
    Add a ``font_size`` attribute to each tag according to the
    frequency of its use, as indicated by its ``count``
    attribute.

    ``steps`` defines the range of font sizes - ``font_size`` will
    be an integer between 1 and ``steps`` (inclusive).

    ``distribution`` defines the type of font size distribution
    algorithm which will be used - logarithmic or linear. It must be
    one of ``tagging.utils.LOGARITHMIC`` or ``tagging.utils.LINEAR``.
    """
    if len(tags) > 0:
        counts = [tag.count for tag in tags]
        min_weight = float(min(counts))
        max_weight = float(max(counts))
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for tag in tags:
            font_set = False
            tag_weight = _calculate_tag_weight(tag.count, max_weight, distribution)
            for i in range(steps):
                if not font_set and tag_weight <= thresholds[i]:
                    tag.font_size = i + 1
                    font_set = True
    return tags
    
###########################
# Freebase Util Functions #
###########################

try:
    import freebase
except ImportError:
    freebase = None

# The key from freebase that will have the topic description
FREEBASE_DESC_KEY = "/common/topic/article"

def fix_name_for_freebase(value):
    """
    Takes a name and replaces spaces with underscores, removes periods
    and capitalizes each word
    """
    words = []
    for word in value.split():
        word = word.replace(".", "")
        words.append(word.title())
    return "_".join(words)
    
def retrieve_freebase_name(name, stype):
    if not freebase:
        return name
    
    search_key = fix_name_for_freebase(name)
    fb_type = settings.FREEBASE_TYPE_MAPPINGS.get(stype, None)
    value = None
    try:
        # Try to get the exact match
        value = freebase.mqlread(
            {"name": None, "type":fb_type or [], 
             "key": {"value": search_key}})
    except:
        try:
            # Try to get a results has a generator and return its top result
            values = freebase.mqlreaditer(
                {"name": None, "type":fb_type or [], 
                 "key": {"value": search_key}})
            value = values.next()
        except Exception, e:
            # Only print error as freebase is only optional
            if settings.ST_DEBUG: print "Error using `freebase`: %s" % e
            
    if value:
        return value["name"]
    return name
    
def retrieve_freebase_desc(name, stype):
    if not freebase:
        return ""
        
    print "Retrieving the description for %s" % name
    
    fb_type = settings.FREEBASE_TYPE_MAPPINGS.get(stype, None)
    value, data = None, ""
    try:
        value = freebase.mqlread(
            {"name": name, "type": fb_type or [],
             FREEBASE_DESC_KEY: [{"id": None}]})
    except:
        try:
            values = freebase.mqlreaditer(
                {"name": name, "type": fb_type or [],
                 FREEBASE_DESC_KEY: [{"id": None}]})
            value = values.next()
        except Exception, e:
            # Only print error as freebase is only optional
            if settings.ST_DEBUG: print "Error using `freebase`: %s" % e
            
    if value and FREEBASE_DESC_KEY in value and value[FREEBASE_DESC_KEY]:
        guid = value[FREEBASE_DESC_KEY][0].get("id", None)
        if not guid:
            return data
        try:
            import urllib
            desc_url = "%s%s" % (settings.FREEBASE_DESCRIPTION_URL, guid)
            sock = urllib.urlopen(desc_url)
            data = sock.read()                            
            sock.close()
        except Exception, e:
            if settings.ST_DEBUG: print "Error getting description from freebase for tag \"%s\" - %s" % (name, e)
        
    return data
    
################
# Render Utils #
################

def render_item(item, stype, template, suffix, template_path='supertagging/render', context={}):
    """
    Use to render tags, relations, tagged items and tagger relations.
    """
    t, model, app, = None, "", ""
    
    if item:
        model = item.content_type.model.lower()
        app = item.content_type.app_label.lower()
    
    tp = "%s/%s" % (template_path, (stype or ""))
    
    try:
        # Retreive the template passed in
        t = get_template(template)
    except:
        if suffix:
            try:
                # Retrieve the template based off of type and the content object with a suffix
                t = get_template('%s/%s__%s__%s.html' % (
                    tp, app, model, suffix.lower()))
            except:
                pass
        else:
            try:
                # Retrieve the template based off of type and the content object
                t = get_template('%s/%s__%s.html' % (
                    tp, app, model))
            except:
                pass
        if not t:
            if suffix:
                try:
                    # Retrieve the template without the app/model with suffix
                    t = get_template('%s/default__%s.html' % (tp, suffix))
                except:
                    pass
            else:
                try:
                    # Retrieve the template without the app/model
                    t = get_template('%s/default.html' % tp)
                except:
                    try:
                        # Retreive the default template using just the starting template path
                        t = get_template('%s/default.html' % template_path)
                    except:
                        pass
    
    if not t: return None
    
    # Render the template
    ret = render_to_string(t.name, context)

    return ret