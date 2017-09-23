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
            # These pickled creds are for cik.smarthomes@gmail.com:
            pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21'
        instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path=pickle_path)
        self.service = instance.create_service()
        about = self.service.about().get().execute()
        email = about['user']['emailAddress']
        # I wanted to hardcode a trailing '/':
        self._GDRIVE_DIR = os.path.expanduser('~/' + email)
        #self._GDRIVE_DIR = os.path.expanduser('~/' + email + '/')
        if not os.path.exists(self._GDRIVE_DIR):
            os.mkdir(self._GDRIVE_DIR)

    
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

    def get_metadata_to_download_files(self, folder_id, print_metadata=False, return_dict=False):
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
            #print('START NEW FILE')
            file = self.service.files().get(fileId=child['id']).execute()
            if return_dict:
                yield file 
            else:
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

    def sync_from_gdrive_to_local(self, folder_id=None, current_dir_path=None):
        """
        This is an initial method I am going to use to sync remote gdrive directories to the local disk. 
        It might be rough at first, but we'll see how it goes...
        """
        if not folder_id:
            folder_id = 'root'
        if not current_dir_path:
            current_dir_path = self._GDRIVE_DIR
        page_token = None
        while True:
          try:
            #file = service.files().get(fileId=file_id).execute()
            # The 'param' is where we can add params as keys for list method:
            param = {}
            if page_token:
              param['pageToken'] = page_token
            # Add orderBy=folder,title param, so the results are ordered by directories first, then name:
            param['orderBy'] = 'folder,title'
            print('Calling\t children().list(), etc:')
            children = self.service.children().list(
                folderId=folder_id, **param).execute()
    
            print('Entering for child loop:')
            for child in children.get('items', []):
              #print('START NEW FILE')
              print('In for child loop. Calling file_meta method:')
              file_meta = self.service.files().get(fileId=child['id']).execute()
              print('File Id: %s' % child['id'])
              print('The name of the file is:\t %s' % file_meta['title'])
              print('MIME type:\t %s' % file_meta['mimeType'])
              print('The id of the files parents is:\t %s' % file_meta['parents'][0]['id'])
              print('The MD5 is:\t %s' % file_meta.get('md5Checksum'))
              ## START SYNC
              # test if MIME type = drive folder:
              local_path = current_dir_path + '/' + file_meta['title']
              if file_meta['mimeType'] == 'application/vnd.google-apps.folder':
                # if directory doesn't already exist:
                if not os.path.exists(local_path):
                  # create directory:
                  print('MAKING DIRECTORY:\t', local_path)
                  os.mkdir(local_path)
                # Calling itself recursively:
                print('Calling sync recursively:')
                #new_dir_path = current_dir_path + '/' file_meta['title']
                print('This is the new_dir_path:\t', local_path)
                self.sync_from_gdrive_to_local(folder_id = file_meta['id'], current_dir_path = local_path)
              # test if the file type is a pdf:
              if file_meta['mimeType'] == 'application/pdf': 
                #filename = local_path + '.' + 'pdf'
                print('This is the filename:\t', local_path)
                with open(local_path, 'wb') as f:
                  self.download_file(file_meta['id'], f)
              #download_file(self, file_id, local_fd):
              ## END SYNC
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
    syncservice = SyncService()
    #print('before calling syncservice')
    #syncservice.sync_from_gdrive_to_local()
    #print('after calling syncservice')
    #Books_id = '0B2Vt6e4DFEDGMTBqOGhpa2FjMFE'
    ## Here is the file id for "new-books", which is a sub-directory of "Books" (which is a sub-directory of 'root'):
    ## NOTE: I couldn't use "new-books" as a variable name, because it contains a "-" (which is an operator).. don't think I can avoid that...
    #new_books_id = '0B2Vt6e4DFEDGemVrX2VjdFI1TVk'
    ## Here is the file id for the "Pre-Calibre books" directory:
    #precalibre_books_id = '0B2Vt6e4DFEDGWTNpM0xnVUtDVmc'


    #def get_metadata_to_download_files(self, folder_id, print_metadata=False, return_dict=False):
    path = '/home/justin/Dropbox/Coding/Projects/gdrive4linux/'
    cik_smarthomes = {}
    for f in syncservice.get_metadata_to_download_files('root', return_dict=True):
        #print("Here's when I call f['id']:\t", f['id'])
        #print('Here are the items in the dict:\t', f.items())
        cik_smarthomes[f['id']] = f
    filename = 'cik.smarthomes@gmail.com_list-files_in_root.json'
    import json
    #print("here is the total dict:\n", json.dumps(cik_smarthomes, indent=4))
    json.dump(cik_smarthomes, open(path + filename, 'w'), indent=4)
