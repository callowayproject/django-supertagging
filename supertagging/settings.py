# These are all the settings that are used to configure supertagging

CALAUS_DEBUG = True
CALAIS_API_KEY = 'your key here'
CALAIS_USER_DIRECTIVES = {}
CALAIS_PROCESING_DIRECTIVES = {}
CALAIS_EXTERNAL_METADATA = {}
CALAIS_PROCESS_RELATIONS = True
CALAIS_PROCESS_TOPICS = True
# IS THIS REALLY NEEDED?
# The reason this was added was because url get caught by calais, though 
# they look bad in the list of tags (the full url), we can handle it here
# or perhaps the query? Should this method exclude the adding of these types
# or exclude the query from returning these types?
CALAIS_ENTITY_TYPE_EXCLUSIONS = ['url',]
CALAIS_MODULES = {
    'app.model': {'fields':({'name': 'content', 'content_type':'TEXT/RAW'},
                            {'name': 'tease',},)}
}