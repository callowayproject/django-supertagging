"""
python-calais v.1.4 -- Python interface to the OpenCalais API
Author: Jordan Dimov (jdimov@mlke.net)
Last-Update: 01/12/2009

1.5 updated by Corey Oordt 8/3/2011
"""

import httplib, urllib, re
import simplejson as json
from StringIO import StringIO

PARAMS_XML = """
<c:params xmlns:c="http://s.opencalais.com/1/pred/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"> <c:processingDirectives %s> </c:processingDirectives> <c:userDirectives %s> </c:userDirectives> <c:externalMetadata %s> </c:externalMetadata> </c:params>
"""

STRIP_RE = re.compile('<script.*?</script>|<noscript.*?</noscript>|<style.*?</style>', re.IGNORECASE)

__version__ = "1.5"

VALID_CONTENT_TYPES = (
    'text/xml', 
    'text/html', 
    'text/raw', 
    'text/htmlraw',
)

VALID_OUTPUT_TYPES = (
    "xml/rdf", 
    "text/simple", 
    "text/microformats", 
    "application/json",
    "text/n3",
)

VALID_BOOLEANS = ('true', 'false', 't', 'f',)

VALID_METADATA_TYPES = (
    "GenericRelations", 
    "SocialTags",
    "GenericRelations,SocialTags",
    "SocialTags,GenericRelations",
)

class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.5) Gecko/2008121623 Ubuntu/8.10 (intrepid)Firefox/3.0.5" # Lie shamelessly to Wikipedia.
urllib._urlopener = AppURLopener()

