# These are all the settings that are used to configure supertagging

CALAUS_DEBUG = True
CALAIS_API_KEY = 'your key here'
CALAIS_USER_DIRECTIVES = {}
CALAIS_PROCESING_DIRECTIVES = {}
CALAIS_EXTERNAL_METADATA = {}
CALAIS_PROCESS_RELATIONS = True
CALAIS_PROCESS_TOPICS = True
CALAIS_MODULES = {
    'app.model': {'fields':({'name': 'content', 'content_type':'TEXT/RAW'},
                            {'name': 'tease',},)}
}