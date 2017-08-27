import os
from apiclient import errors
from pickled_service2_without_pickle_state_methods import auth_with_apiclient
from apiclient import http
# ...

# UTILITY FUNCTIONS:

class SyncService:
    """
    This class contains all the methods relating to files.
    I have temporarily defined alot of runtime variables in the init just for cnvenience, but I have to remember to remove it after...
    """
    def __init__(self, client_secrets="/home/justin/Downloads/gdrive4linux_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json", gdrive_scope='https://www.googleapis.com/auth/drive', pickle_path=False):
        """
        Create an object which has methods pertaining to files.

        Args:
            client_secrets, gdrive_scope and pickle_path are required to create a google drive service object.
        """
        if not pickle_path:
            # These pickled creds seem to be for j.w.winship@gmail.com:
            #pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21'
            # I know that these creds are for sudo.justin.wilson@gmail.com:
            pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21'
        instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path=pickle_path)
        self.service = instance.create_service()
        about = self.service.about().get().execute()
        email = about['user']['emailAddress']
        self._GDRIVE_DIR = os.path.expanduser('~/' + email)
        if not os.path.exists(self._GDRIVE_DIR):
            os.mkdir(self._GDRIVE_DIR)
        print('made it HERE!')

    
# FILE METHODS:

    def print_files_in_folder(self, folder_id, print_metadata=False):
      """print files belonging to a folder.
      This prints the child id, and I also call print_file_metadata(), which requires a child_id as an arg, and returns the name of the file, and the MIME type.
    
      Args:
        folder_id: ID of the folder to print files from.
      """
      page_token = None
      while True:
        try:
          param = {}
          if page_token:
            param['pageToken'] = page_token
          children = self.service.children().list(
              folderId=folder_id, **param).execute()
    
          for child in children.get('items', []):
            print('START NEW FILE')
            print('File Id: %s' % child['id'])
            print('The whole file is: ', child)
            if print_metadata:
                print('Here is when I call the print_file_metadata:')
                self.print_file_metadata(child['id'], whole_file=True)
                print('END NEW FILE')
          page_token = children.get('nextPageToken')
          if not page_token:
            break
        except errors.HttpError as error:
          print('An error occurred: %s' % error)
          break

    def get_metadata_to_download_files(self, folder_id, print_metadata=False):
      """
      This method is to get the required metadata, so I can download all the files. What I gotta do now is create the structs so each file/dir can be a node in the tree.
      """
      page_token = None
      while True:
        try:
          #file = service.files().get(fileId=file_id).execute()
          param = {}
          if page_token:
            param['pageToken'] = page_token
          param['orderBy'] = 'folder,title'
          children = self.service.children().list(
              folderId=folder_id, **param).execute()
    
          for child in children.get('items', []):
            print('START NEW FILE')
            file = self.service.files().get(fileId=child['id']).execute()
            print('File Id: %s' % child['id'])
            #print('The whole file is: ', child)
            #print('Here is when I run a loop on child to print the keys:')
            #for k in child:
            #    print('CHILD VALUE:\t', k)
            print('The name of the file is:\t %s' % file['title'])
            print('MIME type:\t %s' % file['mimeType'])
            print('The id of the files parents is:\t %s' % file['parents'][0]['id'])
            #print('The MD5 is:\t %s' % file['md5Checksum'])
            print('The MD5 is:\t %s' % file.get('md5Checksum'))
            if print_metadata:
                print('Here is when I call the print_file_metadata:')
                #print_file_metadata(service, child['id'], whole_file=True)
                print_file_metadata(self.service, child['id'], whole_file=False)
                print('END NEW FILE')
          page_token = children.get('nextPageToken')
          if not page_token:
            break
        except errors.HttpError as error:
          print('An error occurred: %s' % error)
          break
    
    # ...
    
    def is_file_in_folder(self, folder_id, file_id):
      """Check if a file is in a specific folder.
    
      Args:
        folder_id: ID of the folder.
        file_id: ID of the file.
      Returns:
        Whether or not the file is in the folder.
      """
      try:
        self.service.children().get(folderId=folder_id, childId=file_id).execute()
      except errors.HttpError as error:
        if error.resp.status == 404:
          return False
        else:
          print('An error occurred: %s' % error)
          raise error
      return True
    
    def print_file_metadata(self, file_id, whole_file=False):
      """print a file's metadata.
    
      Args:
        file_id: ID of the file to print metadata for.
      """
      try:
        file = self.service.files().get(fileId=file_id).execute()
    
        print('Title: %s' % file['title'])
        print('MIME type: %s' % file['mimeType'])
        if whole_file:
            print('This is the whole file:')
            print(file)
            print('Here is the dict items:')
            print([attr for attr in file.items()])
      except errors.HttpError as error:
        print('An error occurred: %s' % error)
    
    
    def print_file_content(self, file_id):
      """print(a file's content.)
    
      Args:
        file_id: ID of the file.
    
      Returns:
        File's content if successful, None otherwise.
      """
      try:
        print(self.service.files().get_media(fileId=file_id).execute())
      except errors.HttpError as error:
        print('An error occurred: %s' % error)
    
    
    def download_file(self, file_id, local_fd):
      """Download a Drive file's content to the local filesystem.
    
      Args:
        file_id: ID of the Drive file that will downloaded.
        local_fd: io.Base or file object, the stream that the Drive file's
            contents will be written to.
      """
      request = self.service.files().get_media(fileId=file_id)
      media_request = http.MediaIoBaseDownload(local_fd, request)
    
      while True:
        try:
          download_progress, done = media_request.next_chunk()
        except errors.HttpError as error:
          print('An error occurred: %s' % error)
          return
        if download_progress:
          print('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
          print('Download Complete')
          return

# ABOUT METHODS:
    #def get_about_object(self):
    #    """
    #    Returns an "about" object (dict), that can query user info, email, etc..
    #
    #    Args:
    #    """
    #    try:
    #        about = self.service.about().get().execute()
    #        return about
    #    except errors.HttpError as error:
    #        print('An error has occured: %s' % error)


if __name__ == '__main__':
    # STANDARD LOGISTICS:
    #client_secrets = "/home/justin/Downloads/gdrive4linux-client_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    syncservice = SyncService()
    print("Here is when I inspect a SyncService() object: ")
    print(dir(syncservice))
    print(type(syncservice))
    # Now I'm trying to print the methods of a SyncService.service object:
    service = syncservice.service
    print("This is the actual service object: ")
    print(type(service))
    print(dir(service))
    print("***NEW***: HERE'S WHEN CALL THE print_files_in_folder():")
    syncservice.print_files_in_folder('root')
    #def get_metadata_to_download_files(self, folder_id, print_metadata=False):
    syncservice.get_metadata_to_download_files('root')
    client_secrets = "/home/justin/Downloads/gdrive4linux_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    #gdrive_scope = 'https://www.googleapis.com/auth/drive'
    #instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    #instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='~/Dropbox/Coding/Projects/gdrive4linux/sudo.justin.wilson@gmail.com.pickled_credentials')
    #syncservice.instance = auth_with_apiclient(pickle_path='~/Dropbox/Coding/Projects/gdrive4linux/sudo.justin.wilson@gmail.com.pickled_credentials')
    #service = instance.create_service()
    ##
    ## This is to introspect the actual object:
    #print('Here is the object introspection:')
    #print(dir(service))
    #print('heres when I call the about method:')
    #about_instance = get_about_object(service)
    #print(about_instance)
    #email = email_address(about_instance)
    #print('Here is the email address:\t', email)
    ## Here is when I append the email onto the home dir:
    #homedir = os.path.expanduser('~/' + email + '/')
    #print('This should be the ~/gdrive dir:\t', homedir)
    ##
    # 'root' is alias for root dir
    #fid = 'root'
    # Here is the file id for "INSTALL.Docker.rst":
    #fid = '0B2Vt6e4DFEDGT1EtdXZrZUJ3N1U'
    # Here is the file id for a pdf file:
    #fid = '0B2Vt6e4DFEDGQ1RaZlJYRzZXeWs'
    #Here is the 'id' for the "Books" directory, in root:
    Books_id = '0B2Vt6e4DFEDGMTBqOGhpa2FjMFE'
    # Here is the file id for "new-books", which is a sub-directory of "Books" (which is a sub-directory of 'root'):
    # NOTE: I couldn't use "new-books" as a variable name, because it contains a "-" (which is an operator).. don't think I can avoid that...
    new_books_id = '0B2Vt6e4DFEDGemVrX2VjdFI1TVk'
    # Here is the file id for the "Pre-Calibre books" directory:
    precalibre_books_id = '0B2Vt6e4DFEDGWTNpM0xnVUtDVmc'
    ##
    # Use following methods to print the files in a gdrive dir:
    #print_files_in_folder(service, 'root', print_metadata=True)
    #syncservice.print_files_in_folder(precalibre_books_id, print_metadata=True)
    #syncservice.print_files_in_folder(precalibre_books_id)
    #syncservice.print_files_in_folder(Books_id)
    #print_files_in_folder(service, fid)
    ##
    # This was my attempt to download a file, but as yet, it has been unsuccessful:
    # I think this is the ATOM RFC text file?? Actually, I tried calling the download_file() method on it, and it said that the file id doesn't exist??:
    #fid = '0B6ujjnScaN51cTFUWW9vUmEyQ1k'
    ##
    # 2017-07-19: I confirmed that the "download_file()" method worked with the fid for INSTALL.Docker.rst and a pdf file (in ~/tmp):
    #local_path = '/home/justin/tmp/gdrive4linux_test_download_file-today'
    #with open(local_path, 'wb') as f:
    #    download_file(service, fid, f)
    ##
    # HERE'S WHEN I CALL THE print_file_metadata() method:
    #print_file_metadata(service, file_id, whole_file=False):
    ##print('this is when I called print_file_metadata with whole_file=True')
    ##print_file_metadata(service, file_id, whole_file=True)
    ##
    # 2017-07-19: I was able to print the contents of the "INSTALL.Docker.rst" file, with the following method:
    #print_file_content(service, fid)
    ##
    # Here's how to search ofr a JPEG file, and print the title and file_id:
    #page_token = None
    #while True:
    #    #response = service.files().list(q="mimeType='image/jpeg'",
    #    response = service.files().list(q="mimeType != 'application/vnd.google-apps.folder'",
    #                                         spaces='drive',
    #                                         fields='nextPageToken, items(id, title)',
    #                                         pageToken=page_token).execute()
    #    for file in response.get('items', []):
    #        # Process change
    #        print('Found file: %s (%s)' % (file.get('title'), file.get('id')))
    #    page_token = response.get('nextPageToken', None)
    #    if page_token is None:
    #        break;
