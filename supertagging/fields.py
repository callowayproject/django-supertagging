from django.db.models import signals
from django.db.models.fields import TextField
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
from supertagging import settings
from supertagging.utils import edit_string_for_tags

class PickledObjectField(models.Field):
    """ Django snippet - http://www.djangosnippets.org/snippets/513/ """
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        try:
            return pickle.loads(str(value))
        except:
            # If an error was raised, just return the plain value
            return value
                
    def get_db_prep_save(self, value):
        if value is not None:
            value = pickle.dumps(force_unicode(value))
        return str(value)
        
    def get_internal_type(self): 
        return 'TextField'
        
    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)
            
            

class SuperTagField(TextField):
    """
    A "special" character field that actually works as a relationship to tags
    "under the hood". This exposes a space-separated string of tags, but does
    the splitting/reordering/etc. under the hood.
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        kwargs['blank'] = kwargs.get('blank', True)
        super(SuperTagField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(SuperTagField, self).contribute_to_class(cls, name)

        # Make this object the descriptor for field access.
        setattr(cls, self.name, self)

        # Save tags back to the database post-save
        signals.post_save.connect(self._save, cls, True)

    def __get__(self, instance, owner=None):
        """
        Tag getter. Returns an instance's tags if accessed on an instance, and
        all of a model's tags if called on a class. That is, this model::

           class Link(models.Model):
               ...
               tags = TagField()

        Lets you do both of these::

           >>> l = Link.objects.get(...)
           >>> l.tags
           'tag1 tag2 tag3'

           >>> Link.tags
           'tag1 tag2 tag3 tag4'

        """
        from supertagging.models import SuperTag
        # Handle access on the model (i.e. Link.tags)
        if instance is None:
            return edit_string_for_tags(SuperTag.objects.usage_for_model(owner))

        tags = self._get_instance_tag_cache(instance)
        if tags is None:
            if instance.pk is None:
                self._set_instance_tag_cache(instance, '')
            else:
                self._set_instance_tag_cache(
                    instance, edit_string_for_tags(SuperTag.objects.get_for_object(instance)))

        return self._get_instance_tag_cache(instance)

    def __set__(self, instance, value):
        """
        Set an object's tags.
        """
        from supertagging.models import SuperTag
        if instance is None:
            raise AttributeError(_('%s can only be set on instances.') % self.name)

        tags = edit_string_for_tags(SuperTag.objects.get_for_object(instance))
        
        new_value = []
        if not value:
            value = tags
        else:
            for tag in tags.split(','):
                if tag in value.split(','):
                    new_value.append(tag)
                    
            for tag in value.split(','):
                if tag not in new_value:
                    new_value.append(tag)
            
            value = ','.join([t for t in new_value])
            
        self._set_instance_tag_cache(instance, value)

    def _save(self, **kwargs): #signal, sender, instance):
        """
        Save tags back to the database
        """
        from supertagging.models import SuperTag
        tags = self._get_instance_tag_cache(kwargs['instance'])
        if tags is not None:
            SuperTag.objects.update_tags(kwargs['instance'], tags)

    def __delete__(self, instance):
        """
        Clear all of an object's tags.
        """
        self._set_instance_tag_cache(instance, '')

    def _get_instance_tag_cache(self, instance):
        """
        Helper: get an instance's tag cache.
        """
        return getattr(instance, '_%s_cache' % self.attname, None)

    def _set_instance_tag_cache(self, instance, tags):
        """
        Helper: set an instance's tag cache.
        """
        setattr(instance, '_%s_cache' % self.attname, tags)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        from supertagging import forms
        defaults = {'form_class': forms.SuperTagField}
        defaults.update(kwargs)
        return super(SuperTagField, self).formfield(**defaults)
