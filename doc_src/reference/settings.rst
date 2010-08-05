.. _reference_settings:

Settings
========

.. contents::
   :depth: 3

Here is a list of all the SuperTagging settings and there uses.

.. _settings_default_process_type:

SUPERTAGGING_DEFAULT_PROCESS_TYPE
*********************************

Tells the default process type for OpenCalais to process the data. 

There are 4 options that can be supplied. Default is `TEXT/RAW`

    * TEXT/RAW
    * TEXT/HTML
    * TEXT/HTMLRAW
    * TEXT/XML

.. _setting_enabled:

SUPERTAGGING_ENABLED
********************

Weather or not supertagging is enabled. Will not process any objects if False.

.. _setting_calais_api_key:

SUPERTAGGING_CALAIS_API_KEY
***************************

Your OpenCalais API Key

.. _setting_auto_process:

SUPERTAGGING_AUTO_PROCESS
*************************

If True, will set up post_save and post_delete signals to process the data.

.. _setting_use_queue:

SUPERTAGGING_USE_QUEUE
**********************

Weather to use the Queue system. When a object is saved, it will be saved 
to a queue for later processing. A management command is included for you 
to process the queue.

.. _setting_modules:

SUPERTAGGING_MODULES
********************

This settings is a dictionary that specifies all the models, fields 
and options.

Example of specifying the models

.. code-block:: python

    SUPERTAGGING_MODULES = {
        'stories.story': {},
    }
    
.. code-block:: python
    
    SUPERTAGGING_MODULES = {
        'stories.story': {},
        'media.image': {},
        'blog.entry': {},
    }
    
The values of the models is a dictionary, where the fields and 
options are specified.
    
Possible values:

    * **fields** - List of dictionaries that specify field names and its options
    * **match_kwargs** - A dictionary of extra query parameters to check when processing instances of the model
        * Performs an extra .get(\*\*kwargs) on the instance to ensure it validates against the extra kwargs. *(Optional)*
    * **date_field** - The name of the field to retrieve the instance date. 
                       If this is not specified, supertagging will try to 
                       retrieve the data from the instance 
                       `_meta.get_latest_by` or `_meta.ordering`. This field 
                       is saved into SuperTaggedItem for later sorting by the 
                       items date. *(Optional)*
        
Here is and example for fields, date_field and match_kwargs

.. code-block:: python

    SUPERTAGGING_MODULES = {
        'stories.story': {
            'fields': [{'name': 'body'},],
            'match_kwargs': {'status__in': [1,2,3,], 
                             'published_date__isnull': False},
            'date_field': 'published_date'
        }
    }
    
Fields can be any number of fields in an instance as well.
    
.. code-block:: python

    SUPERTAGGING_MODULES = {
        'stories.story': {
            'fields': [{'name': 'body',
                       'name': 'tease',
                       'name': 'kicker'},],
            
        }
    }
    

    
Here is a list of the different options that can be specified for each field

* **name** - The name of the field *(Required)*
* **process_type** - This is the process type that calais will use when 
                     tagging the data, possible values are "TEXT/RAW", 
                     "TEXT/HTML" and "TEXT/XML", Default is 
                     "TEXT/RAW" *(Optional)*
* **markup** - True|False, tells SuperTagging weather to markup this field or 
               not. Default is False *(Optional)*


A complete example:

