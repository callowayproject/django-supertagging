# These are all the settings that are used to configure supertagging

SUPERTAGGING_DEBUG = True
SUPERTAGGING_CALAIS_API_KEY = 'your key here'
SUPERTAGGING_CALAIS_USER_DIRECTIVES = {}
SUPERTAGGING_CALAIS_PROCESING_DIRECTIVES = {}
SUPERTAGGING_CALAIS_EXTERNAL_METADATA = {}
SUPERTAGGING_PROCESS_RELATIONS = True
SUPERTAGGING_PROCESS_TOPICS = True
# IS THIS REALLY NEEDED?
# The reason this was added was because url get caught by calais, though 
# they look bad in the list of tags (the full url), we can handle it here
# or perhaps the query? Should this method exclude the adding of these types
# or exclude the query from returning these types?
SUPERTAGGING_TAG_TYPE_EXCLUSIONS = ['url',]
#SUPERTAGGING_TAG_TYPE_QUERY_EXCLUSIONS = ['url',]
SUPERTAGGING_MODULES = {
    'app.model': {'fields':({'name': 'content', 'content_type':'TEXT/RAW'},
                            {'name': 'tease',},)}
}
# This value will try to resolve the key's found in a property list
# so that the name of the tag will be available, if True, this will
# result in extra lookups
SUPERTAGGING_RESOLVE_PROPERTY_KEYS = True