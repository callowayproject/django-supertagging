from django.db import models
try:
    import cPickle as pickle
except ImportError:
    import pickle

from supertagging import settings

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
            value = pickle.dumps(value)
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
            
