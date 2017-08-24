from apiclient import errors
from pickled_service2_without_pickle_state_methods import auth_with_apiclient
# ...



def print_files_in_folder(service, folder_id):
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
        print('The whole file is: ', child)
        print('Here is when I call the print_file_metadata:')
        print_file_metadata(service, child['id'], whole_file=True)
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

    print('Title: %s' % file['title'])
    print('MIME type: %s' % file['mimeType'])
    if whole_file:
        print('This is the whole file:')
        print(file)
        print('Here is the dict items:')
        print([attr for attr in file.items()])
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

if __name__ == '__main__':
    client_secrets = "/home/justin/Downloads/gdrive4linux-client_secret_496253704845-c2bofad70kl7nj0415p7fnrptv6c1ftd.apps.googleusercontent.com.json"
    gdrive_scope = 'https://www.googleapis.com/auth/drive'
    instance = auth_with_apiclient(client_path=client_secrets, scope=gdrive_scope, pickle_path='/home/justin/tmp/token_from_auth_with_object-2017-05-21')
    service = instance.create_service()
    fid = 'root'
    #print_files_in_folder(service, fid)
    # This was my attempt to download a file, but as yet, it has been unsuccessful:
    file_id = '0B6ujjnScaN51cTFUWW9vUmEyQ1k'
    local_path = '/home/justin/tmp/gdrive4linux_test_download_file'
    #local_file = open(local_path, 'wb')
    #download_file(service, file_id, local_fd):
    #download_file(service, file_id, local_fd):
    with open(local_path, 'wb') as f:
        download_file(service, file_id, f)
    # HERE'S WHEN I CALL THE print_file_metadata() method:
    #print_file_metadata(service, file_id, whole_file=False):
    print('this is when I called print_file_metadata with whole_file=True')
    print_file_metadata(service, file_id, whole_file=True)
    #print_file_content(service, file_id):
    #print_file_content(service, file_id)
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
