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
        if os.path.exists(pickle_path):
            self.pickled = True
        else:
            self.pickled = False

    ### start pickle
    def __getstate__(self):
        """
        Copy the instance's state for pickling.
        Method called by pickle module.
        """
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        """
        This is a method to restore the state of this instance.
        Called by pickle module.
        """
        self.__dict__.update(state)

    ### end pickle

    def create_service(self, auth_code=None, url=None, http_auth=None):
        """
        Method that returns authenticated service object.
        """
        if not url:
            url = self.auth_uri
        if not auth_code:
            auth_code = self.get_auth_code(url)
        #if not os.path.exists(self.pickle_path):
        if self.pickled is False:
            self.credentials = self.flow.step2_exchange(auth_code)
            self.pickled = True
            pickle.dump( self, open(self.pickle_path, 'wb') )
        else:
            instance = pickle.load( open(self.pickle_path, 'rb') )
            self.credentials = instance.credentials
        if not http_auth:
            http_auth = self.credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v2', http=http_auth)
        return drive_service

    def get_auth_code(self, url):
        webbrowser.open_new(url)
        val = None
        print('the val is: ', val)
        #val = webserver.catch_response()
        val = self.webserver.catch_response()
        print('the val after calling webserver.catch_response() is: ', val)
        return val

if __name__ == '__main__':
    #instance = auth_with_apiclient(client_path='/home/justin/tmp/auth_with_apiclient_object', scope='https://www.googleapis.com/auth/drive', pickle_path='/home/justin/tmp/token_from_my_service_object')
    client_secrets = "/home/justin/Downloads/gdrive_client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json"
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    print('the pickle flag is set to: ', instance.pickled)
    service = instance.create_service()
    print('the pickle flag after create_service, is set to: ', instance.pickled)
    print(dir(service))
    print(type(service))
    #unpickled_object = pickle.load( open(instance.pickle_path, 'rb') )
    #print( type(unpickled_object) )
    #print( dir(unpickled_object) )
    #print(' the type of the thing is: ', type(unpickled_object.credentials))
    #print(' the dir of the thing is: ', dir(unpickled_object.credentials))
    # 2017/05/22: I have managed to pickle and restore an instance, but now I need to add the logic so I know if I've already authorized, and don't have to open up the webbrowser again because we already have the tokens
