import os
import json
import shelve
from apiclient import errors
from googleservice import auth_with_apiclient
from apiclient import http
# ...

# UTILITY FUNCTIONS:
def calculatemd5(filename, block_size=2**20):
    import hashlib
    md5 = hashlib.md5()
    file = open(filename, 'rb')
    while True:
            data = file.read(block_size)
            if not data:
                    break
            md5.update(data)
    return md5.hexdigest()

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
            pickle_path='/home/justin/Dropbox/Coding/Projects/gdrive4linux/cik.smarthomes.pickled_credentials_20170929'
        instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path=pickle_path)
        self.service = instance.create_service()
        about = self.service.about().get().execute()
        self.email = about['user']['emailAddress']
        self._ROOT_DIR = os.path.expanduser('~/' + self.email)
        if not os.path.exists(self._ROOT_DIR):
            os.mkdir(self._ROOT_DIR)
        self.CACHE_DIR =  self._ROOT_DIR + '/.config'
        if not os.path.exists(self.CACHE_DIR):
            os.mkdir(self.CACHE_DIR)
        # store the user data:
        if not os.path.exists(self.CACHE_DIR + '/.about'):
            json.dump(about, open(self.CACHE_DIR + '/.about', 'w'), indent=4)
        self.SHELVE_PATH = self.CACHE_DIR + '/.metadata_cache.db'

    
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

    def sync_from_gdrive_to_local(self, folder_id='root', current_dir_path=None):
        """
        This is an initial method I am going to use to sync remote gdrive directories to the local disk. 
        It might be rough at first, but we'll see how it goes...
        """
        #if not folder_id:
        #    folder_id = 'root'
        if not current_dir_path:
            current_dir_path = self._ROOT_DIR
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
              print('In for child loop. Calling file_meta method:')
              #file_meta = self.service.files().get(fileId=child['id']).execute()
              file_meta = self.get_file_metadata(child['id'])
              print('File Id: %s' % child['id'])
              print('The name of the file is:\t %s' % file_meta['title'])
              print('MIME type:\t %s' % file_meta['mimeType'])
              print('The id of the files parents is:\t %s' % file_meta['parents'][0]['id'])
              print('The MD5 is:\t %s' % file_meta.get('md5Checksum'))
              ## START SYNC
              local_path = current_dir_path + '/' + file_meta['title']
              # The following is a dict which keys are the different types of MIME types of the files in google drive, and the values are how google describes the different types of files:
              # google docs, sheets, presentations, etc all start with "application/vnd.google-apps."
              mime_types = { 
                    "folder" : "application/vnd.google-apps.folder",
                    "google_file" : "application/vnd.google-apps.",
                    "pdf" : "application/pdf",
                    "txt" : "text/plain",
                    }
                        
              # test if MIME type = drive folder:
              if file_meta['mimeType'] == mime_types['folder']:
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
              # test if the mime type of the file is not a Google doc, sheet, presentation, etc, as we can't download those sort of files without exporting them to a different format - which will cause problems with syncing:
              else: 
                if not file_meta['mimeType'].startswith(mime_types["google_file"]):
                    print('This is the filename:\t', local_path)
                    ## test if the file already exists:
                    if not os.path.exists(local_path):
                    #    # test if the file contents are the same as the remote file:

                        with open(local_path, 'wb') as f:
                            self.download_file(file_meta['id'], f)
              ## END SYNC
            page_token = children.get('nextPageToken')
            if not page_token:
              break
          except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break

    def new_sync_from_gdrive_to_local(self, folder_id='root', current_dir_path=None):
        """
        This is an initial method I am going to use to sync remote gdrive directories to the local disk. 
        It might be rough at first, but we'll see how it goes...
        """
        #if not folder_id:
        #    folder_id = 'root'
        if not current_dir_path:
            current_dir_path = self._ROOT_DIR
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
              print('In for child loop. Calling file_meta method:')
              #file_meta = self.service.files().get(fileId=child['id']).execute()
              file_meta = self.get_file_metadata(child['id'])
              # Store the file metadata in a shelve file:
              print("HERE IS THE SHELVE.PATH:\t", self.SHELVE_PATH)
              #shelve_db = shelve.open(self.SHELVE_PATH)
              with shelve.open(self.SHELVE_PATH) as shelve_db:
                shelve_db[child['id']] = file_meta
              print('File Id: %s' % child['id'])
              print('The name of the file is:\t %s' % file_meta['title'])
              print('MIME type:\t %s' % file_meta['mimeType'])
              print('The id of the files parents is:\t %s' % file_meta['parents'][0]['id'])
              print('The MD5 is:\t %s' % file_meta.get('md5Checksum'))
              ## START SYNC
              local_path = current_dir_path + '/' + file_meta['title']
              # The following is a dict which keys are the different types of MIME types of the files in google drive, and the values are how google describes the different types of files:
              # google docs, sheets, presentations, etc all start with "application/vnd.google-apps."
              mime_types = { 
                    "folder" : "application/vnd.google-apps.folder",
                    "google_file" : "application/vnd.google-apps.",
                    "pdf" : "application/pdf",
                    "txt" : "text/plain",
                    }
                        
              # test if MIME type = drive folder:
              if file_meta['mimeType'] == mime_types['folder']:
                # if directory doesn't already exist:
                if not os.path.exists(local_path):
                  # create directory:
                  print('MAKING DIRECTORY:\t', local_path)
                  os.mkdir(local_path)
                # Calling itself recursively:
                print('Calling sync recursively:')
                #new_dir_path = current_dir_path + '/' file_meta['title']
                print('This is the new_dir_path:\t', local_path)
                self.new_sync_from_gdrive_to_local(folder_id = file_meta['id'], current_dir_path = local_path)
              # test if the mime type of the file is not a Google doc, sheet, presentation, etc, as we can't download those sort of files without exporting them to a different format - which will cause problems with syncing:
              else: 
                #if not file_meta['mimeType'].startswith(mime_types["google_file"]):
                #    print('This is the filename:\t', local_path)
                #    ## test if the file already exists:
                #    if not os.path.exists(local_path):
                #        # test if the file contents are the same as the remote file:
                #        with open(local_path, 'wb') as f:
                #            self.download_file(file_meta['id'], f)
                ## NEW
                if not file_meta['mimeType'].startswith(mime_types["google_file"]):
                    print('This is the filename:\t', local_path)
                    ## test if the file already exists:
                    if os.path.exists(local_path):
                        # test if the file contents are the same as the remote file:
                        print("The remote md5 is:\t", file_meta['md5Checksum'])
                        print("The local  md5 is:\t", calculatemd5(local_path))
                        if file_meta['md5Checksum'] != calculatemd5(local_path):
                            # download the file:
                            print("The file has changed. Downloading..")
                            with open(local_path, 'wb') as f:
                                self.download_file(file_meta['id'], f)
                        else:
                            print("The file already exists and the hashes match!")
                ## END
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
    
    def get_file_metadata(self,file_id):
        """
        Makes a call to get the file's metadata, and returns it as a dict.
        
            Args:
            - file_id:  the id of the file to download.
        """
        try:
            file_metadata = self.service.files().get(fileId = file_id).execute()
            return file_metadata
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def print_file_metadata(self, file_id, whole_file=False,return_dict=False):
      """print a file's metadata.
    
      Args:
        file_id: ID of the file to print metadata for.
      """
      try:
        file = self.service.files().get(fileId=file_id).execute()
        if return_dict:
            return file
    
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


