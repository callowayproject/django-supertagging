.. _reference_settings:

========
Settings
========

.. contents::
   :depth: 3

The default SuperTagging settings are:

.. code-block:: python

	SUPERTAGGING_SETTINGS = {
	    'ENABLED': False,
	    'DEBUG': False,
	    'WATCHED_FIELDS': {},
	    'AUTO_PROCESS': False,
	    'ONLY_NON_TAGGED_OBJECTS': False,
	    'CONTENTTYPE_NAME_MAPPING': {},
	    'INCLUDE_DISPLAY_FIELDS': True,
	    'REGISTER_MODELS': True,
	    'REMOVE_REL_ON_DISABLE': True,
	    'RESOLVE_PROPERTY_KEYS': True,
	    'SUBSTITUTE_TAG_UPDATE': True,
	    'USE_QUEUE': False,
	    'FILE_STORAGE': 'django.core.files.storage.FileSystemStorage',
	    'EXCLUSIONS': {
	        'MIN_RELEVANCE': 0,
	        'REL_TYPE_EXCLUSIONS': [],
	        'TAG_TYPE_EXCLUSIONS': [],
	        'TAG_TYPE_QUERY_EXCLUSIONS': []},
	    'FREEBASE': {
	        'DESCRIPTION_URL': 'http://www.freebase.com/api/trans/raw',
	        'ENABLED': False,
	        'RETRIEVE_DESCRIPTIONS': False,
	        'TYPE_MAPPINGS': {}},
	    'MARKUP': {
	        'CONTENT_CACHE_TIMEOUT': 3600,
	        'ENABLED': False,
	        'EXCLUDE': [],
	        'FIELD_SUFFIX': 'tagged',
	        'MIN_RELEVANCE': 0},
	    'OPEN_CALAIS': {
	        'API_KEY': '',
	        'DEFAULT_PROCESS_TYPE': 'TEXT/RAW',
	        'PROCESSING_DIRECTIVES': {
	            'calculateRelevanceScore': True,
	            'contentType': 'TEXT/RAW',
	            'docRDFaccessible': True,
	            'enableMetadataType': '',
	            'outputFormat': 'application/json',
	            'reltagBaseURL': ''},
	        'PROCESS_RELATIONS': True,
	        'PROCESS_SOCIALTAGS': True,
	        'PROCESS_TOPICS': True,
	        'USER_DIRECTIVES': {
	            'allowDistribution': False,
	            'allowSearch': False,
	            'externalID': '',
	            'submitter': 'python-calais client v.1.5'}},
	}


.. _setting_enabled:

ENABLED
=======

**Default:** ``False``

Whether or not SuperTagging is enabled. Will not process any objects if ``False``\ . This allows starting and stopping tag processing while preserving the value of :ref:`setting_auto_process`\ .

.. _setting_debug:

DEBUG
=====

**Default:** ``False``

If ``True``\ , errors will fail loudly in order to debug the code.


.. _setting_modules:

WATCHED_FIELDS
==============

**Default:** ``{}``

This settings is a dictionary that specifies all the models, fields 
and options.

The keys of the dictionary are strings in the format ``app_name.model_name``\ . The value of each key is a dictionary, where the fields and other options are specified.

* **fields** - *(Required)* List of dictionaries that specify field names and its options

  * **name** - *(Required)* ``String`` The name of the field
  * **process_type** - *(Optional)* ``String`` The process type that OpenCalais should use when tagging the data, possible values are ``TEXT/RAW``\ , ``TEXT/HTML``\ , ``TEXT/HTMLRAW``\ , or ``TEXT/XML``\ . Default is the value of :ref:`settings_default_process_type`\ .
  * **markup** - *(Optional)* ``bool`` Should SuperTagging automatically markup this field? Default is ``False``\ .
  * **combine_fields** - *(Optional)* ``list`` A list of two or more fields on the model to combine into one submission to OpenCalais for processing. Markup is not available for these combined fields.

* **match_kwargs** - *(Optional)* ``dict`` A dictionary of extra query parameters to check when processing instances of the model. Performs an extra ``.get(**kwargs)`` on the instance to ensure it validates against the extra query parameters. 
* **date_field** - *(Optional)* ``String`` The name of the field to retrieve the instance date. If this is not specified, supertagging will try to retrieve the data from the instance ``_meta.get_latest_by`` or ``_meta.ordering``\ . This field is saved into ``SuperTaggedItem`` to allow easy sorting of the items by date. 


