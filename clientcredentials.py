import json

class ClientCredentials:
    def __init__(self, client_file=None, scope=None, **kwargs):
        """
            This is an object to store the client id, to be identified by the Oauth2.0 server.
            
            OPTIONAL ARGS:
            - client_file=<str>     This is the path to a json file that contains the client_id and client_secret.
                                    If this arg is not used, then the client credentials must be passed as key=value pairs to kwargs.
            - scope=<str>           This is the scope of permissions requested from the Oauth2.0 server.
        """
        if scope:
            self.scope = scope
        if client_file:
            f = json.load(open(client_file))
            try:
                self.client_id = self.get_key(f, 'client_id')
                self.client_secret = self.get_key(f, 'client_secret')
            except KeyError as key:
                raise KeyError(key, ' value not found in file')
        else:
            try:
                self.client_id = kwargs['client_id']
                self.client_secret = kwargs['client_secret']
            except KeyError as key:
                print(key, ' is a required parameter.')


    def get_key(self, obj, key):
        """
        Utility method to return the value of key. I needed this because the client credentials downloaded from Google are nested under the "installed" key...


		If there is a key called 'key' in obj's keys, it will return its value, else, it will test if any of obj.keys() are dict, and look for the key there, it will recursively test each item of any nested dicts, to see if it contains the key, else return an error if the key is not found.

        EG:
            obj = {'key1' : 'val1', 'nested_dict' : 
                    {'n_key1': 'n_val1', 'n_key2' : 'n_val2'}
                    }
            ^ get_key(obj, 'n_key2')
              'n_val2'
        """
        if key in obj:
            return obj[key]
        else:
            for item in obj:
                if isinstance(obj[item], dict):
                    return self.get_key(obj[item], key)
        raise KeyError(key, ' value not found')


if __name__ == '__main__':
    f = '/home/justin/workspaces/APIs/git.json'
    c = ClientCredentials(client_file=f)
    print('client_id is: ', c.client_id)
    print('client_secret is: ', c.client_secret)

