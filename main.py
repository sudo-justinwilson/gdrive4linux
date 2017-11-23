import argparse
import json
import os

from googleservice import auth_with_apiclient
from file_methods import SyncService, calculatemd5

"""
This file is the main executable file. It should be the only file that needs to be executed, and it will import set everything up and execute whatever needs to be executed.
"""

# define local paths:

class Sync:

    def __init__(self, local_creds):
        """
        Class that actually executes the commands.

        Args:
        - local_creds: This is a json file which contains the following keys:
            client_secrets= This specifies the path to the client secrets.
            pickle_path= (optional?) This specifies the local path where the pickled creds will/or are stored.
        """
        CONFIG_PATH = os.path.expanduser('~/.gdrive4linux/')
        if not os.path.exists(CONFIG_PATH):
            os.mkdir(CONFIG_PATH)
        try:
            with open(local_creds) as f:
                creds = json.load(f)
                instance = auth_with_apiclient(creds['client_secrets'], creds['gdrive_scope'], pickle_path = CONFIG_PATH + '.creds.pickle')
                self.service = instance.create_service()
        except AttributeError as e:
            print("You didn't provide a valid local_creds json file")
            raise e
        except Exception as e:
            print("There was an error")
            raise e

if __name__ == '__main__':
    instance = Sync('.local_path')
    print(dir(instance))