Here is a complete example:

.. code-block:: python

	SUPERTAGGING_MODULES = {
	    'stories.story': {
	        'fields': [{
	                'name': 'body',
	                'process_type': 'TEXT/HTML',
	                'markup': True
	            }, {
	                'name': 'tease'
	            }, {
	                'name': 'kicker',
	                'markup': True
	            }],
	        'match_kwargs': {
	            'status__in': [1,2,3,], 
	            'published_date__isnull': False},
	        'date_field': 'published_date'
	    },
	    'media.image': {
	        'fields': [{'name': 'caption',
	                    'process_type': 'TEXT/HTML',
	                    'markup': True}],
	        'date_field': 'creation_date'
	    }
	}


.. _setting_include_display_fields:

INCLUDE_DISPLAY_FIELDS
======================

**Default:** ``True``

Should SuperTagging include three extra fields for display purposes:

* **description** - a text field
* **icon** - a image field
* **related** - a many2many field to 'self' (SuperTag)

.. _setting_auto_process:

AUTO_PROCESS
============

**Default:** ``False``

If True, will set up post_save and post_delete signals to process the data.

.. _setting_only_non_tagged_objects:

ONLY_NON_TAGGED_OBJECTS
=======================

**Default:** ``False``

Used with :ref:`setting_auto_process`\ . If ``True``\ , will only process objects that have not been tagged before. Objects that have tags but need re-processing must be added to the queue manually.

If ``False``\ , process all objects.


.. _setting_resolve_property_keys:

RESOLVE_PROPERTY_KEYS
=====================

**Default:** ``True``

If ``True``\ , SuperTagging will try resolve the Calais ID to a tag name.

.. _setting_register_models:

REGISTER_MODELS
===============

**Default:** ``False``

If ``True``\ , an additional attribute will be avilable in a model's instance for easy query related access to SuperTagging.

.. _setting_substitute_tag_update:

SUBSTITUTE_TAG_UPDATE
=====================

**Default:** ``False``

When ``True``\ , and a substitute is specified in :ref:`api_supertag` all 
associated :ref:`api_supertaggeditem` and :ref:`api_supertagrelation` will be 
updated with the new tag.

.. _setting_remove_rel_on_disable:

REMOVE_REL_ON_UPDATE
====================

**Default:** ``False``

