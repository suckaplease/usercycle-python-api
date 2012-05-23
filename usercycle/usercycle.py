import datetime
import requests
from pprint import pprint

DEBUG = True

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
base_url = protocol + '://' + api_host + '/api/v' + version

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
    def __init__(self, code, text):
        errors = {
            400:ResourceInvalid,
            401:Unauthorized,
            403:Forbidden,
            404:ResourceNotFound,
            405:MethodNotAllowed,
            406:NotAcceptable,
            500:ServerError,
        }
        if DEBUG: print code, text
        raise errors.get(int(code), UnknownError)(text)

class ResourceInvalid(Exception): pass
class Unauthorized(Exception): pass
class Forbidden(Exception): pass
class ResourceNotFound(Exception): pass
class MethodNotAllowed(Exception): pass
class NotAcceptable(Exception): pass
class ServerError(Exception): pass
class UnknownError(Exception): pass

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
               occurred_at=None,
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
        action = "signed_up"
        
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
                
        return self.post_request("/events.json",identity, action, occurred_at=occurred_at, properties=kwargs)
    
    def activated(self, identity, occurred_at=None, **kwargs):
        action = 'activated'        
        return self.post_request("/events.json",identity, action, occurred_at=occurred_at, properties=kwargs)
    
    def came_back(self, identity, occurred_at=None, **kwargs):
        action= 'came_back'
        return self.post_request("/events.json", identity, action, occurred_at=occurred_at, properties=kwargs)
   
    # FIXME
    def purchased(self, identity, revenue_amount=None, occurred_at=None, **kwargs):
        action = 'purchased'        
        if revenue_amount: kwargs['revenue_amount'] = revenue_amount
        
        return self.post_request("/events.json", identity, action, occurred_at=occurred_at, properties=kwargs)

    def referred(self, identity, occurred_at=None, **kwargs):
        action = 'referred'
        return self.post_request("/events.json", identity, action, occurred_at=occurred_at, properties=kwargs)
    
    def canceled(self, identity, reason=None, occurred_at=None, **kwargs):
        action = 'canceled'
        if reason: kwargs['reason'] = reason
        return self.post_request("/events.json", identity, action, occurred_at=occurred_at, properties=kwargs)

    def post_request(self, path, identity, action_name, occurred_at=None, properties=None):
        if self.access_token:
            post_args = {
                "identity":identity,
                "action_name":action_name,
            }
            for k,v in properties.iteritems():
                post_args[k] = v
            if occurred_at:
                # VALID FORMAT AS OF 4/18/12
                fmt = '%Y-%m-%d %H:%M:%S UTC'
                assert datetime.datetime.strptime(occurred_at, fmt)
                post_args['occurred_at'] = occurred_at
            
            url = protocol + "://" + api_host + "/api/v%s" % version + "%s" % path
            if DEBUG:
                print url
                pprint( post_args )
            headers = {
                "X-Usercycle-API-Key":self.access_token,
                "Accept":"application/json",
                }            
            try:
                r = requests.post(url, data=post_args, headers=headers)
                if DEBUG: 
                    pprint(r.headers)
                    pprint(post_args)
                r.raise_for_status()
                response = _parse_json(r.text)
                return response
            except requests.HTTPError, e:
                if DEBUG: 
                    print response 
                    pprint(r.headers)
                #raise UsercycleError(e)
                raise UsercycleError(r.status_code, r.text)
        else:
            raise ValueError("missing access_token")

    def get_events(self, count=100, page=1, uuid=None, **kwargs):
        '''
        uuid (optional) is the unique event identifier returned after an event is posted
        optional kwargs: identity, action, since
        '''
        params = {'count': count, 'page': page}
        for k,v in kwargs.iteritems():
            params[k] = v
        if uuid:
            return self.get_request('/events/%s.json' % uuid, params=params)
        else:
            return self.get_request('/events.json', params=params)

    def get_people(self, count=100, page=1):
        params = {'count': count, 'page': page}
        return self.get_request('/people.json', params=params)

    # TODO: get cohorts

    def get_request(self, path, params={}, properties=None):
        if self.access_token:
            get_args = params
            get_args['api_key'] = self.access_token
            if properties: 
                get_args['properties'] = properties
            
            #url = protocol + "://" + api_host + "/api/v%s" % version + "%s" % path
            url = base_url + path
            if DEBUG: print url
            headers = {
                "X-Usercycle-API-Key":self.access_token,
                "Accept":"application/json",
                }            
            try:
                r = requests.get(url, params=get_args, headers=headers)
                r.raise_for_status()
                response = _parse_json(r.text)
                return response
            except requests.HTTPError, e:
                if DEBUG: print r, e
                #raise UsercycleError(e)
                raise UsercycleError(r.status_code, r.text)
        else:
            raise ValueError("missing access_token")
