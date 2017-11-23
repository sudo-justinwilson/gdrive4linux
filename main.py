import argparse
import json
import os

from googleservice import auth_with_apiclient
from file_methods import Methods, calculatemd5

"""
This file is the main executable file. It should be the only file that needs to be executed, and it will import set everything up and execute whatever needs to be executed.
"""

# define local paths:

class Sync(Methods):

    def __init__(self, local_creds):
        """
        Class that actually executes the commands.

        Args:
        - local_creds: This is a json file which contains the following keys:
            client_secrets= This specifies the path to the client secrets.
            pickle_path= (optional?) This specifies the local path where the pickled creds will/or are stored.
        """
        # CONFIG_PATH stores app data (not user data):
        CONFIG_PATH = os.path.expanduser('~/.gdrive4linux/')
        if not os.path.exists(CONFIG_PATH):
            os.mkdir(CONFIG_PATH)

        # This is where I'll store the file metadata:
        self.SHELVE_PATH = CONFIG_PATH + 'metadata.shelve'

        try:
            with open(local_creds) as f:
                creds = json.load(f)
                instance = auth_with_apiclient(creds['client_secrets'], creds['gdrive_scope'], pickle_path = CONFIG_PATH + '.creds.pickle')
                self.service = instance.create_service()
            email = self.about(self.service)['user']['emailAddress']
            #email = self.service.about().get().execute()['user']['emailAddress']
            self.gdrive_root_dir = os.path.expanduser('~/' + email)
        except AttributeError as e:
            print("You didn't provide a valid local_creds json file")
            raise e
        except Exception as e:
            print("There was an error")
            raise e

    #def mkdir_gdrive_root(self, service=self.service, path=None,):
    #    """
    #    Create the google drive root directory, where the user's files will be stored.
    #    """
    #    about_object = SyncService

if __name__ == '__main__':
    instance = Sync('.local_path')
    print(dir(instance))
    print("The email address is:")
    #print(instance.about(instance.service)['user']['emailAddress'])
    #print(type(instance.email))
    print(instance.gdrive_root_dir) 
