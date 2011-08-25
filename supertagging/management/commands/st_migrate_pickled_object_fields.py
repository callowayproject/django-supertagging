#!/usr/bin/python
import time
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from supertagging.models import SuperTag, SuperTagRelation, SuperTaggedItem, SuperTaggedRelationItem
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        c = Core()
        c.execute()
        

def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result
            

def convert_fields(model, field):
    print "-- Processing: %s" % model
    cursor = connection.cursor()
    
    sql = "SELECT id, %s FROM %s ORDER BY id LIMIT 100" % (field, model._meta.db_table)
    cursor.execute(sql)
    
    for result in ResultIter(cursor):
        pid, value = result
        print "-- Fixing row: %s" % pid
        
        try:
            old_data = pickle.loads(str(value))
        except Exception, e:
            print "-- Error loading old data, continuing..  (%s)" % e
            old_data = value
            
        try:
            item = model.objects.get(pk=pid)
            if hasattr(item, field):
                setattr(item, field, old_data)
            item.save()
        except Exception, e:
            print "-- Error occuring while saving %s: %s" % (model, e)
    
    print "-- Done Processing: %s" % model

class Core(object):
    """
    Convert the old Pickled data
    """ 
    @transaction.commit_manually
    def execute(self):
        print "Begin Pickled Field Conversion"
        
        convert_fields(SuperTag, "properties")
        transaction.commit()
        
        convert_fields(SuperTagRelation, "properties")
        transaction.commit()
        
        convert_fields(SuperTaggedItem, "instances")
        transaction.commit()
        
        convert_fields(SuperTaggedRelationItem, "instances")
        transaction.commit()
        
        print "Done"
