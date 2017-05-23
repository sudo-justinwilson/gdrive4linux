import os
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
    def __init__(self, client_path=None, scope=None, pickle_path=None):
        if not client_path:
            raise Exception('A path to a json file containing the client_id and client_secret needs to be provided')
        if not scope:
            raise Exception('A scope needs to be provided')
        if not pickle_path:
            raise Exception('A pickle_path needs to be provided')
        self.client_path = client_path
        self.scope = scope
        self.pickle_path = pickle_path
        self.webserver = WebServer()
        self.flow = client.flow_from_clientsecrets(self.client_path, scope = self.scope, redirect_uri = self.webserver.redirect_uri)
        self.auth_uri = self.flow.step1_get_authorize_url()
        self.credentials = None
        if os.path.exists(self.pickle_path):
            self.credentials = pickle.load( open(self.pickle_path, 'rb') ).credentials
            self.pickled = True
        else:
            self.pickled = False

    def create_service(self, auth_code=None, url=None, http_auth=None):
        """
        Method that returns authenticated service object.
        """
        if self.pickled is False:
            if not url:
                url = self.auth_uri
            if not auth_code:
                auth_code = self.get_auth_code(url)
            self.credentials = self.flow.step2_exchange(auth_code)
            self.pickled = True
            pickle.dump( self, open(self.pickle_path, 'wb') )
        if not http_auth:
            http_auth = self.credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v2', http=http_auth)
        return drive_service

    def get_auth_code(self, url):
        webbrowser.open_new(url)
        val = None
        print('the val is: ', val)
        val = self.webserver.catch_response()
        print('the val after calling webserver.catch_response() is: ', val)
        return val

if __name__ == '__main__':
    #instance = auth_with_apiclient(client_path='/home/justin/tmp/auth_with_apiclient_object', scope='https://www.googleapis.com/auth/drive', pickle_path='/home/justin/tmp/token_from_my_service_object')
    client_secrets = "/home/justin/Downloads/gdrive_client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json"
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    print('the pickle flag before calling create_service is set to: ', instance.pickled)
    service = instance.create_service()
    print('the pickle flag after create_service, is set to: ', instance.pickled)
    print(dir(service))
    print(type(service))
    print("Here is the unpickled credentials introspection: ", dir(instance.credentials))
    print(type(instance.credentials))
    print(instance.credentials.to_json())
    if instance.credentials.access_token_expired:
        print('the access_token_expired is True')
    else:
        print('access_token_expired == FALSE!')
    #unpickled_object = pickle.load( open(instance.pickle_path, 'rb') )
    #print( type(unpickled_object) )
    #print( dir(unpickled_object) )
    #print(' the type of the thing is: ', type(unpickled_object.credentials))
    #print(' the dir of the thing is: ', dir(unpickled_object.credentials))
    # 2017/05/23: I was curious to see if it worked without the __{g,s}etstate__ methods, and if they had any effect, in this version I removed them, and they seem to work..
    # 2017/05/23: Yeah, so it turns out that I don't need the __{g,s}etstate__ methods to pickle the instance, with populated credentials..
