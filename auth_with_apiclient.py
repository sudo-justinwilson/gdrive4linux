import webbrowser
import httplib2
from webserver_new import WebServer
from apiclient.discovery import build
from oauth2client import client

class auth_with_apiclient.py:
    """
    My implementation of using the google-api-client module to create an authorized service object, which can make oauth2.0 authorized Google API calls.
    """
    def __init__(self, client_path=None, scope=None):
        if client_path:
            self.client_path = client_path
        else:
            raise Exception('A path to a json file containing the client_id and client_secret needs to be provided')
        if scope:
            self.scope = scope
        else:
            raise Exception('A scope needs to be provided')
        self.webserver = WebServer()
        self.flow = client.flow_from_clientsecrets(self.client_path, scope = self.scope, redirect_uri = self.webserver.redirect_uri)
        self.auth_uri = self.flow.step1_get_authorize_url()
        self.auth_code = self.get_auth_code(self.auth_uri)

    def get_auth_code(url):
        webbrowser.open_new(url)
        val = None
        print('the val is: ', val)
        val = webserver.catch_response()
        print('the val after calling webserver.catch_response() is: ', val)
        return val
    
    credentials = flow.step2_exchange(code)
    
    http_auth = credentials.authorize(httplib2.Http())
    # this is the service to make the API calls:
    drive_service = build('drive', 'v2', http=http_auth)

    # we need to store.credentials.to_json() in a file.
    token_path = $PATH
    import json
    json.dump(open(token_path, 'w'), credentials.to_json())

