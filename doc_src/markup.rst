.. _markup:

Markup
======

This is a way to populate your content with extra content in relation to the 
tags. The most common way would be to replace where the tags are located with 
links to another section of your site with more information.

Setup
*****

In the settings you will need to have

.. code-block:: python

    SUPERTAGGING_MARKUP = True
    
How It Works
************

When SuperTagging loads up and markup is enabled, it will add an additional 
attribute for every field specified in :ref:`setting_modules`.

.. code-block:: python


    SUPERTAGGING_MARKUP = True
    MARKUP_FIELD_SUFFIX = "tagged"
    SUPERTAGGING_MODULES = {
       'stories.story': 
            {'fields':[
                {'name': 'body',
                 'markup_handler': 'MyCustomHandler'}]},
        'media.image':
            {'fields':[
                {'name': 'caption'}]},
        'blog.entry':
            {'fields':[
                {'name': 'content'},
                {'name': 'tease',
                 'markup': False}]}
    }

Lets take the code sample above as an example. We notice that markup is 
enabled and the prefix for the markup fields is `tagged`. The first module 
is a **story** model, and the field named **body** is marked to be tagged. 
It also specifies a custom markup handler, which we'll get to a bit later. 
The next model is a **image** model and the **caption** field is marked for 
tagging. The last model is an **entry** model and it has 2 fields marked for 
tagging, **content** and **tease**, but tease is not to be marked up.

After `SuperTagging` is done loading you will end up with three additional
attributes for the three different models.

* **story model**
    * tagged_body
* **image model**
    * tagged_caption
* **entry**
    * tagged_content
    
Notice that the a 'tagged_tease' does not exist for the **entry** model.
    
Markup handler
**************
    
Each field will be assigned a `MarkupHandler` object, which can be found
in `supertagging/markup.py` file. This module does all the markup processing
for you on the fly. If an error occurs, since the original content is never 
touched, the original content is returned.

You can create your own custom handler as well.

.. code-block:: python

    from supertagging.markup import MarkupHandler
    
    class MyCustomHandler(MarkupHandler):
        def handle(self, instance):
            # DO YOUR CUSTOM MARKUP HERE
            return "MARKED UP CONTENT"
            
The `handle` method needs to return a string of the marked up content.

If you want a create a custom handler but use the default markup method, your code
might look something like this:

.. code-block:: python

    from supertagging.markup import MarkupHandler, markup_content
    
    class MyCustomHandler(MarkupHandler):
        def handle(self, instance):
            # DO SOMETHING HERE
            return markup_content(instance, self.field)
            
            
Markup Template
***************

`markup.html`

This template is used to render the tags in a marked up state. Below is the 
default html rendered.

.. code-block:: django

    <a href="#">{{ actual_value }}</a>
    
**Context**

    * actual_value - the value of the tag, this might be the same as the tag name or a reference to the tag, IE: 'his', 'her' etc.
    * tag - a `SuperTag` instance

            
Caching
*******

There is a build-in cache for the markup, since every time we call this new
attribute, a couple database calls need to happen to retrieve all the tags
and its meta data for an instance.

You can change the default timeout for this cache by changing the following setting

.. code-block:: python

    SUPERTAGGING_MARKUP_CONTENT_CACHE_TIMEOUT = 3600
    
    
Gotchas
*******

In some cases, after enabling markup and successfully tagging an instance the markup
does not show up. Two things might cause this, 1 is the cache has not expired and 2
the markup did not validate. 

Markup validation happens when the markup field is called and the data retrieved does
not match what the instance has stored. This usually means that the instance was edited
and the field that gets tagged was changed and it has not been re-processed by 
OpenCalais.