.. _installation:

Installation
============

Download SuperTagging
*********************

There are a couple ways for you to get Django-SuperTagging,

    1. Clone the git repository `from GitHub <https://github.com/callowayproject/django-supertagging>`_
    2. Use pip to install it from `PyPI <http://pypi.python.org/pypi/supertagging>`_

::

	pip install supertagging


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
    