.. _installation:

Installation
============

Download SuperTagging
*********************

There are a couple ways for you to get Django-SuperTagging,

    1. Clone the git repository `from here <http://opensource.washingtontimes.com/projects/supertagging/>`_
    2. Download the latest build from our opensource site `here <http://opensource.washingtontimes.com/pypi/simple/supertagging/>`_
    3. Use PIP to install from our opensource site pypi 
        * pip install --extra-index-url=http://opensource.washingtontimes.com/pypi/simple/ supertagging


Dependencies
************

* `simplejson <http://code.google.com/p/simplejson/>`_ *(Required)*
* `freebase <http://code.google.com/p/freebase-python/>`_ *(Optional)*


Add SuperTagging to your project
********************************

Add to INSTALLED_APPS

.. code-block:: python

    INSTALLED_APPS = (
        ...
        supertagging,
        ...
    )
    
Run syncdb::

    >>> ./manage.py syncdb
    