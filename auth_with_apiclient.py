import webbrowser
import httplib2
from webserver_new import WebServer
from apiclient.discovery import build
from oauth2client import client, file

class auth_with_apiclient.py:
    """
    My implementation of using the google-api-client module to create an authorized service object, which can make oauth2.0 authorized Google API calls.
    ** It *should* return an google OAuth2Credentials object.   **
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
    #   WHY NOT PICKLE THE CREDENTIALS??
    token_path = $PATH
    import json
    json.dump(open(token_path, 'w'), credentials.to_json())
    # I think it would be better to use the oauth2client.file.Storage object to store the credentials:
    token_storage_path = '/home/justin/tmp/.tokens.json'
    file_Storage_object = file.Storage(token_storage_path)
    # To store the credentials, we need to acquire a lock:
    file_Storage_object.acquire_lock()
    # then write the credentials to disk:
    file_Storage_object.put(credentials)
    # release lock:
    file_Storage_object.release_lock()
    # After doing some reading, the google docs state that credential objects can be safely pickled and unpickled.. I think that this would be better than using a "Storage" object, as the Storage object stores the tokens in a human readable file, whereas pickle stores the object in a non-human-readable binary file:
    token_path = self.tokens
    # or
    flow = pickle.load( open(self.tokens, 'rb')
    # you don't even have to store the tokens as a seperate object, but this might be better because if the tokens are class attributes, they will be visible with: self.tokens - for example..
    # How's about pickling an OAuth2Credentials object, or flow (whatever):
    import pickle
    token_path = self.token_path
    pickle.dump( self, open(token_path, 'wb') )

    # TODO:
    #   - write methods to retrieve credentials from file.
    #   - the docs advise that if the redirect_uri serves html, then as we know, the authorization code is visible in the URL. We can prevent this by intercepting the auth_code, then redirecting the browser to another page..
    # HOW DO WE REDIRECT THE PAGE WITH PYTHON???
    #   - I was thinking how we could hide the client id and secret using pickle??? Maybe we could pickle the ClientCredentials object, then retrieve it by unpickling it??
