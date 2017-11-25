import argparse
import json
import os

from googleservice import auth_with_apiclient
from v2_methods import Methods, calculatemd5

"""
This file is the main executable file. It should be the only file that needs to be executed, and it will import set everything up and execute whatever needs to be executed.
"""

# define local paths:

class Sync(Methods):

    def __init__(self, local_creds, verbose=True):
        """
        Class that actually executes the commands.

        Args:
        - local_creds: This is a json file which contains the following keys:
            client_secrets= This specifies the path to the client secrets.
            pickle_path= (optional?) This specifies the local path where the pickled creds will/or are stored.
        """
        self.verbose = verbose
        # config_dir stores app data (not user data):
        config_dir = os.path.expanduser('~/.gdrive4linux/')
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        # This is where I'll store the file metadata:
        self.SHELVE_PATH = config_dir + 'metadata.shelve'

        try:
            with open(local_creds) as f:
                creds = json.load(f)
                instance = auth_with_apiclient(creds['client_secrets'], creds['gdrive_scope'], pickle_path = config_dir + '.creds.pickle')
                self.service = instance.create_service()
            email = self.about(self.service)['user']['emailAddress']
            #email = self.service.about().get().execute()['user']['emailAddress']
            self.gdrive_root_dir = os.path.expanduser('~/' + email)
        except AttributeError as e:
            print("You didn't provide a valid local_creds json file")
            return
        except Exception as e:
            print("There was an error")
            return

    #def mkdir_gdrive_root(self, service=self.service, path=None,):
    #    """
    #    Create the google drive root directory, where the user's files will be stored.
    #    """
    #    about_object = SyncService

if __name__ == '__main__':
    instance = Sync('.local_path')
    #print(dir(instance))
    #print("The email address is:")
    ##print(instance.about(instance.service)['user']['emailAddress'])
    ##print(type(instance.email))
    #print(instance.gdrive_root_dir) 

    ## test get_changes:
    #changes = instance.get_changes('4244')
    #print(type(changes))
    #print(changes.keys())
    changes = instance.new_retrieve_all_changes(start_change_id='240')
    print(type(changes))
    print(dir(changes))
    print("The len of items is:")
    print(len(changes['items']))
    print("newStartPageToken is:")
    print(changes['newStartPageToken'])
    print(changes.keys())
    
    #saved_start_page_token = '4244'
    ## Begin with our last saved start token for this user or the
    ## current token from getStartPageToken()
    #page_token = saved_start_page_token;
    #while page_token is not None:
    #    response = instance.service.changes().list(pageToken=page_token,
    #                                            spaces='drive').execute()
    #    for change in response.get('items'):
    #        # Process change
    #        print('Change found for file: %s' % change.get('fileId'))
    #    if 'newStartPageToken' in response:
    #        # Last page, save this token for the next polling interval
    #        saved_start_page_token = response.get('newStartPageToken')
    #    page_token = response.get('nextPageToken')
    #    print()
    #    print()
    #    print()
    #    print(dir(page_token))
    #    print(type(page_token))
    #    print(page_token)
