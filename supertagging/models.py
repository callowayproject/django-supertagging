from django.db import models, connection
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from supertagging.fields import PickledObjectField
from supertagging.utils import calculate_cloud, get_tag_list, get_queryset_and_model, parse_tag_input
from supertagging.utils import LOGARITHMIC

qn = connection.ops.quote_name

###################
##   MANAGERS    ##
###################

class SuperTagManager(models.Manager):
    def update_tags(self, obj, tag_names):
        """
        Update tags associated with an object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        current_tags = list(self.filter(supertaggeditem__content_type__pk=ctype.pk,
                                        supertaggeditem__object_id=obj.pk))
                                        
        updated_tag_names = parse_tag_input(tag_names)
        # Always lower case tags
        updated_tag_names = [t.lower() for t in updated_tag_names]

        from supertagging.modules import process
        # Process the tags with Calais
        processed_tags = process(obj, updated_tag_names)
        
        for t in updated_tag_names:
            if t not in [p.name for p in processed_tags]:
                try:
                    tag = self.get(name__iexact=t)
                except:
                    tag = self.create(id=t, name=t, slug=slugify(t), stype='Custom')
                    
                SuperTaggedItem._default_manager.create(tag=tag, content_object=obj, field='None')
                
                
    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)

        ids = self.filter(supertaggeditem__content_type__pk=ctype.pk,
                           supertaggeditem__object_id=obj.pk).exclude(stype='Topic').values('id')
                           
        return self.filter(id__in=ids)
                           
    def get_topics_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        ids = self.filter(supertaggeditem__content_type__pk=ctype.pk,
                           supertaggeditem__object_id=obj.pk, stype='Topic').values('id')
        
        return self.filter(id__in=ids)
             
             
    def _get_usage(self, model, counts=False, min_count=None, extra_joins=None, extra_criteria=None, params=None):
       """
       Perform the custom SQL query for ``usage_for_model`` and
       ``usage_for_queryset``.
       """
       if min_count is not None: counts = True

       model_table = qn(model._meta.db_table)
       model_pk = '%s.%s' % (model_table, qn(model._meta.pk.column))
       query = """
       SELECT DISTINCT %(tag)s.id, %(tag)s.name%(count_sql)s, %(tag)s.slug
       FROM
           %(tag)s
           INNER JOIN %(tagged_item)s
               ON %(tag)s.id = %(tagged_item)s.tag_id
           INNER JOIN %(model)s
               ON %(tagged_item)s.object_id = %(model_pk)s
           %%s
       WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
           %%s
       GROUP BY %(tag)s.id, %(tag)s.name
       %%s
       ORDER BY %(tag)s.name ASC""" % {
           'tag': qn(self.model._meta.db_table),
           'count_sql': counts and (', COUNT(%s)' % model_pk) or '',
           'tagged_item': qn(SuperTaggedItem._meta.db_table),
           'model': model_table,
           'model_pk': model_pk,
           'content_type_id': ContentType.objects.get_for_model(model).pk,
       }

       min_count_sql = ''
       if min_count is not None:
           min_count_sql = 'HAVING COUNT(%s) >= %%s' % model_pk
           params.append(min_count)

       cursor = connection.cursor()
       cursor.execute(query % (extra_joins, extra_criteria, min_count_sql), params)
       tags = []
       for row in cursor.fetchall():
           t = self.model(id=row[0],name=row[1], slug=row[3])
           if counts:
               t.count = row[2]
           tags.append(t)
       return tags              
    def usage_for_model(self, model, counts=False, min_count=None, filters=None):
       """
       Obtain a list of tags associated with instances of the given
       Model class.

       If ``counts`` is True, a ``count`` attribute will be added to
       each tag, indicating how many times it has been used against
       the Model class in question.

       If ``min_count`` is given, only tags which have a ``count``
       greater than or equal to ``min_count`` will be returned.
       Passing a value for ``min_count`` implies ``counts=True``.

       To limit the tags (and counts, if specified) returned to those
       used by a subset of the Model's instances, pass a dictionary
       of field lookups to be applied to the given Model as the
       ``filters`` argument.
       """
       if filters is None: filters = {}

       queryset = model._default_manager.filter()
       for f in filters.items():
           queryset.query.add_filter(f)
       usage = self.usage_for_queryset(queryset, counts, min_count)

       return usage  
       
    def usage_for_queryset(self, queryset, counts=False, min_count=None):
       """
       Obtain a list of tags associated with instances of a model
       contained in the given queryset.

       If ``counts`` is True, a ``count`` attribute will be added to
       each tag, indicating how many times it has been used against
       the Model class in question.

       If ``min_count`` is given, only tags which have a ``count``
       greater than or equal to ``min_count`` will be returned.
       Passing a value for ``min_count`` implies ``counts=True``.
       """

       extra_joins = ' '.join(queryset.query.get_from_clause()[0][1:])
       where, params = queryset.query.where.as_sql()
       if where:
           extra_criteria = 'AND %s' % where
       else:
           extra_criteria = ''
       return self._get_usage(queryset.model, counts, min_count, extra_joins, extra_criteria, params)   
                  
    def cloud_for_model(self, model, steps=4, distribution=LOGARITHMIC,
                       filters=None, min_count=None):
        """
        Obtain a list of tags associated with instances of the given
        Model, giving each tag a ``count`` attribute indicating how
        many times it has been used and a ``font_size`` attribute for
        use in displaying a tag cloud.

        ``steps`` defines the range of font sizes - ``font_size`` will
        be an integer between 1 and ``steps`` (inclusive).

        ``distribution`` defines the type of font size distribution
        algorithm which will be used - logarithmic or linear. It must
        be either ``supertagging.utils.LOGARITHMIC`` or
        ``supertagging.utils.LINEAR``.

        To limit the tags displayed in the cloud to those associated
        with a subset of the Model's instances, pass a dictionary of
        field lookups to be applied to the given Model as the
        ``filters`` argument.

        To limit the tags displayed in the cloud to those with a
        ``count`` greater than or equal to ``min_count``, pass a value
        for the ``min_count`` argument.
        """
        tags = list(self.usage_for_model(model, counts=True, filters=filters,
                                        min_count=min_count))
        return calculate_cloud(tags, steps, distribution)      
           
                           
class SuperTagRelationManager(models.Manager):
    def get_for_tag(self, tag):
        return self.filter(tag__pk=tag.id)


class SuperTaggedItemManager(models.Manager):
    
    def get_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with a given tag or list of tags.
        """
        tags = get_tag_list(tags)
        tag_count = len(tags)
        if tag_count == 0:
            # No existing tags were given
            queryset, model = get_queryset_and_model(queryset_or_model)
            return model._default_manager.none()
        elif tag_count == 1:
            # Optimisation for single tag - fall through to the simpler
            # query below.
            tag = tags[0]
        else:
            return self.get_intersection_by_model(queryset_or_model, tags)

        queryset, model = get_queryset_and_model(queryset_or_model)
        content_type = ContentType.objects.get_for_model(model)
        opts = self.model._meta
        tagged_item_table = qn(opts.db_table)
        return queryset.extra(
            tables=[opts.db_table],
            where=[
                '%s.content_type_id = %%s' % tagged_item_table,
                '%s.tag_id = %%s' % tagged_item_table,
                '%s.%s = %s.object_id' % (qn(model._meta.db_table),
                                          qn(model._meta.pk.column),
                                          tagged_item_table)
            ],
            params=[content_type.pk, tag.pk],
        )
        
    def get_intersection_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *all* of the given list of tags.
        """
        tags = get_tag_list(tags)
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have all the
        # given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s
        HAVING COUNT(%(model_pk)s) = %(tag_count)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
            'tag_count': tag_count,
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def get_union_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *any* of the given list of tags.
        """
        tags = get_tag_list(tags)
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have any of
        # the given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def get_related(self, obj, queryset_or_model, num=None):
        """
        Retrieve a list of instances of the specified model which share
        tags with the model instance ``obj``, ordered by the number of
        shared tags in descending order.

        If ``num`` is given, a maximum of ``num`` instances will be
        returned.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        model_table = qn(model._meta.db_table)
        content_type = ContentType.objects.get_for_model(obj)
        related_content_type = ContentType.objects.get_for_model(model)
        query = """
        SELECT %(model_pk)s, COUNT(related_tagged_item.object_id) AS %(count)s
        FROM %(model)s, %(tagged_item)s, %(tag)s, %(tagged_item)s related_tagged_item
        WHERE %(tagged_item)s.object_id = %%s
          AND %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tag)s.id = %(tagged_item)s.tag_id
          AND related_tagged_item.content_type_id = %(related_content_type_id)s
          AND related_tagged_item.tag_id = %(tagged_item)s.tag_id
          AND %(model_pk)s = related_tagged_item.object_id"""
        if content_type.pk == related_content_type.pk:
            # Exclude the given instance itself if determining related
            # instances for the same model.
            query += """
          AND related_tagged_item.object_id != %(tagged_item)s.object_id"""
        query += """
        GROUP BY %(model_pk)s
        ORDER BY %(count)s DESC
        %(limit_offset)s"""
        query = query % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'count': qn('count'),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'tag': qn(self.model._meta.get_field('tag').rel.to._meta.db_table),
            'content_type_id': content_type.pk,
            'related_content_type_id': related_content_type.pk,
            # Hardcoding this for now just to get tests working again - this
            # should now be handled by the query object.
            'limit_offset': num is not None and 'LIMIT %s' or '',
        }

        cursor = connection.cursor()
        params = [obj.pk]
        if num is not None:
            params.append(num)
        cursor.execute(query, params)
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            # Use in_bulk here instead of an id__in lookup, because id__in would
            # clobber the ordering.
            object_dict = queryset.in_bulk(object_ids)
            return [object_dict[object_id] for object_id in object_ids \
                    if object_id in object_dict]
        else:
            return []
    
    
class SuperTaggedRelationItemManager(models.Manager):
    pass
    

###################
##    MODELS     ##
###################
class SuperTag(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    stype = models.CharField("Type", max_length=100)
    properties = PickledObjectField(null=True, blank=True)
    
    objects = SuperTagManager()
    
    def __unicode__(self):
        return self.name
        

        
class SuperTagRelation(models.Model):
    tag = models.ForeignKey(SuperTag)
    stype = models.CharField("Type", max_length=100)
    name = models.CharField(max_length=150)
    properties = PickledObjectField(null=True, blank=True)
    
    objects = SuperTagRelationManager()
    
    def __unicode__(self):
        return self.stype
        

class SuperTaggedItem(models.Model):
    tag = models.ForeignKey(SuperTag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    field = models.CharField(max_length=100)
    process_type = models.CharField(max_length=20, null=True, blank=True)
    relevance = models.IntegerField(null=True, blank=True)
    instances = PickledObjectField(null=True, blank=True)
    
    objects = SuperTaggedItemManager()
    
    def __unicode__(self):
        return ''
        

class SuperTaggedRelationItem(models.Model):
    relation = models.ForeignKey(SuperTagRelation)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    field = models.CharField(max_length=100)
    process_type = models.CharField(max_length=20, null=True, blank=True)
    instances = PickledObjectField(null=True, blank=True)
    
    objects = SuperTaggedRelationItemManager()
    
    def __unicode__(self):
        return self.relation
        
        