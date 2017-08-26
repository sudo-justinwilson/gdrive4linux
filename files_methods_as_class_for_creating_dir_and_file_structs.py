from apiclient import errors
from pickled_service2_without_pickle_state_methods import auth_with_apiclient
from os.path import expanduser
# ...

# FILE METHODS:

def print_files_in_folder(service, folder_id, print_metadata=False):
  """print files belonging to a folder.
  This prints the child id, and I also call print_file_metadata(), which requires a child_id as an arg, and returns the name of the file, and the MIME type.

  Args:
    service: Drive API service instance.
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
        #print('The whole file is: ', child)
        #print('Here is when I run a loop on child to print the keys:')
        #for k in child:
        #    print('CHILD VALUE:\t', k)
        if print_metadata:
            print('Here is when I call the print_file_metadata:')
            #print_file_metadata(service, child['id'], whole_file=True)
            print_file_metadata(service, child['id'], whole_file=False)
            print('END NEW FILE')
      page_token = children.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError as error:
      print('An error occurred: %s' % error)
      break

# ...

def is_file_in_folder(service, folder_id, file_id):
  """Check if a file is in a specific folder.

  Args:
    service: Drive API service instance.
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

from apiclient import errors
from apiclient import http
# ...

def print_file_metadata(service, file_id, whole_file=False):
  """print a file's metadata.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to print metadata for.
  """
  try:
    file = service.files().get(fileId=file_id).execute()

    print('The name of the file is:\t %s' % file['title'])
    print('MIME type:\t %s' % file['mimeType'])
    print('The id of the files parents is:\t %s' % file['parents'])
    #print('The MD5 is:\t %s' % file['md5Checksum'])
    print('The MD5 is:\t %s' % file.get('md5Checksum'))
    if whole_file:
        #print('This is the whole file:')
        #print(file)
        print('Here is the dict items:')
        for k in file:
            print('FILE FROM METADATA:\t', k)
        #print([attr for attr in file.items()])
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def print_file_content(service, file_id):
  """print(a file's content.)

  Args:
    service: Drive API service instance.
    file_id: ID of the file.

  Returns:
    File's content if successful, None otherwise.
  """
  try:
    print(service.files().get_media(fileId=file_id).execute())
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def download_file(service, file_id, local_fd):
  """Download a Drive file's content to the local filesystem.

  Args:
    service: Drive API Service instance.
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

# ABOUT METHODS:

def get_about_object(service):
    """
    Returns an "about" object (dict), that can query user info, email, etc..

    Args:
        service: authorized gdrive API service instance.
    """
    try:
        about = service.about().get().execute()
        return about
    except errors.HttpError as error:
        print('An error has occured: %s' % error)

def email_address(about_object):
    """
    Return the email address (string).

    Args:
        about_object: An "about" instance.
    """
    email = about_object['user']['emailAddress']
    return email



if __name__ == '__main__':
    # STANDARD LOGISTICS:
    #client_secrets = "/home/justin/Downloads/gdrive4linux-client_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    client_secrets = "/home/justin/Downloads/gdrive4linux_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    service = instance.create_service()
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
    #homedir = expanduser('~/' + email + '/')
    #print('This should be the ~/gdrive dir:\t', homedir)
    ##
    # 'root' is alias for root dir
    fid = 'root'
    # Here is the file id for "INSTALL.Docker.rst":
    #fid = '0B2Vt6e4DFEDGT1EtdXZrZUJ3N1U'
    # Here is the file id for a pdf file:
    #fid = '0B2Vt6e4DFEDGQ1RaZlJYRzZXeWs'
    ##
    # Use following methods to print the files in a gdrive dir:
    print_files_in_folder(service, fid, print_metadata=True)
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
