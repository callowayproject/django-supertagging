from django.conf import settings
import warnings

DEFAULT_PROCESSING_DIRECTIVES = {
    "contentType": "TEXT/RAW", 
    "outputFormat": "application/json", 
    "reltagBaseURL": '', 
    "calculateRelevanceScore": True, 
    "enableMetadataType": '', 
    "docRDFaccessible": True, 
}
DEFAULT_USER_DIRECTIVES = {
    "allowDistribution": False, 
    "allowSearch": False, 
    "externalID": '',
    "submitter": "python-calais client v.1.5",
}
DEFAULT_CALAIS_SETTINGS = {
    'API_KEY': '',
    # 'USER_DIRECTIVES': DEFAULT_USER_DIRECTIVES, 
    # 'PROCESSING_DIRECTIVES': DEFAULT_PROCESSING_DIRECTIVES,
    'PROCESS_RELATIONS': False,
    'PROCESS_TOPICS': False,
    'PROCESS_SOCIALTAGS': False,
    'DEFAULT_PROCESS_TYPE': 'TEXT/RAW', 
}
DEFAULT_EXCLUSIONS = {
    'TAG_TYPE_EXCLUSIONS': [], # exclude tags of certian types from saving
    'REL_TYPE_EXCLUSIONS': [], # exclude relations of certian types from saving
    'TAG_TYPE_QUERY_EXCLUSIONS': [], # Tags will be saved, but not returned in 
                                     # the queries * NOT IMPLEMENTED *
    'MIN_RELEVANCE': 0, # Minimum relevance to save a tag-object pair (0-1000)
}
DEFAULT_FREEBASE_SETTINGS = {
    'ENABLED': False, # use freebase to disambiguate tags
    'TYPE_MAPPINGS': {}, # maps calais types to freebase types
    'RETRIEVE_DESCRIPTIONS': False, # True: attempt to retreive description 
                                    # for the tag via Freebase and save it to 
                                    # the description field
    # The first part of the url to retreive descriptions from freebase
    'DESCRIPTION_URL': "http://www.freebase.com/api/trans/raw",
}
DEFAULT_MARKUP_SETTINGS = {
    'ENABLED': False, # True: Automatically provide a version of the content
                      # with the tags marked with links.
    'FIELD_SUFFIX': "tagged", # The suffix of the field created when using markup.
    'EXCLUDE': [], # List of strings that will be excluded from being marked up, eg: his, her, him etc.
    'CONTENT_CACHE_TIMEOUT': 3600, # Integer for the cache timeout for the markup content.
    'MIN_RELEVANCE': 0, # Minimum relevance of a tag to include it in 
                           # automatic markup of the content (0-1000)
}
DEFAULT_SETTINGS = {
    'ENABLED': False, # Enable supertagging. This will allow starting and 
                      # stopping tag processing while preserving AUTO_PROCESS
    'DEBUG': False, # If True, raise errors when errors occur
    'WATCHED_FIELDS': {}, # The models/fields to process
    'INCLUDE_DISPLAY_FIELDS': True, # True: include fields: display_name, description, icon, related
    'AUTO_PROCESS': False, # Set up post save and delete signals
    'ONLY_NON_TAGGED_OBJECTS': False, # If the save signal is used, 
                                      # True: tell the handler to only add objects 
                                      #       that have never had tags. Objects 
                                      #       that have tags but need re-processing 
                                      #       must be added to the queue manually.
                                      # False: handle all objects
    'RESOLVE_PROPERTY_KEYS': True, # True: resolve related tags' name, 
                                 # False: keep the UID
    'REGISTER_MODELS': False, # True: add an attribute to your model(s) to 
                              # retrieve the tags.
    'SUBSTITUTE_TAG_UPDATE': False,  # If True, when a substitute is supplied all the Tagged Items and Relation 
                              # Tagged Items will be set with the substitute tag. If False, the Tagged Items
                              # and the Relation Tagged Items will still have the original tag. This is a
                              # way to preserve the old tag data.
    'REMOVE_REL_ON_DISABLE': False, # True: all related content to a tag is
                                    # removed (items from models 
                                    # `SuperTaggedItem` and `SuperTaggedRelationItem`)
    'FILE_STORAGE': settings.DEFAULT_FILE_STORAGE, # For the tag icon
    'USE_QUEUE': False, # True: add objects to a queue for later processing 
                        # False: process the item on save.
    'CONTENTTYPE_NAME_MAPPING': {}, # Names used enstead of integers when displaying the content. 
                                    # EX: {'stories': 322, 'photos': 129, 'entries': 102, 'polls': 754}
                                    # Where the value is the actual content type id and the key is the name
                                    # used in the url. 
                                    #   supertagging/tags/barack_obama/stories/
                                    #   supertagging/tags/world_cup/photos/
    # 'OPEN_CALAIS': DEFAULT_CALAIS_SETTINGS,
    # 'EXCLUSIONS': DEFAULT_EXCLUSIONS,
    # 'MARKUP': DEFAULT_MARKUP_SETTINGS,
    # 'FREEBASE': DEFAULT_FREEBASE_SETTINGS,
}

