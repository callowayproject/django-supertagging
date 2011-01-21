import os
from setuptools import setup, find_packages
import supertagging


try:
    reqs = open(os.path.join(os.path.dirname(__file__),'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name = 'supertagging',
    version=supertagging.get_version(),
    description = 'An interface to the Open Calais service for semantic markup.',
    author = 'Jose Soares',
    author_email = 'jsoares@washingtontimes.com',
    url = 'https://github.com/washingtontimes/django-supertagging',
    packages = find_packages(),
    include_package_data = True,
    install_requires = reqs,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ]
)