If ``True``\ , all content related to a tag is removed (items from models 
:ref:`api_supertaggeditem` and :ref:`api_supertaggedrelationitem`\ .


.. _setting_default_storage:

FILE_STORAGE
============

**Default:** ``settings.DEFAULT_FILE_STORAGE``

Default file storage used for the icon display field.

.. _setting_use_queue:

USE_QUEUE
=========

**Default:** ``False``

If ``True``\ , use the queuing system. When a object is saved, it will be saved to a queue for later processing. A management command is included for you to process the queue.

If ``False``\ , process the object on save.


.. _setting_contenttype_name_mapping:

CONTENTTYPE_NAME_MAPPING
========================

**Default:** ``{}``

A dict of mapped content type ids to names, used for the views

.. code-block:: python
    
	{
	    34: 'stories',
	    83: 'images',
	}
     
Where the key is the content type id and the value is the string 
used in the url:

This:

	/supertagging/tag/barack_obama/**stories**/

	/supertagging/tag/barack_obama/**images**/

instead of this:

	/supertagging/tag/barack_obama/**34**/

	/supertagging/tag/barack_obama/**83**/

This was done in order to make readable urls.


OPEN_CALAIS
===========

.. _settings_default_process_type:

DEFAULT_PROCESS_TYPE
********************

**Default:** ``TEXT/RAW``

Tells the default process type for OpenCalais to process the data. 

There are four options that can be supplied.

    * ``TEXT/RAW``
    * ``TEXT/HTML``
    * ``TEXT/HTMLRAW``
    * ``TEXT/XML``

.. _setting_calais_api_key:

API_KEY
*******

**Default:** ``''``

Your OpenCalais API Key


These next two settings are options for open calais.

.. _setting_calais_user_directives:

USER_DIRECTIVES
***************

**Default:** 

.. code-block:: python

	{
	    "allowDistribution": False, 
	    "allowSearch": False, 
	    "externalID": '',
	    "submitter": "python-calais client v.1.5",
	}

View `Input Parameters <http://www.opencalais.com/documentation/calais-web-service-api/forming-api-calls/input-parameters>`_ on OpenCalais.com for more information.

.. _setting_calais_processing_directives:

PROCESSING_DIRECTIVES
*********************

**Default:**

.. code-block:: python

	{
	    "contentType": "TEXT/RAW", 
	    "outputFormat": "application/json", 
	    "reltagBaseURL": '', 
	    "calculateRelevanceScore": True, 
	    "enableMetadataType": '', 
	    "docRDFaccessible": True, 
	}


View `Input Parameters <http://www.opencalais.com/documentation/calais-web-service-api/forming-api-calls/input-parameters>`_ on OpenCalais.com for more information.

.. _setting_process_relations:

PROCESS_RELATIONS
*****************

**Default:** ``False``

If ``True``\ , save the tag relations (Events/Facts) returned by OpenCalais
    
.. _setting_process_topics:
    
PROCESS_TOPICS
**************

**Default:** ``False``

If ``True``\ , save the topics returned by OpenCalais. These will simply be added as tags, but will not include all tag details.  


.. _setting_process_socialtags:

PROCESS_SOCIALTAGS
******************

**Default:** ``False``

If ``True``\ , save the social tags returned by OpenCalais. These will simply be added as tags, but will not include all tag details.



EXCLUSIONS
==========

.. _setting_tag_type_exclusions:

TAG_TYPE_EXCLUSIONS
*******************

**Default:** ``[]``

Tag types as strings to exclude from being added. These tags should be all 
the "Entities" listed on the following link.

`OpenCalais Entities, Events and Facts <http://www.opencalais.com/documentation/calais-web-service-api/api-metadata/entity-index-and-definitions>`_

.. _setting_rel_type_exclusions:

REL_TYPE_EXCLUSIONS
*******************

**Default:** ``[]``

Same as above but these are the relations and are shown on the following link 
as "Events and Facts"

`OpenCalais Entities, Events and Facts <http://www.opencalais.com/documentation/calais-web-service-api/api-metadata/entity-index-and-definitions>`_


TAG_TYPE_QUERY_EXCLUSIONS
*************************

**NOT IMPLEMENTED (YET)**

Tags will be saved, but not returned in the queries

.. _setting_min_relevance:

MIN_RELEVANCE
*************

**Default:** ``0``

Integer between 0 and 1000, will only save tags that have a higher relevance 
that this setting.





FREEBASE
========


.. _setting_use_freebase:

ENABLED
*******

**Default:** ``False``

Use Freebase to disambiguate the tags?

.. _setting_freebase_type_mapping:

TYPE_MAPPINGS
*************

**Default:** ``{}``

For better disambiguation, use this setting to map Calais types to freebase types.

.. _setting_freebase_retrieve_descriptions:

RETRIEVE_DESCRIPTIONS
*********************

**Default:** ``False``

If the display fields are enabled, you can have freebase retrieve the description for the tags.

.. _setting_freebase_description_url:

DESCRIPTION_URL
***************

**Default:** ``"http://www.freebase.com/api/trans/raw"``

The first part of the url from where to retrieve the descriptions.


MARKUP
======

.. _setting_markup:

ENABLED
*******

**Default:** ``False``

Is automatic markup of content enabled?

.. _setting_min_relevance_markup:

MIN_RELEVANCE
*************

**Default:** ``0``

Integer between 0 and 1000, tells SuperTagging the minimum relevance to use when marking up the content.

.. _setting_markup_field_suffix:

FIELD_SUFFIX
************

**Default:** ``"tagged"``

If markup is enabled, SuperTagging will add a field to the instance with the 
marked up content, this setting specifies the suffix. 

For example: if ``'body'`` field is marked for tagging, by default a field called ``'body__tagged'`` will be available in the instance that contains the content with marked up content.

.. _setting_markup_excludes:

EXCLUDES
********

**Default:** ``[]``

List of strings of values to exclude from being marked up. For example, 
OpenCalais returns 'his', 'her', 'him' etc. in reference to a tag.

.. _setting_markup_cache_timeout:

CONTENT_CACHE_TIMEOUT
*********************

**Default:** ``3600``

Cache timeout for the markup content in seconds.
