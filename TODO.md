#TO-DO list:
    - Clean up unnecessary comments, debugging and code, or alternatively, change all the debugging print statements, so that it uses the debug() method instead.
    - Change the sync_to_local() method, so that it only downloads the file if the local file is older than the remote file (check last modified date).
    - Add an option so that we can copy and paste the URL, and get back the auth code on a headless machine.
    - store the metadata in sqlite3.
    - watch local files for changes (inotify?).


#Daily tasks:
    - the change object does return files that have been added, so now I just have to use the 'largestChangeId' or 'newStartPageToken', so I know where the next change begins...

# How to get auth URL for headless client:
    >>>client_secret = '/home/justinwilson/Dropbox/Coding/Projects/gdrive4linux/new_j.w.winship_gdrive4linux-client_id.json'
    >>> scops = 'https://www.googleapis.com/auth/drive'
    >>> flow = oauth2client.client.flow_from_clientsecrets(client_secret, scops)
    >>> dir(flow)```
    >>> flow.redirect_uri = 'https://localhost'
    >>> flow.step1_get_authorize_url()
    'https://accounts.google.com/o/oauth2/auth?response_type=code&redirect_uri=https%3A%2F%2Flocalhost&access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&client_id=840431396841-7tm1c4o5m18jc5lpfai8p9cu8qhi5rf5.apps.googleusercontent.com'