USER_SETTINGS = dict(DEFAULT_SETTINGS.items() + getattr(settings, 'SUPERTAGGING_SETTINGS', {}).items())
USER_SETTINGS['OPEN_CALAIS'] = dict(DEFAULT_CALAIS_SETTINGS.items() + USER_SETTINGS.get('OPEN_CALAIS', {}).items())
USER_SETTINGS['OPEN_CALAIS']['USER_DIRECTIVES'] = dict(DEFAULT_USER_DIRECTIVES.items() + USER_SETTINGS['OPEN_CALAIS'].get('USER_DIRECTIVES', {}).items())
USER_SETTINGS['OPEN_CALAIS']['PROCESSING_DIRECTIVES'] = dict(DEFAULT_PROCESSING_DIRECTIVES.items() + USER_SETTINGS['OPEN_CALAIS'].get('PROCESSING_DIRECTIVES', {}).items())
USER_SETTINGS['EXCLUSIONS'] = dict(DEFAULT_EXCLUSIONS.items() + USER_SETTINGS.get('EXCLUSIONS', {}).items())
USER_SETTINGS['MARKUP'] = dict(DEFAULT_MARKUP_SETTINGS.items() + USER_SETTINGS.get('MARKUP', {}).items())
USER_SETTINGS['FREEBASE'] = dict(DEFAULT_FREEBASE_SETTINGS.items() + USER_SETTINGS.get('FREEBASE', {}).items())


ERR_MSG = "Setting %s is deprecated; use SUPERTAGGING_SETTINGS['%s'] instead."

DEP_SETTINGS = (
    # Old setting name, New setting name, local variable name
    ('SUPERTAGGING_MODULES', 'WATCHED_FIELDS', 'MODULES'),
    ('SUPERTAGGING_DEBUG', 'DEBUG', 'ST_DEBUG'),
    ('SUPERTAGGING_RESOLVE_PROPERTY_KEYS', 'RESOLVE_PROPERTY_KEYS', 'RESOLVE_KEYS'),
    ('SUPERTAGGING_AUTO_PROCESS', 'AUTO_PROCESS', 'AUTO_PROCESS'),
    ('SUPERTAGGING_ONLY_NON_TAGGED_OBJECTS', 'ONLY_NON_TAGGED_OBJECTS', 'ONLY_NON_TAGGED_OBJECTS'),
    ('SUPERTAGGING_ENABLED', 'ENABLED', 'ENABLED'),
    ('SUPERTAGGING_REGISTER_MODELS', 'REGISTER_MODELS', 'REGISTER_MODELS'),
    ('SUPERTAGGING_SUBSTITUTE_TAG_UPDATE', 'SUBSTITUTE_TAG_UPDATE', 'SUBSTITUTE_TAG_UPDATE'),
    ('SUPERTAGGING_REMOVE_REL_ON_DISABLE', 'REMOVE_REL_ON_DISABLE', 'REMOVE_REL_ON_DISABLE'),
    ('SUPERTAGGING_USE_QUEUE', 'USE_QUEUE', 'USE_QUEUE'),
    ('SUPERTAGGING_INCLUDE_DISPLAY_FIELDS', 'INCLUDE_DISPLAY_FIELDS', 'INCLUDE_DISPLAY_FIELDS'),
    ('SUPERTAGGING_DEFAULT_STORAGE', 'FILE_STORAGE', 'DEFAULT_STORAGE'),
    ("SUPERTAGGING_CONTENTTYPE_NAME_MAPPING", "CONTENTTYPE_NAME_MAPPING", "CONTENTTYPE_NAME_MAPPING"),
)

for dep_setting, new_setting, short_name in DEP_SETTINGS:
    if hasattr(settings, dep_setting):
        warnings.warn(ERR_MSG % (dep_setting, new_setting), DeprecationWarning)
        USER_SETTINGS[new_setting] = getattr(settings, dep_setting)
    globals().update({short_name: USER_SETTINGS[new_setting]})
        

