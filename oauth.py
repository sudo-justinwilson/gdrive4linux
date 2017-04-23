import http.server
import socketserver
import requests
import json
import time
import random
import os
import string
import webbrowser
import urllib

# other files in ./:
from oauthbase import OauthBase
from clientcredentials import ClientCredentials
from webserver import WebServer

###     START NEW           ###
class Oauth(OauthBase):
    """
    """
    def __init__(self, token_path=None, client_creds=None, scope=None, **kwargs):
        """
        Initialize Oauth object.
        The client (the app that is requesting access to the user (user=resource owner) resources on behalf of user.

        Optional args:
		token_path	-	the path to where the user's access/refresh tokens will be stored.
        - client_creds  -   this is a convenience that allows the caller to pass a dict that contains the client_id and client_secret as, or as a string that is the path to a file that contains the client credentials in json format.
        EG:
            # pass a dict:
            oauth = Oauth('/home/user/.user.creds', client_creds=creds_dict)
            or
            # pass a str that's a path to a json file:
            oauth = Oauth('/home/user/.user.creds', client_creds='/home/Downloads/creds_dict')

        The client credentials will then be handled by this module.
        

        TODO:
        - chmod 600 token_path
        - define ONE oauth2.0 server in __init__(), because as far as I can tell, there is only one oauth server...
        """
        if token_path:
            self.token_path = token_path
        else: 
            self.token_path = os.path.expanduser('~/.contacts_address_resolution')
        self.webserver = WebServer()
        # Test if a path to the json file that contains the client_id and secret has been passed to init, else, the client params should be passed as key:value pairs to kwargs, which will then be returned as a dict. kwargs.keys() will be tested to ensure that the right values have been passed or an exception will be raised.
        if client_creds:
            if isinstance(client_creds, dict):
                self.client_creds = ClientCredentials(scope=scope, **client_creds)
            if isinstance(client_creds, str):
                self.client_creds = ClientCredentials(scope=scope, client_file=client_creds)
        elif 'client_id' in kwargs and 'client_secret' in kwargs:
            self.client_creds = ClientCredentials(scope=scope, **kwargs)
        else:
            raise Exception("The client id and secret need to be provided.")
        
    def auth_in_browser(self, params=None, server=None, send_nonce=True):
        """
        Open a browser so the user can grant permission to the protected resources.
        This starts the installed app oauth2.0 flow.

        OPTIONAL ARGS:
        - params:       this is a dict that will be appended to the url as query srings.
        - server:       this is the oauth2.0 server that the request will be made to.
        - send_nonce:   whether to send a nonce with the query or not. This mechanism helps security.
        The server is Google by default for now, but the idea is that we will be able to use any oauth2.0 provider.
        """
        if server:
            target = server
        else:
            target = 'https://accounts.google.com/o/oauth2/v2/auth'
        if send_nonce:
            # send a nonce with the request (state):
            if not isinstance(params, dict):
                params = {
                'redirect_uri': self.webserver.redirect_uri, 
                'scope': self.client_creds.scope, 
                'client_id': self.client_creds.client_id,
                'state' : self.webserver.nonce,
                'response_type': 'code'}
            self.webserver._nonce_sent = True
        else:
            # don't send a nonce:
            if not isinstance(params, dict):
                params = {
                'redirect_uri': self.webserver.redirect_uri, 
                'scope': self.client_creds.scope, 
                'client_id': self.client_creds.client_id,
                'response_type': 'code'}

        url = target + '?' + urllib.parse.urlencode(params)
        webbrowser.open_new_tab(url)

    def swap_code(self, code, params=None, token_path=None, oauth_server=None):
        """
        This method swaps the auth code, from self.webserver.serve_html(), for the oauth tokens. 
        It should store the oauth tokens, from the HTTP response, in a file at token_path, and get_token() should return a token when when the user wants user calls it.
        This method should not be called by the user as it is called by other methods (serve_html) and should be non-public.
        Eventually, the token_path param should be removed as well as it is defined with __init__, and the user should only have to call self.authorize(), but until I've got this class where I want it, token_path will remain for testing...

        - TARGET URL 
            (https://accounts.google.com/o/oauth2/v2/auth) + '?'
        REQUIRED HTTP PARAMETERS:
        - SCOPE
            https://www.googleapis.com/auth/drive
        - REDIRECT URI
            'http://127.0.0.1:' + self._port
        - RESPONSE_TYPE
            'code'
        - CLIENT_ID
            '696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com
        *** PARAMS ARE DELIMITED WITH '&'   ***
        """
        if not oauth_server:
            oauth_server = 'https://accounts.google.com/o/oauth2/token'
        if not isinstance(params, dict):
            params = {
            'client_id' : self.client_creds.client_id,
            'client_secret' : self.client_creds.client_secret,
            'redirect_uri' : self.webserver.redirect_uri,
            'grant_type' : 'authorization_code'
            }

        params['code'] = code
        try:
            oauth_request = requests.post(oauth_server, data=params)
            #oauth_request = requests.post('https://accounts.google.com/o/oauth2/token', data=params)
            oauth_response = oauth_request.json()       # This stores the json response as a json string.
        except ValueError as e:
            print("THE RESPONSE DID NOT CONTAIN ANY VALID JSON: ", e)
            #return 'NO JSON IN RESPONSE'
            return 
        oauth_response['time_received'] = int(time.time())
        #print("Here is the full credentials dict, that should have a time_received key: ", oauth_response)
        # if token_path was specified, store user credentials there as a json file, else use value from __init__:
        if token_path:
            path = token_path
        else:
            path = self.token_path
        json.dump(oauth_response, open(path, 'w'))


    def authorize(self, auth_uri=None):
        """
        This function just calls the methods required to initially grant permission for Google.
        """
        print("Please grant application permission in browser...")
        self.auth_in_browser(server=auth_uri)
        code = self.webserver.serve_html()
        #self.swap_code(code)
        return code

    def grant_permission(self):
        """
        This is a convenience that calls authorize and swap_code so that permission is granted and the file at self.token_path is populated with valid access and refresh tokens.
        """
        authorization_code = self.authorize()
        self.swap_code(authorization_code)

    def get_token(self, token_path=None):
        """
        This method returns either the existing access_token (if it hasn't expired), or if it has, it will refresh the token, either way, it returns a valid access token.
        """
        # check that a file exists at self.token_path, else raise exception:
        if token_path is None:
            token_path = self.token_path
            if not os.path.exists(token_path):
                #self.authorize()       # I decided that this could lead to undefined behaviour..
                raise Exception("This app has not yet been granted permission. \
                Please call self.authorize() to grant permission to this app.")
        creds = json.load(open(token_path))
        # check if the tokens are over 3600 seconds old:
        self.token_age = age = int(time.time()) - creds['time_received']
        if age > 3590:
            print(int(time.time()), '  ', creds['time_received'], '  should == ', age)
            print("Refreshing token...")
            # store existing refresh_token as when we refresh a token, the response doesn't have a refresh token:
            temp_refresh_token = creds['refresh_token']
            # refresh_token() returns a dict:
            new_token = self.refresh_token()        
            # put back refresh_token:
            new_token['refresh_token'] = temp_refresh_token
            # new_token.keys() should == access_token, token_type, expires_in, refresh_token: plus 'time_received' which I defined:
            if len(new_token.keys()) == 5:      # for testing
                # update creds_file with new access_token:
                json.dump(new_token, open(token_path, 'w'))         #json.dump(obj, fp)
            else:
                raise Exception("The refresh token should have 5 keys, but there isn't...")
            # return refreshed token:
            return new_token['access_token']
        # existing access token is still valid (younger than 3600s), so return it:
        else:
            return creds['access_token']

    def refresh_token(self, token_path=None, oauth_server=None):
        """
        This method returns the refresh_token as a dict. It DOES NOT UPDATE THE CREDS FILE! That should be handled by the caller.
        This method return a refresh_token (which should be a json response) as a dict. IT DOES NOT UPDATE THE CREDENTIALS_FILE! <- this should be handled by the caller.
        So the items required to get a refresh token are:
        - client_id             CONSTANT
        - client_secret         CONSTANT
        - refresh_token         VARIABLE?
        - grant_type            CONSTANT
        - URL                   CONSTANT
        - And it uses the POST method.
        """
        if not oauth_server:
            # this is the same server as swap_code.. TODO: define self.oauth_server
            oauth_server= 'https://accounts.google.com/o/oauth2/token'
        # check that there is a tokens file, else raise exception:
        if token_path is None:
            token_path = self.token_path
            if not os.path.exists(self.token_path):
                #self.authorize()       # I decided that this could lead to undefined behaviour..
                raise Exception("This app has not yet been granted permission. \
                Please call self.authorize() needs to grant permission to this app and to get an authorization code.")
        params = {
            'client_id' : self.client_creds.client_id,
            'client_secret' : self.client_creds.client_secret,
            'grant_type' : 'refresh_token',
            'refresh_token' : json.load(open(token_path))['refresh_token']
            }
    
        try:
            oauth_refresh = requests.post(oauth_server, data=params)
        except ValueError as e:
            Exception("REFRESH HTTP RESPONSE DID NOT CONTAIN VALID JSON: ", e)
        answer = oauth_refresh.json()
        # testing
        answer['time_received'] = int(time.time())
        return answer

    def is_valid(self, token, print_response=False):
        print("Checking if token is valid...")
        target = 'https://www.googleapis.com/oauth2/v1/tokeninfo'
        r = requests.get(target, params={'access_token':token})
        if print_response:
            print("Here is the response:")
            print(r.text)
        if r.status_code == 200:
            return True
        else:
            return False

if __name__ == '__main__':
    #client_id_path = '/home/justin/Downloads/client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json'   
    client_id_path = '/home/justin/Downloads/gdrive_client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json'
    scope='https://www.googleapis.com/auth/drive'
    oauth = Oauth(token_path='/home/justin/tmp/contacts-credentials.json', client_creds=client_id_path, scope=scope)
    ## initial authorization code below:
    # UNCOMMENT FOR INITIAL AUTH >auth_code = oauth.authorize()
    # UNCOMMENT FOR INITIAL AUTH >oauth.swap_code(auth_code)
    token = oauth.get_token()
    if oauth.is_valid(token, print_response=True):
        print('the token is:\t', token)
        #print("the token is valid")
    else:
        print("the token is INVALID")
    #target = 'https://www.googleapis.com/drive/v2/files'
    #r = requests.get(target, params={'access_token':token})
    #print(r.text)
    # the above code has been tested and is working correctly!
    # TODO: define self.is_valid(token) method to test if the token is valid
    # TODO: clean up the comments
    # make it so that the app credentials are parameters, and be used by anyone's app
