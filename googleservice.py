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

    TODO:
        - Refactor so this program can accept command-line arguments
    """

    def __init__(self, client_path=None, scope=None, pickle_path=None):
        """
        Create an auth_with_apiclient instance.

        Args:
        - client_path:      This is the path to the app credentials from the Google developer's console.
        - scope:            This specifies the amount of access (or permissions) requested from Google.
        - pickle_path:      Specifies the path where the access and refresh tokens are stored as a pickled file.
        """
        if not client_path:
            raise Exception('A path to a json file containing the client_id and client_secret needs to be provided')
        # Mandatory arg:
        if not scope:
            raise Exception('A scope needs to be provided')
        # Mandatory arg:
        if not pickle_path:
            raise Exception('A pickle_path needs to be provided')
        self.client_path = client_path
        self.scope = scope
        self.pickle_path = pickle_path
        self.webserver = WebServer()
        # Defines the type of oauth2.0 flow that we will use:
        self.flow = client.flow_from_clientsecrets(self.client_path, scope = self.scope, redirect_uri = self.webserver.redirect_uri)
        # Returns the url to request an authorization code:
        self.auth_uri = self.flow.step1_get_authorize_url()
        self.credentials = None
        # This tests if a file exists at pickle_path, and if there is, it indicates that we have already got an access and refresh token - so we don't need to go through the initial authorization code flow:
        if os.path.exists(self.pickle_path):
            self.credentials = pickle.load( open(self.pickle_path, 'rb') ).credentials
            self.pickled = True
        else:
            self.pickled = False

    def create_service(self, auth_code=None, url=None, http_auth=None, version='v2'):
        """
        Method that returns authenticated service object.

        TODO:
            I need to include an optional arg: version=v2 - so we can optionally return a v3 instance.
        """
        if self.pickled is False:
            if not url:
                url = self.auth_uri
            if not auth_code: 
                auth_code = self.get_auth_code(url)
            self.credentials = self.flow.step2_exchange(auth_code)
            self.pickled = True
            try:
                pickle.dump( self, open(self.pickle_path, 'wb') )
            except FileNotFoundError as e:
                print("The pickle path does not exist:\t", e.filename)
                return -1
        if not http_auth:
            http_auth = self.credentials.authorize(httplib2.Http())
        drive_service = build('drive', version, http=http_auth)
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
    # The client_secrets file seems to have disappeared:
    #client_secrets = "/home/justin/Downloads/gdrive4linux-client_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    client_secrets = "/home/justin/Downloads/gdrive4linux_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    print('Here is what the client_secrets is:\t', client_secrets)
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    # I had to go through the initial oauth2.0 flow again, because the pickled object expects a module named 'pickled_service2_without_pickle_state_methods' - which I renamed to googleservice.py:
    #instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/Dropbox/Coding/Projects/gdrive4linux/cik.smarthomes.pickled_credentials_20170929')
    print('the pickle flag before calling create_service is set to: ', instance.pickled)
    service = instance.create_service()
    print('the pickle flag after create_service, is set to: ', instance.pickled)
    #print(dir(service))
    #print(type(service))
    print('Here is when I call dir(service.files): ', dir(service.files))
    #print("Here is the unpickled credentials introspection: ", dir(instance.credentials))
    #print(type(instance.credentials))
    #print(instance.credentials.to_json())
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
