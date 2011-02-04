from django.conf import settings

DEFAULT_PROCESS_TYPE = getattr(settings, 'SUPERTAGGING_DEFAULT_PROCESS_TYPE', 'TEXT/RAW')

# The models/fields to process
MODULES = getattr(settings, 'SUPERTAGGING_MODULES', {})

# OpenCalais settings
USER_DIR = getattr(settings, 'SUPERTAGGING_CALAIS_USER_DIRECTIVES', {})
PROCESSING_DIR = getattr(settings, 'SUPERTAGGING_CALAIS_PROCESSING_DIRECTIVES', {})
PROCESS_RELATIONS = getattr(settings, 'SUPERTAGGING_PROCESS_RELATIONS', False)
PROCESS_TOPICS = getattr(settings, 'SUPERTAGGING_PROCESS_TOPICS', False)

# If True, raise errors when errors occur
ST_DEBUG = getattr(settings, 'SUPERTAGGING_DEBUG', False)

# Tags Types to exclude, this will exclude tags of a certian type 
# from being saved.
EXCLUSIONS = getattr(settings, 'SUPERTAGGING_TAG_TYPE_EXCLUSIONS', [])

# Relation Types to exclude, this will exlucde relations of a certian 
# type from being saved.
REL_EXLCUSIONS = getattr(settings, 'SUPERTAGGING_REL_TYPE_EXCLUSIONS', [])

# Tags will be saved, but not returned in the queries * NOT IMPLEMENTED *
QUERY_EXCLUSIONS = getattr(settings, 'SUPERTAGGING_TAG_TYPE_QUERY_EXCLUSIONS', [])

# When resolving related tags, resolve the name or keep the UID
RESOLVE_KEYS = getattr(settings, 'SUPERTAGGING_RESOLVE_PROPERTY_KEYS', True)

# Your Open-Calais API_KEY
API_KEY = getattr(settings, 'SUPERTAGGING_CALAIS_API_KEY', None)

# Auto process tags, (sets up post save and delete signals)
AUTO_PROCESS = getattr(settings, 'SUPERTAGGING_AUTO_PROCESS', False)

# If the save signal is used, this settings will tell the handler to 
# only add objects that have no tags. Objects that do have tags but
# needs to be re-processed will have to be added to the queue manually.
ONLY_NON_TAGGED_OBJECTS = getattr(settings, 'SUPERTAGGING_ONLY_NON_TAGGED_OBJECTS', False)

# Set the process to be enabled. This will allow enabling and disabling
# the processing of tagging while preserving AUTO_PROCESS
ENABLED = getattr(settings, 'SUPERTAGGING_ENABLED', True)

# Minimum relevance score needed when adding tags
MIN_RELEVANCE = getattr(settings, 'SUPERTAGGING_MIN_RELEVANCE', 0)

# Minimun relevance score needed when marking up the content
MIN_RELEVANCE_MARKUP = getattr(settings, 'SUPERTAGGING_MIN_RELEVANCE_MARKUP', MIN_RELEVANCE)

# If True, will register your model(s), this will add a attribute to your 
# model(s) to retrieve the tags.
REGISTER_MODELS = getattr(settings, 'SUPERTAGGING_REGISTER_MODELS', False)

# If True, when a substitute is supplied all the Tagged Items and Relation 
# Tagged Items will be set with the substitute tag. If False, the Tagged Items
# and the Relation Tagged Items will still have the original tag. This is a
# way to preserve the old tag data.
SUBSTITUTE_TAG_UPDATE = getattr(settings, 'SUPERTAGGING_SUBSTITUTE_TAG_UPDATE', False)

# If True, all related content to a tag will be removed, items from models 
# `SuperTaggedItem` and `SuperTaggedRelationItem`
REMOVE_REL_ON_DISABLE = getattr(settings, 'SUPERTAGGING_REMOVE_REL_ON_DISABLE', False)

# Optional, use freebase to disambiguate tags
USE_FREEBASE = getattr(settings, 'SUPERTAGGING_USE_FREEBASE', False)

# Only used if USE_FREEBASE is True, maps calais types to freebase types
FREEBASE_TYPE_MAPPINGS = getattr(settings, 'SUPERTAGGING_FREEBASE_TYPE_MAPPINGS', {})

# If True and INCLUDE_DISPLAY_FIELDS is True, will try to retreive
# a description for the tag via Freebase and save it to the description field
FREEBASE_RETRIEVE_DESCRIPTIONS = getattr(settings, 'SUPERTAGGING_FREEBASE_RETRIEVE_DESCRIPTIONS', False)

# The first part of the url to retreive descriptions from freebase
FREEBASE_DESCRIPTION_URL = getattr(settings, 'SUPERTAGGING_FREEBASE_DESCRIPTION_URL', "http://www.freebase.com/api/trans/raw")

# If set true and auto process is on, will add objects to a queue enstead 
# of processing the item on the save. Should be used with the management
# command.
USE_QUEUE = getattr(settings, 'SUPERTAGGING_USE_QUEUE', False)

# To allow the registration of the models that are also tagged.
MARKUP = getattr(settings, 'SUPERTAGGING_MARKUP', False)

# The suffix of the field created when using markup.
MARKUP_FIELD_SUFFIX = getattr(settings, 'SUPERTAGGING_MARKUP_FIELD_SUFFIX', "tagged")

# List of strings that will be excluded from being marked up, ex: his, her, him etc.
MARKUP_EXCLUDES = getattr(settings, 'SUPERTAGGING_MARKUP_EXCLUDES', [])

# Integer for the cache timeout for the markup content.
MARKUP_CONTENT_CACHE_TIMEOUT = getattr(settings, 'SUPERTAGGING_MARKUP_CONTENT_CACHE_TIMEOUT', 3600)

# Weather or not to include fields, description, icon, related
INCLUDE_DISPLAY_FIELDS = getattr(settings, 'SUPERTAGGING_INCLUDE_DISPLAY_FIELDS', True)

# Default image storage, for the tag icon
DEFAULT_STORAGE = getattr(settings, 'SUPERTAGGING_DEFAULT_STORAGE', settings.DEFAULT_FILE_STORAGE)

# Names used enstead of integers when displaying the content. 
# EX: {'stories': 322, 'photos': 129, 'entries': 102, 'polls': 754}
# Where the value is the actual content type id and the key is the name
# used in the url. 
#   supertagging/tags/barack_obama/stories/
#   supertagging/tags/world_cup/photos/
CONTENTTYPE_NAME_MAPPING = getattr(settings, "SUPERTAGGING_CONTENTTYPE_NAME_MAPPING", {})
