import webbrowser
import os
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
    class MyPickler:
        def __init__(self, path, item=None):
            """
            This accepts an item, creates an instance attribute from it, and stores it in the file, pickled.
            """
            self.path = path
            self.item = item
            if os.path.exists(self.path):
                self.anything_pickled = True
            else:
                self.anything_pickled = False

        def store(self, path=None):
            """
            Pickle this instance to a file at self.path.
            """
            if not path:
                path = self.path
            if not self.path:
                raise Exception('self.item is None! Nothing to pickle.')
            pickle.dump(self, open(path, 'wb') )
            self.anything_pickled = True

        def get(self, path=None):
            if not self.anything_pickled:
                raise Exception('Nothing has been pickled yet!')
            if not path:
                path = self.path
            item = pickle.load( open(path, 'rb') )
            return item



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
        # The credentials below will be assigned to a "MyPickler" instance, with the credentials:
        self.credentials = self.MyPickler(self.token_path)

    def create_service(self, auth_code=None, url=None, http_auth=None):
        """
        Method that returns authenticated service object.
        """
        if not url:
            url = self.auth_uri
        if not auth_code:
            auth_code = self.get_auth_code(url)
        if self.credentials.anything_pickled:
            credentials = self.credentials.get().item
        else:
            self.credentials.item = self.flow.step2_exchange(auth_code) 
            self.credentials.store()
            credentials = self.credentials.item
        if not http_auth:
            http_auth = credentials.authorize(httplib2.Http())

        # this is the service to make the API calls:
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
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, token_path='/home/justin/tmp/token_from_mypickler_object-2017-05-21')
    service = instance.create_service()
    print(dir(service))
    print(type(service))
    print(type(instance.credentials))
    print(dir(instance.credentials))

