import os
import json
import shelve
from apiclient import errors
#from googleservice import auth_with_apiclient
from apiclient import http
from testing import debug

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

#class SyncService:
class Methods:
    """
    This class contains all the methods relating to files.
    I have temporarily defined alot of runtime variables in the init just for cnvenience, but I have to remember to remove it after...
    """
    def __init__(self, verbose=False):
        """
        Create an object which has methods pertaining to files.

        Args:
            client_secrets, gdrive_scope and pickle_path are required to create a google drive service object.
        """
        #if not pickle_path:
        #    try:
        #        # These pickled creds are for cik.smarthomes@gmail.com:
        #        pickle_path='/home/justin/Dropbox/Coding/Projects/gdrive4linux/cik.smarthomes.pickled_credentials_20170929'
        #    except FileNotFoundError as e:
        #        print("The pickle path that you provided does not exist:\t", e)
        #    except exception as e:
        #        print("There was an error:\t", e)
        #instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path=pickle_path)
        # Rip out self.service so that it's not hard-coded in:
        #self.service = instance.create_service()
        # I'll have to put this function into another module, so that the other module creates the gdrive root directory:
        #about = self.service.about().get().execute()
        #self.email = about['user']['emailAddress']
        #self._ROOT_DIR = os.path.expanduser('~/' + self.email)
        #if not os.path.exists(self._ROOT_DIR):
        #    os.mkdir(self._ROOT_DIR)
        #self.CACHE_DIR =  self._ROOT_DIR + '/.config'
        #if not os.path.exists(self.CACHE_DIR):
        #    os.mkdir(self.CACHE_DIR)
        ## store the user data:
        #if not os.path.exists(self.CACHE_DIR + '/.about'):
        #    json.dump(about, open(self.CACHE_DIR + '/.about', 'w'), indent=4)
        #self.SHELVE_PATH = self.CACHE_DIR + '/.metadata_cache.db'
        # 'verbose' is a flag that indicates whether or not to print debugging data lines:
        self.verbose = verbose

    