if __name__ == '__main__':
    syncservice = SyncService()
    print('before calling syncservice')
    #syncservice.sync_from_gdrive_to_local()
    syncservice.new_sync_from_gdrive_to_local()
    #print('after calling syncservice')
    #Books_id = '0B2Vt6e4DFEDGMTBqOGhpa2FjMFE'
    ## Here is the file id for "new-books", which is a sub-directory of "Books" (which is a sub-directory of 'root'):
    ## NOTE: I couldn't use "new-books" as a variable name, because it contains a "-" (which is an operator).. don't think I can avoid that...
    #new_books_id = '0B2Vt6e4DFEDGemVrX2VjdFI1TVk'
    ## Here is the file id for the "Pre-Calibre books" directory:
    #precalibre_books_id = '0B2Vt6e4DFEDGWTNpM0xnVUtDVmc'


    #def get_metadata_to_download_files(self, folder_id, print_metadata=False, return_dict=False):
    #path = '/home/justin/Dropbox/Coding/Projects/gdrive4linux/'
    #cik_smarthomes = {}
    #for f in syncservice.get_metadata_to_download_files('root', return_dict=True):
    #    #print("Here's when I call f['id']:\t", f['id'])
    #    #print('Here are the items in the dict:\t', f.items())
    #    cik_smarthomes[f['id']] = f
    #filename = 'cik.smarthomes@gmail.com_list-files_in_root.json'
    #import json
    ##print("here is the total dict:\n", json.dumps(cik_smarthomes, indent=4))
    #json.dump(cik_smarthomes, open(path + filename, 'w'), indent=4)
    ##def print_file_metadata(self, file_id, whole_file=False):
    # Test the "return_dict" optional arg:
    #import json
    #d = syncservice.print_file_metadata('root', whole_file=True, return_dict=True)
    #print("here is the returned dict:", d)
    #print(json.dumps(d, indent=4))
    #print("here is the email address that we're using:\t", syncservice.email)
    #
    #def calculatemd5(filename, block_size=2**20):
    #    import hashlib
    #    md5 = hashlib.md5()
    #    file = open(filename, 'rb')
    #    while True:
    #            data = file.read(block_size)
    #            if not data:
    #                    break
    #            md5.update(data)
    #    return md5.hexdigest()

    #path = "/home/justin/tmp/test-file.txt"
    #print("This is the path to the file that we want the md5 of:\t", path)
    #print("Now we'll calculate the md5 hash:")
    #print(calculatemd5(path))
    #

    #def get_meta(folder='root'):
    #    print("This is the folder that we're in right now:\t", folder)
    #    for thing in syncservice.get_metadata_to_download_files(folder, print_metadata=True, return_dict=True):
    #        print(json.dumps(thing, indent=4))
    #        if thing['mimeType'] == "application/vnd.google-apps.folder":
    #            print("Found an item that is a folder!")
    #            return get_meta(folder=thing['id'])

    #get_meta()

    #for thing in syncservice.get_metadata_to_download_files('root', print_metadata=True, return_dict=True):
    #    #if thing['mimeType'] == "application/vnd.google-apps.folder":
    #    #    for thing in syncservice.get_metadata_to_download_files('root', print_metadata=True, return_dict=True):
    #        
    #    print("The title of the thing is:\t", thing['title'])
    #    print("The type of the thing is:\t", type(thing))
    #    print("The mime type of the thing is:\t", thing['mimeType'])
    #    print("The id of the the thing is:\t", thing['id'])
    #    print('The MD5 is:\t %s' % thing.get('md5Checksum'))
    #    
    #    #print(thing)
    ##                    "folder" : "application/vnd.google-apps.folder",
    ## def print_files_in_folder(self, folder_id, print_metadata=False):

    ## I want to see if I can recover teh shelved db:
    #path = syncservice.SHELVE_PATH
    #with shelve.open(path) as db:
    #    for k in db:
    #        print(k)
    ## I AM PLEASED TO CONFIRM THAT IT WORKS!!

    #
    ## Test if the calculatemd5() function:
    #h = calculatemd5(syncservice.SHELVE_PATH)
    #print("The hash is:\t", h)

