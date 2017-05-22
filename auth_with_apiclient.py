import webbrowser
import httplib2
import pickle
from webserver import WebServer
from apiclient.discovery import build
from oauth2client import client, file

class auth_with_apiclient:
    """
    My implementation of using the google-api-client module to create an authorized service object, which can make oauth2.0 authorized Google API calls.
    ** It *should* return an google OAuth2Credentials object.   **
    """
    def __init__(self, client_path=None, scope=None, token_path=None):
        if not client_path:
            raise Exception('A path to a json file containing the client_id and client_secret needs to be provided')
        if not scope:
            raise Exception('A scope needs to be provided')
        if not token_path:
            raise Exception('A token_path needs to be provided')
        self.client_path = client_path
        self.scope = scope
        self.token_path = token_path
        self.webserver = WebServer()
        self.flow = client.flow_from_clientsecrets(self.client_path, scope = self.scope, redirect_uri = self.webserver.redirect_uri)
        self.auth_uri = self.flow.step1_get_authorize_url()
        # I removed self.auth_code below, because it calls self.get_auth_code(), which opens up a webbrowser on __init__:
        #self.auth_code = self.get_auth_code(self.auth_uri)

    def create_service(self, auth_code=None, url=None, http_auth=None):
        """
        Method that returns authenticated service object.
        """
        if not url:
            url = self.auth_uri
        if not auth_code:
            auth_code = self.get_auth_code(url)
            #auth_code = self.auth_code
            #raise Exception('no auth_code was passed to create_service')
        #if not http_auth:
        #    http_auth = credentials.authorize(httplib2.Http())
        #    http_auth = self.auth_uri(url)
        credentials = self.flow.step2_exchange(auth_code)
        #token_path = self.token_path
        pickle.dump( credentials, open(self.token_path, 'wb') )
        if not http_auth:
            http_auth = credentials.authorize(httplib2.Http())

        # this is the service to make the API calls:
        drive_service = build('drive', 'v2', http=http_auth)
        # I tried pickling the above credentials object, but when I unpickle it, it returns an auth_with_apiclient (self) object?? So I'm trying to pickle the below service object. What I'm trying to do is essentially store the tokens, but I'm having difficulty using pickle to store them. Do I have to create a seperate user_tokens object, and pickle them??
        pickle.dump( drive_service, open(self.token_path, 'wb') )
        return drive_service

    def get_auth_code(self, url):
        webbrowser.open_new(url)
        val = None
        print('the val is: ', val)
        #val = webserver.catch_response()
        val = self.webserver.catch_response()
        print('the val after calling webserver.catch_response() is: ', val)
        return val

    #def unpickle_credentials(self, path=None):
    #    """
    #    This method unpickles the credentials object, that was pickled with the "create_service" method, and should return an authenticated OAuth2Credentials object.
    #    """

    #def flow(self, client_path=None, scope=None, redirect_uri=None):
    #    """
    #    This is a method to start the oauth2 flow (so it doesn't start on __init__).
    #    """
    #    if not client_path:
    #        client_path = self.client_path
    #    if not scope:
    #        scope = self.scope
    #    if not redirect_uri:
    #        redirect_uri = self.webserver.redirect_uri

    #    flow = client.flow_from_clientsecrets(client_path, scope = scope, redirect_uri = redirect_uri)
    #    auth_uri = flow.step1_get_authorize_url()
    #    auth_code = self.get_auth_code(auth_uri)
    
    #credentials = self.flow.step2_exchange(code)
    #
    #http_auth = credentials.authorize(httplib2.Http())
    ## this is the service to make the API calls:
    #drive_service = build('drive', 'v2', http=http_auth)

    ## we need to store.credentials.to_json() in a file.
    ##   WHY NOT PICKLE THE CREDENTIALS??
    #token_path = $PATH
    #import json
    #json.dump(open(token_path, 'w'), credentials.to_json())
    ## I think it would be better to use the oauth2client.file.Storage object to store the credentials:
    #token_storage_path = '/home/justin/tmp/.tokens.json'
    #file_Storage_object = file.Storage(token_storage_path)
    ## To store the credentials, we need to acquire a lock:
    #file_Storage_object.acquire_lock()
    ## then write the credentials to disk:
    #file_Storage_object.put(credentials)
    ## release lock:
    #file_Storage_object.release_lock()
    ## After doing some reading, the google docs state that credential objects can be safely pickled and unpickled.. I think that this would be better than using a "Storage" object, as the Storage object stores the tokens in a human readable file, whereas pickle stores the object in a non-human-readable binary file:
    #token_path = self.tokens
    ## or
    #flow = pickle.load( open(self.tokens, 'rb')
    ## you don't even have to store the tokens as a seperate object, but this might be better because if the tokens are class attributes, they will be visible with: self.tokens - for example..
    ## How's about pickling an OAuth2Credentials object, or flow (whatever):
    #import pickle
    #token_path = self.token_path
    #pickle.dump( self, open(token_path, 'wb') )

    # TODO:
    #   - write methods to retrieve credentials from file.
    #   - the docs advise that if the redirect_uri serves html, then as we know, the authorization code is visible in the URL. We can prevent this by intercepting the auth_code, then redirecting the browser to another page..
    # HOW DO WE REDIRECT THE PAGE WITH PYTHON???
    #   - I was thinking how we could hide the client id and secret using pickle??? Maybe we could pickle the ClientCredentials object, then retrieve it by unpickling it??
    #   - I need to rewrite the webserver.auth_code method, so I can just pass a string to look for, instead of hard-coding looking for the keyword "code". This would make the method more general, and I coul possibly use it for intercepting any string from incoming HTTP requests.

if __name__ == '__main__':
    #instance = auth_with_apiclient(client_path='/home/justin/tmp/auth_with_apiclient_object', scope='https://www.googleapis.com/auth/drive', token_path='/home/justin/tmp/token_from_my_service_object')
    client_secrets = "/home/justin/Downloads/gdrive_client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json"
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, token_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    service = instance.create_service()
    print(dir(service))
    print(type(service))