# FILE METHODS:

    def print_files_in_folder(self, service, folder_id, print_metadata=False):
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
          children = service.children().list(
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

    def get_metadata_to_download_files(self, service, folder_id, print_metadata=False, return_dict=False):
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
          children = service.children().list(
              folderId=folder_id, **param).execute()
    
          for child in children.get('items', []):
            #print('START NEW FILE')
            file = service.files().get(fileId=child['id']).execute()
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
                    print_file_metadata(service, child['id'], whole_file=False)
                    print('END NEW FILE')
          page_token = children.get('nextPageToken')
          if not page_token:
            break
        except errors.HttpError as error:
          print('An error occurred: %s' % error)
          break

    def sync_from_gdrive_to_local(self, service, folder_id='root', current_dir_path=None):
        """
        This is an initial method I am going to use to sync remote gdrive directories to the local disk. 
        It might be rough at first, but we'll see how it goes...
        """
        #if not folder_id:
        #    folder_id = 'root'
        # The current_dir_path needs to be passed as an arg:
        #if not current_dir_path:
            #current_dir_path = self._ROOT_DIR
        page_token = None
        while True:
          try:
            param = {}
            if page_token:
              param['pageToken'] = page_token
            # Add orderBy=folder,title param, so the results are ordered by directories first, then name:
            param['orderBy'] = 'folder,title'
            print('Calling\t children().list(), etc:')
            children = service.children().list(
                folderId=folder_id, **param).execute()
    
            print('Entering for child loop:')
            for child in children.get('items', []):
              print('In for child loop. Calling file_meta method:')
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
            print('An HTTP error occurred: %s' % error)
            break
          except TypeError as error:
            print(e.args)
            break

    def new_sync_from_gdrive_to_local(self, service, SHELVE_PATH, folder_id='root', current_dir_path=None):
        """
        This is an initial method I am going to use to sync remote gdrive directories to the local disk. 
        It might be rough at first, but we'll see how it goes...
        """
        #if not folder_id:
        #    folder_id = 'root'
        #if not current_dir_path:
        #    current_dir_path = self._ROOT_DIR
        page_token = None
        while True:
          try:
            param = {}
            if page_token:
              param['pageToken'] = page_token
            # Add orderBy=folder,title param, so the results are ordered by directories first, then name:
            param['orderBy'] = 'folder,title'
            debug(self.verbose, 'Calling\t children().list(), etc:')
            children = service.children().list(
                folderId=folder_id, **param).execute()
    
            debug(self.verbose, 'Entering for child loop:')
            for child in children.get('items', []):
              debug(self.verbose, 'In for child loop. Calling file_meta method:')
              file_meta = self.get_file_metadata(child['id'])
              # Store the file metadata in a shelve file:
              debug(self.verbose, "HERE IS THE SHELVE.PATH:\t", SHELVE_PATH)
              with shelve.open(SHELVE_PATH) as shelve_db:
                shelve_db[child['id']] = file_meta
              debug(self.verbose, 'File Id: %s' % child['id'])
              debug(self.verbose, 'The name of the file is:\t %s' % file_meta['title'])
              debug(self.verbose, 'MIME type:\t %s' % file_meta['mimeType'])
              debug(self.verbose, 'The id of the files parents is:\t %s' % file_meta['parents'][0]['id'])
              debug(self.verbose, 'The MD5 is:\t %s' % file_meta.get('md5Checksum'))
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
                  debug(self.verbose, 'MAKING DIRECTORY:\t', local_path)
                  os.mkdir(local_path)
                # Calling itself recursively:
                debug(self.verbose, 'Calling sync recursively:')
                #new_dir_path = current_dir_path + '/' file_meta['title']
                debug(self.verbose, 'This is the new_dir_path:\t', local_path)
                self.new_sync_from_gdrive_to_local(service, SHELVE_PATH, folder_id = file_meta['id'], current_dir_path = local_path)
              # test if the mime type of the file is not a Google doc, sheet, presentation, etc, as we can't download those sort of files without exporting them to a different format - which will cause problems with syncing:
              else: 
                if not file_meta['mimeType'].startswith(mime_types["google_file"]):
                    debug(self.verbose, 'This is the filename:\t', local_path)
                    ## test if the file already exists:
                    if os.path.exists(local_path):
                        try:
                            # test if the file contents are the same as the remote file:
                            debug(self.verbose, "The remote md5 is:\t", file_meta['md5Checksum'])
                            debug(self.verbose, "The local  md5 is:\t", calculatemd5(local_path))
                            if file_meta['md5Checksum'] != calculatemd5(local_path):
                                # download the file:
                                debug(self.verbose, "The file has changed. Downloading..")
                                with open(local_path, 'wb') as f:
                                    self.download_file(file_meta['id'], f)
                            else:
                                debug(self.verbose, "The file already exists and the hashes match!")
                        except Exception as e:
                            print("An error occurred:\t", e)
            page_token = children.get('nextPageToken')
            if not page_token:
              break
          except errors.HttpError as error:
            print('An HTTP error occurred: %s' % error)
            break
          except TypeError as error:
            print(e.args)
            break
    
    
    # ...
    
    def is_file_in_folder(self, service, folder_id, file_id):
      """Check if a file is in a specific folder.
    
      Args:
        folder_id: ID of the folder.
        file_id: ID of the file.
      Returns:
        Whether or not the file is in the folder.
      """
      try:
        service.children().get(folderId=folder_id, childId=file_id).execute()
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
            file_metadata = service.files().get(fileId = file_id).execute()
            return file_metadata
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def print_file_metadata(self, service, file_id, whole_file=False,return_dict=False):
      """print a file's metadata.
    
      Args:
        file_id: ID of the file to print metadata for.
      """
      try:
        file = service.files().get(fileId=file_id).execute()
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
        print(service.files().get_media(fileId=file_id).execute())
      except errors.HttpError as error:
        print('An error occurred: %s' % error)
    
    
    def download_file(self, file_id, local_fd):
      """Download a Drive file's content to the local filesystem.
    
      Args:
        file_id: ID of the Drive file that will downloaded.
        local_fd: io.Base or file object, the stream that the Drive file's
            contents will be written to.
      """
      request = service.files().get_media(fileId=file_id)
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

    ## CHANGE METHODS:
    def getstartpagetoken(self, service):
        try:
            changes = service.changes().getStartPageToken()
            print("Here is the dir:\t", dir(changes))
            number = changes.execute()
            print("finished calling execute")
            print("The type of the number is:\t", type(number))
            print("The number is:\t", number)
            #service.changes
        except Exception as e:
            print("An error occurred:\t", e)
            return
        return number

    def retrieve_all_changes(self, service, start_change_id=None):
      """Retrieve a list of Change resources.
    
      Args:
        service: Drive API service instance.
        start_change_id: ID of the change to start retrieving subsequent changes
                         from or None.
      Returns:
        List of Change resources.
      """
      result = []
      page_token = None
      while True:
        try:
          param = {}
          if start_change_id:
            param['startChangeId'] = start_change_id
          if page_token:
            param['pageToken'] = page_token
          changes = service.changes().list(**param).execute()
    
          result.extend(changes['items'])
          page_token = changes.get('nextPageToken')
          if not page_token:
            break
        #except errors.HttpError, error as
        except Exception as e:
          print('An error occurred: %s' % error)
          break
      return result

    def about(self, service):
        """
        Returns an "about" object.
        """
        #self.email = about['user']['emailAddress']
        about = self.service.about().get().execute()
        return about




if __name__ == '__main__':
    # This tests when verbose is set to True:
    syncservice = SyncService(verbose=True)
    # This tests when verbose is set to False (default):
    #syncservice = SyncService()
    #print('before calling syncservice')
    #syncservice.sync_from_gdrive_to_local()
    syncservice.new_sync_from_gdrive_to_local()