.. code-block:: python

    SUPERTAGGING_MODULES = {
        'stories.story': {
            'fields': [{'name': 'body',
                       'process_type': 'TEXT/HTML',
                       'markup': True},
                      {'name': 'tease'},
                      {'name': 'kicker',
                       'markup': True}],
            'match_kwargs': {'status__in': [1,2,3,], 
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
    
These next two settings are options for open calais.

.. _setting_calais_user_directives:

SUPERTAGGING_CALAIS_USER_DIRECTIVES
***********************************

View `Input Parameters <http://www.opencalais.com/documentation/calais-web-service-api/forming-api-calls/input-parameters>`_ on OpenCalais.com for more information.

.. _setting_calais_processing_directives:

SUPERTAGGING_CALAIS_PROCESSING_DIRECTIVES
*****************************************

View `Input Parameters <http://www.opencalais.com/documentation/calais-web-service-api/forming-api-calls/input-parameters>`_ on OpenCalais.com for more information.

.. _setting_process_relations:

SUPERTAGGING_PROCESS_RELATIONS
******************************
    
Weather or not to include the tag relations (Events/Facts) 
returned by OpenCalais
    
.. _setting_process_topics:
    
SUPERTAGGING_PROCESS_TOPICS
***************************  

Weather or not to include the topics returned by OpenCalais. These will 
simply be added as tags, but will not include tag details such as relevance.  

.. _setting_register_models:

SUPERTAGGING_REGISTER_MODELS
****************************

If True, an additional attribute will be avilable in a model's instance for 
easy query related access to SuperTagging.

.. _setting_debug:

SUPERTAGGING_DEBUG
******************

If True, errors will fail loudly in order to debug the code.

.. _setting_tag_type_exclusions:

SUPERTAGGING_TAG_TYPE_EXCLUSIONS
********************************

Tag types as strings to exclude from being added. These tags should be all 
the "Entities" listed on the following link.

`OpenCalais Entities, Events and Facts <http://www.opencalais.com/documentation/calais-web-service-api/api-metadata/entity-index-and-definitions>`_

.. _setting_rel_type_exclusions:

SUPERTAGGING_REL_TYPE_EXCLUSIONS
********************************

Same as above but these are the relations and are shown on the following link 
as "Events and Facts"

`OpenCalais Entities, Events and Facts <http://www.opencalais.com/documentation/calais-web-service-api/api-metadata/entity-index-and-definitions>`_

.. _setting_resolve_property_keys:


SUPERTAGGING_SUBSTITUTE_TAG_UPDATE
**********************************

When True, and then a substitute is specified in :ref:`api_supertag` all 
associated :ref:`api_supertaggeditem` and :ref:`api_supertagrelation` will be 
updated with the new tag.

SUPERTAGGING_RESOLVE_PROPERTY_KEYS
**********************************

If True, supertagging will try resolve the Calais ID to a tag name.

.. _setting_only_non_tagged_objects:

SUPERTAGGING_ONLY_NON_TAGGED_OBJECTS
************************************

If True, will only process objects that have not been tagged before.

.. _setting_min_relevance:

SUPERTAGGING_MIN_RELEVANCE
**************************

Integer between 0 and 1000, will only save tags that have a higher relevance 
that this setting. Topics do not use this value since they return 
no relevance.

.. _setting_min_relevance_markup:

SUPERTAGGING_MIN_RELEVANCE_MARKUP
*********************************

Integer between 0 and 1000, tells supertagging the min relevance to use when 
marking up the content.

.. _setting_use_freebase:

SUPERTAGGING_USE_FREEBASE
*************************

Weather or not to use Freebase to disambiguate the tags.

.. _setting_freebase_type_mapping:

SUPERTAGGING_FREEBASE_TYPE_MAPPINGS
***********************************

For better disambiguation, use this setting to map calais types to 
freebase types.

.. _setting_freebase_retrieve_descriptions:

SUPERTAGGING_FREEBASE_RETRIEVE_DESCRIPTIONS
*******************************************

If the display fields are enabled, you can have freebase retrieve the 
description for the tags.

.. _setting_freebase_description_url:

SUPERTAGGING_FREEBASE_DESCRIPTION_URL
*************************************

The first part of the url where to retrieve the descriptions.

.. _setting_markup:

SUPERTAGGING_MARKUP
*******************

Weather or not to markup is enabled.

.. _setting_markup_field_suffix:

SUPERTAGGING_MARKUP_FIELD_SUFFIX
********************************

If markup is enabled, supertagging will add a field to the instance with the 
marked up content, this setting specifies the prefix. Default is 'tagged'

IE: if 'body' field is marked for tagging, by default a field called 
'tagged_body' will be available in the instance that contains the content 
with marked up content.

.. _setting_markup_excludes:

SUPERTAGGING_MARKUP_EXCLUDES
****************************

List of strings of values to exclude from being marked up, for example, 
OpenCalais returns 'his', 'her', 'him' etc. in reference to a tag.

.. _setting_include_display_fields:

SUPERTAGGING_INCLUDE_DISPLAY_FIELDS
***********************************

Weahter or not to include 3 extra fields for display purposes.

* **description** - a text field
* **icon** - a image field
* **related** - a many2many field to 'self' (SuperTag)

.. _setting_default_storage:

SUPERTAGGING_DEFAULT_STORAGE
****************************

Default file storage used for the icon display field

.. _setting_contenttype_name_mapping:

SUPERTAGGING_CONTENTTYPE_NAME_MAPPING
*************************************

A dict of mapped content type ids to names, used for the views

.. code-block:: python
    
    {34, 'stories',
     83, 'images'}
     
Where the key is the content type id and the value is the string 
used in the url

/supertagging/tag/barack_obama/**stories**/

/supertagging/tag/barack_obama/**images**/

This was done in order to make readable urls.