DEP_CALAIS = (
    ('SUPERTAGGING_CALAIS_USER_DIRECTIVES', 'USER_DIRECTIVES', 'USER_DIR'),
    ('SUPERTAGGING_CALAIS_PROCESSING_DIRECTIVES', 'PROCESSING_DIRECTIVES', 'PROCESSING_DIR'),
    ('SUPERTAGGING_PROCESS_RELATIONS', 'PROCESS_RELATIONS', 'PROCESS_RELATIONS'),
    ('SUPERTAGGING_PROCESS_TOPICS', 'PROCESS_TOPICS', 'PROCESS_TOPICS'),
    ('SUPERTAGGING_PROCESS_SOCIALTAGS', 'PROCESS_SOCIALTAGS', 'PROCESS_SOCIALTAGS'),
    ('SUPERTAGGING_CALAIS_API_KEY', 'API_KEY', 'API_KEY'),
    ('SUPERTAGGING_DEFAULT_PROCESS_TYPE', 'DEFAULT_PROCESS_TYPE', 'DEFAULT_PROCESS_TYPE'),
)

for dep_setting, new_setting, short_name in DEP_CALAIS:
    if hasattr(settings, dep_setting):
        warnings.warn(ERR_MSG % (dep_setting, "OPEN_CALAIS']['%s" % new_setting), DeprecationWarning)
        USER_SETTINGS['OPEN_CALAIS'][new_setting] = getattr(settings, dep_setting)
    globals().update({short_name: USER_SETTINGS['OPEN_CALAIS'][new_setting]})

DEP_EXCLUSIONS = (
    ('SUPERTAGGING_TAG_TYPE_EXCLUSIONS', 'TAG_TYPE_EXCLUSIONS', 'EXCLUSIONS'),
    ('SUPERTAGGING_REL_TYPE_EXCLUSIONS', 'REL_TYPE_EXCLUSIONS', 'REL_EXLCUSIONS'),
    ('SUPERTAGGING_TAG_TYPE_QUERY_EXCLUSIONS', 'TAG_TYPE_QUERY_EXCLUSIONS', 'QUERY_EXCLUSIONS'),
    ('SUPERTAGGING_MIN_RELEVANCE', 'MIN_RELEVANCE', 'MIN_RELEVANCE'),
)

for dep_setting, new_setting, short_name in DEP_EXCLUSIONS:
    if hasattr(settings, dep_setting):
        warnings.warn(ERR_MSG % (dep_setting, "EXCLUSIONS']['%s" % new_setting), DeprecationWarning)
        USER_SETTINGS['EXCLUSIONS'][new_setting] = getattr(settings, dep_setting)
    globals().update({short_name: USER_SETTINGS['EXCLUSIONS'][new_setting]})


DEP_MARKUP = (
    ('SUPERTAGGING_MARKUP', 'ENABLED', 'MARKUP'),
    ('SUPERTAGGING_MIN_RELEVANCE_MARKUP', 'MIN_RELEVANCE', 'MIN_RELEVANCE_MARKUP'),
    ('SUPERTAGGING_MARKUP_FIELD_SUFFIX', 'FIELD_SUFFIX', 'MARKUP_FIELD_SUFFIX'),
    ('SUPERTAGGING_MARKUP_EXCLUDES', 'EXCLUDE', 'MARKUP_EXCLUDES'),
    ('SUPERTAGGING_MARKUP_CONTENT_CACHE_TIMEOUT', 'CONTENT_CACHE_TIMEOUT', 'MARKUP_CONTENT_CACHE_TIMEOUT'),
)

for dep_setting, new_setting, short_name in DEP_MARKUP:
    if hasattr(settings, dep_setting):
        warnings.warn(ERR_MSG % (dep_setting, "MARKUP']['%s" % new_setting), DeprecationWarning)
        USER_SETTINGS['MARKUP'][new_setting] = getattr(settings, dep_setting)
    globals().update({short_name: USER_SETTINGS['MARKUP'][new_setting]})

DEP_FREEBASE = (
    ('SUPERTAGGING_USE_FREEBASE', 'ENABLED', 'USE_FREEBASE',),
    ('SUPERTAGGING_FREEBASE_TYPE_MAPPINGS', 'TYPE_MAPPINGS', 'FREEBASE_TYPE_MAPPINGS'),
    ('SUPERTAGGING_FREEBASE_RETRIEVE_DESCRIPTIONS', 'RETRIEVE_DESCRIPTIONS', 'FREEBASE_RETRIEVE_DESCRIPTIONS'),
    ('SUPERTAGGING_FREEBASE_DESCRIPTION_URL', 'DESCRIPTION_URL', 'FREEBASE_DESCRIPTION_URL'),
)

for dep_setting, new_setting, short_name in DEP_FREEBASE:
    if hasattr(settings, dep_setting):
        warnings.warn(ERR_MSG % (dep_setting, "FREEBASE']['%s" % new_setting), DeprecationWarning)
        USER_SETTINGS['FREEBASE'][new_setting] = getattr(settings, dep_setting)
    globals().update({short_name: USER_SETTINGS['FREEBASE'][new_setting]})

globals().update(USER_SETTINGS)
