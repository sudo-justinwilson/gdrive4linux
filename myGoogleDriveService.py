import webbrowser
import httplib2
from apiclient import OAuth2WebServerFlow
from webserver import WebServer
from clientcredentials import ClientCredentials
from apiclient.http import MediaIoBaseDownload
from oauth2client.file import Storage

##      MY DRIVE APICLIENT      ##

scope = 'https://www.googleapis.com/auth/drive'
webserver = WebServer()
path_to_client_credentials = '/home/justin/Downloads/gdrive_client_secret_696694623422-rte0oijs03i83paq0efj7m46nvqphuuj.apps.googleusercontent.com.json'
client_creds = ClientCredentials(client_file=path_to_client_credentials, scope=scope)

flow = OAuth2WebServerFlow(client_id=client_creds.client_id,
                           client_secret=client_creds.client_secret,
                           scope=scope,
                           redirect_uri=webserver.redirect_uri)

auth_uri = flow.step1_get_authorize_url()       # this returns the URI that is meant to be opened up in the browser, so the user can grant permission to the app

# open up a new tab in the user's default webbrowser:
webbrowser.open_new_tab(auth_uri)
# start the webserver to intercept the authorization code:
auth_code = webserver.serve_html()

# Now that we have the auth_code, we can swap it for credentials:
credentials = flow.step2_exchange(code)

# Now we can call the 'authorize' method, so that the credential headers are applied to all requests made by an httplib2.Http instance:
http = httplib2.Http()
http = credentials.authorize(http)

# Now we can build an API service object:
service = build('drive', 'v3', http=http)

# A "Storage" object stores Credentials objects, so we can get and set them.
# There are also methods for storing credentials for different users, which would allow users to have multiple google drive accounts - for instance:
storage = Storage('.credentials')
storage.put(credentials)
# To get credentials:
credentials = storage.get()


## USING THE GOOGLE DRIVE SERVICE OBJECT        ###
# now that we have sorted the above logistics out, we can make google drive api calls, using the apiclient:


## Searching for files:
page_token = None
while True:
    response = drive_service.files().list(q="mimeType='image/jpeg'",
                                         spaces='drive',
                                         fields='nextPageToken, files(id, name)',
                                         pageToken=page_token).execute()
    for file in response.get('files', []):
        # Process change
        print 'Found file: %s (%s)' % (file.get('name'), file.get('id'))
    page_token = response.get('nextPageToken', None)
    if page_token is None:
        break;

# To download a file, we need a file_id, this can be obtained by searching for files, without any filters:


file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
request = drive_service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
##      ##  MediaIoBaseDownload is imported from apiclient.htp. use help() for more details..
done = False
while done is False:
    status, done = downloader.next_chunk()
    print "Download %d%%." % int(status.progress() * 100)




##from oauth2client.client import OAuth2WebServerFlow
##...
##flow = OAuth2WebServerFlow(client_id='your_client_id',
##                           client_secret='your_client_secret',
##                           scope='https://www.googleapis.com/auth/calendar',
##                           redirect_uri='http://example.com/auth_return')
