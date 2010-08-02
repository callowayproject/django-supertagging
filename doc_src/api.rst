.. _api:

API Reference
=============

.. contents::
   :depth: 3

.. _api_supertag:

SuperTag
********

Fields
------

* **calais_id** - Contains the OpenCalais entity ID
    * CharField
    * Length: 255
    * Unique
* **substitute** - Substitute tags in order to have better disambiguation.
    * ForeignKey to self
    * null=True, blank=True
* **name** - The tag name.
    * CharField
    * Length: 150
* **slug** - Slugified name
    * SlugField
    * Length: 150
* **stype** - Tag type as returned by OpenCalais
    * CharField
    * Length: 100
* **properties** - Tag properties as returned by OpenCalais
    * `PickledObjectField <http://djangosnippets.org/snippets/513/>`_
    * null=True, blank=True
* **enabled** - Weather or not this tag is used.
    * BooleanField
    * Default: True
    
Optional Fields
---------------

If :ref:`setting_include_display_fields` is True, these fields will be 
included with the model.

* **display_name** - Name used for display purposes. Since all SuperTag name are lowered when returned from calais, we can use this field to set the case correctly for example
    * CharField
    * Length: 150
    * null=True, blank=True
* **description** - Description of the tag
    * TextField
    * null=True, blank=True
* **icon** - Image field for the tag
    * ImageField
    * null=True, blank=True
* **related** - Manually relating tags
    * ManyToManyField to self
    * null=True, blank=True
    

Methods
-------

get_name
~~~~~~~~

Gets the name of the tag, this will try to retrieve the display name first 
if the display fields are available, if the display fields are not available 
the normal name will be returned.

has_display_fields
~~~~~~~~~~~~~~~~~~

Returns True or False, if the display fields are available.

render
~~~~~~

Renders the instance, view :ref:`render` for more information.

.. _api_supertagrelation:

SuperTagRelation
****************

Fields
------

* **tag** - The associated tag
    * ForeignKey to :ref:`api_supertag`
* **stype** - The type of relation
    * CharField
    * Length: 100
* **name** - Name of the relation
    * CharField
    * Length: 150
* **properties** - Relation properties returned by OpenCalais
    * `PickledObjectField <http://djangosnippets.org/snippets/513/>`_
    * null=True, blank=True

Methods
-------

render
~~~~~~

Renders the instance, view :ref:`render` for more information.


.. _api_supertaggeditem:

SuperTaggedItem
***************

Generic relation to a :ref:`api_supertag`

Fields
------

* **tag** - The associated tag
    * ForeignKey to :ref:`api_supertag`
* **content_type** - Content type of an object
    * ForeignKey to `django.contrib.contenttypes.models.ContentType`
* **object_id** - Instance primary key
    * PositiveIntegerField
* **content_object** - Gernric relation
    * GenericForeignKey to content_type and object_id
* **field** - The name of the field this instance refers to
    * CharField
    * Length: 100
* **process_type** - The type used to process the data, "TEXT/HTML", "TEXT/RAW" or "TEXT/XML"
    * CharField
    * Length: 10
    * null=True, blank=True
* **relevance** - The relevance score
    * IntegerField
    * null=True, blank=True
* **instances** - Contains a list of all the tags found in the content.
    * `PickledObjectField <http://djangosnippets.org/snippets/513/>`_
    * null=True, blank=True
* **item_date** - Date of the object
    * DateTimeField
    * null=True, blank=True

Methods
-------

render
~~~~~~

Renders the instance, view :ref:`render` for more information.

.. _api_supertaggedrelationitem:

SuperTaggedRelationItem
***********************

Fields
------

* **relation** - Associated relation
    * ForignKey to :ref:`api_supertagrelation`
* **content_type** - Content type of an object
    * ForeignKey to `django.contrib.contenttypes.models.ContentType`
* **object_id** - Instance primary key
    * PositiveIntegerField
* **content_object** - Gernric relation
    * GenericForeignKey to content_type and object_id
* **field** - The name of the field this instance refers to
    * CharField
    * Length: 100
* **process_type** - The type used to process the data, "TEXT/HTML", "TEXT/RAW" or "TEXT/XML"
    * CharField
    * Length: 10
    * null=True, blank=True
* **instances** - Contains a list of all the tags found in the content.
    * `PickledObjectField <http://djangosnippets.org/snippets/513/>`_
    * null=True, blank=True
* **item_date** - Date of the object
    * DateTimeField
    * null=True, blank=True
    
Methods
-------

render
~~~~~~

Renders the instance, view :ref:`render` for more information.

.. _api_supertagprocessqueue:

SuperTagProcessQueue
********************

Holds a generic relation to an object to be processed at a later time, this 
model is only used when :ref:`setting_use_queue` is set to `True`

Fields
------

* **content_type** - Content type of an object
    * ForeignKey to `django.contrib.contenttypes.models.ContentType`
* **object_id** - Instance primary key
    * PositiveIntegerField
* **content_object** - Gernric relation
    * GenericForeignKey to content_type and object_id
* **locked** - Weather the object is being processed
    * BooleanField
    * Default: False
    

.. _render:

Rendering Items
***************

:ref:`api_supertag`, :ref:`api_supertaggeditem`, :ref:`api_supertagrelation` 
and :ref:`api_supertaggedrelationitem` have a `render` method in order to 
correctly display its contents.

Template Locations
------------------

Default location for these templates are in `supertagging/templates/render`. 
For each model there is an additional folder:

* SuperTag: "tags/"
* SuperTaggedItem: "tagged_items/"
* SuperTagRelation: "relations/"
* SuperTaggedRelationItem: "tagged_relations/"

For example the default template for a SuperTaggedItem would be 
"supertagging/templates/render/tagged_items/default.html"

This default template is the last resort, below is a detail list of template 
paths that will be checked first

1. template argument - this is a full path starting in your templates dir
2. template_path + `stype` + `app` + `model` + `suffix` - for :ref:`api_supertag` and :ref:`api_supertagrelation` a type, model, app and suffix will be added.
    * supertagging/render/tags/<stype>/<app>__<model>__<suffix>.html
    * supertagging/render/tags/people/stories__story__custom.html
3. template_path + `stype` + `app` + `model` - Same as above but without the suffix
    * supertagging/render/tags/people/stories__story.html
4. template_path + `stype` + default + `suffix` - Same as #2 except not `app` and `model`
    * supertagging/render/tags/people/default__custom.html
5. template_path + `stype` + default - Same as #4 except without the suffix
    * supertagging/render/tags/people/default.html
6. template_path + default - the last possible path to look for the template
    * supertagging/render/tags/default.html

.. note::

    As stated in #2 of the list above, `stype` only applies to :ref:`api_supertag` and :ref:`api_supertagrelation` 
    since :ref:`api_supertaggeditem` and :ref:`api_supertaggedrelationitem` 
    doesn't contain the `stype` field. It will simply not be part of the path.
    
Template Context
----------------

:ref:`api_supertag` and :ref:`api_supertagrelation` has only it self returned 
in the context

* **obj** - self
    
:ref:`api_supertaggeditem` and :ref:`api_supertaggedrelationitem` has 2 conext 
variables

* **obj** - the generic related item
* **content** - self