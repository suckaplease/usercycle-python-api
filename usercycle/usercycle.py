
import urllib
import urllib2
import httplib

# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)

version = "1"
protocol = "http"
api_host = "api.usercycle.com"

USERCYCLE_ACCESS_TOKEN = "REPLACE_WITH_YOUR_TOKEN"

class UsercycleError(Exception):
    """
    200: Success (upon a successful GET, PUT, or DELETE request)
    201: Created (upon a successful POST request)
    400: Resource Invalid (improperly-formatted request)
    401: Unauthorized (incorrect or missing authentication credentials)
    404: Resource Not Found (requesting a non-existent person or other resource)
    405: Method Not Allowed (e.g., trying to POST to a URL that responds only to GET)
    406: Not Acceptable (server can## satisfy the Accept header specified by the client)
    500: Server Error
    """
    def __init__(self, data):
        errors = {
            400:Invalid,
            401:Unauthorized,
            403:Forbidden,
            404:ResourceNotFount,
            405:MethodNotAllowed,
            406:NotAcceptable,
            500:ServerError,
        }
        raise errors.get(data.code, UnknownError)(data)

class ResourceInvalid(Exception): pass
class Unauthorized(Exception): pass
class ResourceNotFound(Exception): pass
class MethodNotAllowed(Exception): pass
class NotAcceptable(Exception): pass
class ServerError(Exception): pass
class Forbidden(Exception): pass

class UsercycleAPI(object):
    """
    Client library for the USERCycle API
    """
    def __init__(self, access_token=None):
        if access_token:
            self.access_token = access_token
        else:
            self.access_token = USERCYCLE_ACCESS_TOKEN
    
    def signup(self,
               identity,
               first_name=None,
               last_name=None,
               title=None,
               company=None,
               email=None,
               phone=None,
               twitter=None,
               facebook=None,
               plan_name=None,
               referrer=None,
               campaign_source=None,
               search_terms=None,
               **kwargs):
        kwargs['action'] = "SIGNED_UP"
        kwargs['identity'] = identity
        
        if first_name: kwargs['firstname'] = first_name
        if last_name: kwargs['lastname'] = last_name
        if title: kwargs['title'] = title
        if company: kwargs['company'] = company
        if email: kwargs['email'] = email
        if phone: kwargs['phone'] = phone
        if twitter: kwargs['twitter'] = twitter
        if facebook: kwargs['facebook'] = facebook
        if plan_name: kwargs['plan_name'] = plan_name
        if referrer: kwargs['referrer'] = referrer
        if campaign_source: kwargs['campaign_source'] = campaign_source
        if search_terms: kwargs['search_terms'] = search_terms
                
        self.request("/events.json",post_args=kwargs)
    
    def activated(self, identity, **kwargs):
        kwargs['action'] = 'ACTIVATED'
        kwargs['identity'] = identity
        self.request("/events.json",post_args=kwargs)
    
    def came_back(self, identity, **kwargs):
        kwargs['action'] = 'CAME_BACK'
        kwargs['identity'] = identity
        
        self.request("/events.json", post_args=kwargs)
    
    def purchased(self, identity, revenue_amount=None, **kwargs):
        kwargs['action'] = 'PURCHASED'
        kwargs['identity'] = identity
        
        if revenue_amount: kwargs['revenue_amount'] = revenue_amount
        
        self.request("/events.json", post_args=kwargs)

    def referred(self, identity, **kwargs):
        kwargs['action'] = 'referred'
        kwargs['identity'] = identity
        self.request("/events.json", post_args=kwargs)
    
    def canceled(self, identity, reason=None, **kwargs):
        kwargs['action'] = 'CANCELED'
        kwargs['identity'] = identity
        if reason: kwargs['reason'] = reason
        self.request("/events.json", post_args=kwargs)


    def request(self, path, args=None, post_args=None):
        if not args: args = {}
        #if self.access_token:
        #    if post_args is not None:
        #        post_args["access_token"] = self.access_token
        #    else:
        #        args["access_token"] = self.access_token
                
        post_data = None if post_args is None else urllib.urlencode(post_args)
        url = protocol + "://" + api_host + "/api/v%s" % version + "%s" % path
        if args:
            args = args.encode('utf-8')
            url += "?" + urllib.urlencode(args)
        
        #print "URL:  %s" % url
        request = urllib2.Request(url,post_data)
        request.add_header("X-Usercycle-API-Key",self.access_token)
        request.add_header("Accept","application/json")

        file = urllib2.urlopen(request)
        
        try:
            response = _parse_json(file.read())
        except urllib2.HTTPError, e:
            raise UsercycleError(e)
        finally:
            file.close()
        return response