class Calais():
    """
    Python class that knows how to talk to the OpenCalais API.  Use the analyze() and analyze_url() methods, which return CalaisResponse objects.  
    """
    api_key = None
    processing_directives = {
        "contentType": "TEXT/RAW", 
        "outputFormat": "application/json", 
        "reltagBaseURL": '', 
        "calculateRelevanceScore": True, 
        "enableMetadataType": '', 
        "docRDFaccessible": True, 
    }
    user_directives = {
        "allowDistribution": False, 
        "allowSearch": False, 
        "externalID": '',
        "submitter": "python-calais client v.%s" % __version__,
    }
    external_metadata = {}

    def __init__(self, api_key, submitter=None):
        self.api_key = api_key
        if submitter:
            self.user_directives["submitter"]=submitter
    
    def _validate_directives(self):
        """
        Validate that the directives are valid and have valid values
        """
        if (self.processing_directives['contentType'] and 
            self.processing_directives['contentType'].lower() not in VALID_CONTENT_TYPES):
            raise TypeError("%s is not a valid content type.")
        if (self.processing_directives['outputFormat'] and
            self.processing_directives['outputFormat'].lower() not in VALID_OUTPUT_TYPES):
            raise TypeError("%s is not a valid output type.")
        if (self.processing_directives['enableMetadataType'] and
            self.processing_directives['enableMetadataType'].lower() not in VALID_METADATA_TYPES):
            raise TypeError("%s is not a valid metadata type.")
        
        if (self.processing_directives['calculateRelevanceScore'] and 
            not isinstance(self.processing_directives['calculateRelevanceScore'], bool)):
            if self.processing_directives['calculateRelevanceScore'].lower() not in VALID_BOOLEAN_TYPES:
                raise TypeError("%s is not a valid boolean type.")
        
        if (self.processing_directives['docRDFaccessible'] and 
            not isinstance(self.processing_directives['docRDFaccessible'], bool)):
            if self.processing_directives['docRDFaccessible'].lower() not in VALID_BOOLEAN_TYPES:
                raise TypeError("%s is not a valid boolean type.")
        
        if (self.user_directives['allowDistribution'] and 
            not isinstance(self.user_directives['allowDistribution'], bool)):
            if self.user_directives['allowDistribution'].lower() not in VALID_BOOLEAN_TYPES:
                raise TypeError("%s is not a valid boolean type.")
        
        if (self.user_directives['allowSearch'] and 
            not isinstance(self.user_directives['allowSearch'], bool)):
            if self.user_directives['allowSearch'].lower() not in VALID_BOOLEAN_TYPES:
                raise TypeError("%s is not a valid boolean type.")
    
    def _get_param_headers(self):
        headers = {}
        for key, val in self.processing_directives.items():
            if key == 'contentType':
                headers['Content-Type'] = val
            elif key == 'outputFormat':
                headers['Accept'] = val
            elif val:
                headers[key] = val
        for key, val in self.user_directives.items():
            if val:
                headers[key] = val
        for key, val in self.external_metadata.items():
            if val:
                headers[key] = val
        return headers
    
    def rest_POST(self, content):
        headers = {
            "x-calais-licenseID": self.api_key,
        }
        headers.update(self._get_param_headers())
        conn = httplib.HTTPConnection("api.opencalais.com:80")
        conn.request("POST", "/tag/rs/enrich", content.encode('utf8'), headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data

    def get_random_id(self):
        """
        Creates a random 10-character ID for your submission.  
        """
        import string
        from random import choice
        chars = string.letters + string.digits
        np = ""
        for i in range(10):
            np = np + choice(chars)
        return np

    def get_content_id(self, text):
        """
        Creates a SHA1 hash of the text of your submission.  
        """
        import hashlib
        h = hashlib.sha1()
        h.update(text)
        return h.hexdigest()

    def preprocess_html(self, html):
        html = html.replace('\n', '')
        html = STRIP_RE.sub('', html)
        return html

    def analyze(self, content, content_type="TEXT/RAW", external_id=None):
        if not (content and  len(content.strip())):
            return None
        self.processing_directives["contentType"]=content_type
        if external_id:
            self.user_directives["externalID"] = external_id
        return CalaisResponse(self.rest_POST(content))

    def analyze_url(self, url):
        f = urllib.urlopen(url)
        html = self.preprocess_html(f.read())
        return self.analyze(html, content_type="TEXT/HTML", external_id=url)

    def analyze_file(self, fn):
        import mimetypes
        try:
            filetype = mimetypes.guess_type(fn)[0]
        except:
            raise ValueError("Can not determine file type for '%s'" % fn)
        if filetype == "text/plain":
            content_type="TEXT/RAW"
            f = open(fn)
            content = f.read()
            f.close()
        elif filetype == "text/html":
            content_type = "TEXT/HTML"
            f = open(fn)
            content = self.preprocess_html(f.read())
            f.close()
        else:
            raise ValueError("Only plaintext and HTML files are currently supported.  ")
        return self.analyze(content, content_type=content_type, external_id=fn)

class CalaisResponse():
    """
    Encapsulates a parsed Calais response and provides easy pythonic access to the data.
    """
    raw_response = None
    simplified_response = None
    
    def __init__(self, raw_result):
        try:
            self.raw_response = json.load(StringIO(raw_result))
        except:
            raise ValueError(raw_result)
        self.simplified_response = self._simplify_json(self.raw_response)
        self.__dict__['doc'] = self.raw_response['doc']
        for k,v in self.simplified_response.items():
            self.__dict__[k] = v
    
    def _simplify_json(self, json):
        result = {}
        # First, resolve references
        for element in json.values():
            for k,v in element.items():
                if isinstance(v, unicode) and v.startswith("http://") and json.has_key(v):
                    element[k] = json[v]
        for k, v in json.items():
            if v.has_key("_typeGroup"):
                group = v["_typeGroup"]
                if not result.has_key(group):
                    result[group]=[]
                del v["_typeGroup"]
                v["__reference"] = k
                result[group].append(v)
        return result

    def print_summary(self):
        if not hasattr(self, "doc"):
            return None
        info = self.doc['info']
        print "Calais Request ID: %s" % info['calaisRequestID']
        if info.has_key('externalID'): 
            print "External ID: %s" % info['externalID']
        if info.has_key('docTitle'):
            print "Title: %s " % info['docTitle']
        print "Language: %s" % self.doc['meta']['language']
        print "Extractions: "
        for k,v in self.simplified_response.items():
            print "\t%d %s" % (len(v), k)

    def print_entities(self):
        if not hasattr(self, "entities"):
            return None
        for item in self.entities:
            print "%s: %s (%.2f)" % (item['_type'], item['name'], item['relevance'])

    def print_topics(self):
        if not hasattr(self, "topics"):
            return None
        for topic in self.topics:
            print topic['categoryName']

    def print_relations(self):
        if not hasattr(self, "relations"):
            return None
        for relation in self.relations:
            print relation['_type']
            for k,v in relation.items():
                if not k.startswith("_"):
                    if isinstance(v, unicode):
                        print "\t%s:%s" % (k,v)
                    elif isinstance(v, dict) and v.has_key('name'):
                        print "\t%s:%s" % (k, v['name'])
