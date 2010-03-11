#!/usr/bin/python
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from supertagging.models import SuperTagProcessQueue
from supertagging.modules import process
from supertagging import settings as st_settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        c = Core()
        c.execute()


class Core(object):
    """
    The Core is responsible for driving Supertagging
    """ 
    @transaction.commit_manually
    def execute(self):
        """
        The main execution path; this function is invoked by a scheduler.
        """
        processed, failed, objs_to_del, objs_to_reset = 0, 0, [], []
        print 'Getting objects to process...'
        objects = SuperTagProcessQueue.objects.filter(locked=False)
        print 'Done. %s object(s)' % len(objects)
        print 'Locking object(s)...'
        SuperTagProcessQueue.objects.filter(locked=False).update(locked=True)
        transaction.commit()
        print 'Done.'
        for obj in objects:
            print 'Processing: %s...' % obj
            try:
                print 'Start processing object with calais...'
                process(obj.content_object)
                print 'Done'
                objs_to_del.append(obj.pk)
                print 'Committing calais data...'
                transaction.commit()
                print 'Done'
                processed += 1
            except Exception, e:
                print 'Failed to process object, rolling back... %s' % e
                objs_to_reset.append(obj.pk)
                transaction.rollback()
                print 'Done'
                failed += 1
            time.sleep(1)
            
        print 'Unlocking objects...'
        SuperTagProcessQueue.objects.filter(pk__in=objs_to_reset).update(locked=False)
        transaction.commit()
        print 'Done'
        print 'Deleting processed objects form queue...'
        SuperTagProcessQueue.objects.filter(pk__in=objs_to_del).delete()
        transaction.commit()
        print 'Done'
        print '%s of %s objects processed. %s failed.' % (processed, 
            processed + failed, failed)
