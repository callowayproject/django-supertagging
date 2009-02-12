from django.conf import settings

DEFAULT_PROCESS_TYPE = 'TEXT/RAW'

# The models/fields to process
MODULES = getattr(settings, 'SUPERTAGGING_MODULES', {})
USER_DIR = getattr(settings, 'SUPERTAGGING_CALAIS_USER_DIRECTIVES', {})
PROCESSING_DIR = getattr(settings, 'SUPERTAGGING_CALAIS_PROCESSING_DIRECTIVES', {})
PROCESS_RELATIONS = getattr(settings, 'SUPERTAGGING_PROCESS_RELATIONS', False)
PROCESS_TOPICS = getattr(settings, 'SUPERTAGGING_PROCESS_TOPICS', False)

# If True, raise errors when errors occur
ST_DEBUG = getattr(settings, 'SUPERTAGGING_DEBUG', False)

# Tags (name) to exclude
EXLCUSIONS = getattr(settings, 'SUPERTAGGING_TAG_TYPE_EXCLUSIONS', [])

# When resolving related tags, resolve the name or keep the UID
RESOLVE_KEYS = getattr(settings, 'SUPERTAGGING_RESOLVE_PROPERTY_KEYS', True)

# Your Open-Calais API_KEY
API_KEY = getattr(settings, 'SUPERTAGGING_CALAIS_API_KEY', None)