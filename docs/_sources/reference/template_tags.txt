.. _template_tags:

Template Tags
=============

.. contents::
   :depth: 4

Here is the list of current template tags, most of these are tags from
`Django Tagging <http://code.google.com/p/django-tagging/>`_ with some addtions


.. note::

    Tag names have changed slightly, the biggest difference is that now there
    is "super" prepended to them. This is so we don't clash with a project 
    that uses Django-Tagging and SuperTagging together.
    
    The following "Tags from Django-Tagging" section are a modified version 
    of Django-Tagging template tag documentation 

Tags from Django-Tagging
************************

The ``supertagging.templatetags.supertagging_tags`` module defines a number of
template tags which may be used to work with tags.

Tag reference
-------------

supertags_for_model
~~~~~~~~~~~~~~~~~~~

Retrieves a list of ``SuperTag`` objects associated with a given model and
stores them in a context variable.

Usage

.. code-block:: django

    {% supertags_for_model [model] as [varname] %}

The model is specified in ``[appname].[modelname]`` format.

Extended usage

.. code-block:: django

    {% supertags_for_model [model] as [varname] with counts %}


If specified - by providing extra ``with counts`` arguments - adds a
``count`` attribute to each tag containing the number of instances of
the given model which have been tagged with it.

Examples

.. code-block:: django

   {% supertags_for_model products.Widget as widget_tags %}
   {% supertags_for_model products.Widget as widget_tags with counts %}

supertag_cloud_for_model
~~~~~~~~~~~~~~~~~~~~~~~~

Retrieves a list of ``SuperTag`` objects for a given model, with tag cloud
attributes set, and stores them in a context variable.

Usage

.. code-block:: django

   {% supertag_cloud_for_model [model] as [varname] %}

The model is specified in ``[appname].[modelname]`` format.

Extended usage

.. code-block:: django

   {% supertag_cloud_for_model [model] as [varname] with [options] %}

Extra options can be provided after an optional ``with`` argument, with
each option being specified in ``[name]=[value]`` format. Valid extra
options are:

   ``steps``
      Integer. Defines the range of font sizes.

   ``min_count``
      Integer. Defines the minimum number of times a tag must have
      been used to appear in the cloud.

   ``distribution``
      One of ``linear`` or ``log``. Defines the font-size
      distribution algorithm to use when generating the tag cloud.

Examples

.. code-block:: django

   {% supertag_cloud_for_model products.Widget as widget_tags %}
   {% supertag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distribution=log %}

supertags_for_object
~~~~~~~~~~~~~~~~~~~~

Retrieves a list of ``SuperTag`` objects associated with an object and stores
them in a context variable.

Usage

.. code-block:: django

   {% supertags_for_object [object] as [varname] %}

Example

.. code-block:: django

    {% supertags_for_object foo_object as tag_list %}

supertagged_objects
~~~~~~~~~~~~~~~~~~~

Retrieves a list of instances of a given model which are tagged with a
given ``SuperTag`` and stores them in a context variable.

Usage

.. code-block:: django

   {% supertagged_objects [tag] in [model] as [varname] %}

The model is specified in ``[appname].[modelname]`` format.

The tag must be an instance of a ``SuperTag``, not the name of a tag.

Example

.. code-block:: django

    {% supertagged_objects comedy_tag in tv.Show as comedies %}
    
    
New Tags for SuperTagging
*************************

Below is a list of the new tags that can be used with SuperTagging

Tag reference
-------------

relations_for_supertag
~~~~~~~~~~~~~~~~~~~~~~

Usage

.. code-block:: django

    {% relations_for_supertag [tag] as [varname] %}
    {% relations_for_supertag [tag] as [varname] with type=[TYPE] %}

The tag must of an instance of a ``SuperTag``, not the name of a tag.

Example

.. code-block:: django

    {% relations_for_supertag state_tag as relations %}
    {% relations_for_supertag state_tag as relations with type=Quotation %}

relations_for_object
~~~~~~~~~~~~~~~~~~~~

Useage

.. code-block:: django
    
    {% relations_for_object [object] as [varname] %}
    {% relations_for_object [object] as [varname] with [type=TYPE]}
    
Example

.. code-block:: django

    {% relations_for_object story as story_relations %}
    {% relations_for_object story as story_relations with type=Quotation %}

relations_for
~~~~~~~~~~~~~

Returns a list of `SuperTagRelation` objects for a tag within a given object.

Useage

.. code-block:: django
    
    {% relations_for [tag] in [object] as [varname] %}
    
Example

.. code-block:: django

    {% relations_for state_tag in obj as obj_relations %}
    
supertag_render
~~~~~~~~~~~~~~~

Useage

.. code-block:: django

    {% supertag_render [SuperTag or SuperTaggedItem or SuperTagRelation or SuperTaggedRelationItem] [with] [suffix=S] [template=T] %}
    
Example

.. code-block:: django
    
    {% supertag_render tag %}
    {% supertag_render tagged_item with suffix=custom %}
    {% supertag_render rel_item with template=mycustomtemplates/supertags/custom.html %}
    
Only suffix OR template can be specified, but not both.

View :ref:`render` for more information about rendering.
