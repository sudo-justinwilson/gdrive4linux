from abc import ABCMeta, abstractmethod

class OauthBase(metaclass=ABCMeta):
    """
    Abstract base class for oauth2.0 module. This base class is an attempt to make it more modular, so it can be more easily adaptable to all oauth2.0 compliant providers.
    It has an abstract method for each step of the oauth2.0 flow (for installed apps).
    The following abstract methods should be over-ridden by concrete subclasses:
        
        1) authorize():
          Ask resource owner (user) to grant permission for client (the app that is requesting to access the protected resources on behalf of the user) to access protected resource. 
            This method should handle:
            a) opening up a URL in a web browser, so that the resource owner can grant permission to the client.
            b) setting up a simple web server that can receive the authorization code, which is sent in a HTTP GET request after the resource owner grants permission.
            c) returning the authorization code so that it can be passed as a parameter to self.swap_code.

                                          web
                user            --->    browser
                                            
                                        permission granted? if yes...
                web server      <---    authorization code

                return authorization code

        2) swap_code(authorization_code):
          This method swaps the authorization code for access and refresh tokens.
            This method should handle:
            a) swapping the authorization codefor the tokens.
            b) storing the tokens in a json file at self.token_path.
            c) does not need to return a value.


                client
                [authorization
                  code]         --->    oauth server

              self.token_path   <---    tokens

        3) get_token():
            This method is called when a user wants a valid access token that can be used in restful API calls. It should also refresh the token, if necessary.
            This method should handle:
            a) Return a valid access token

        4) refresh_token(refresh_token):
          Access tokens are often valid for a finite period of time (3600 seconds with Google's Oauth2.0 implementation). When it expires, the refresh token can be used to obtain a valid token from the oauth2.0 server.
            This method should handle:
              a) Requesting a new access token from the oauth2.0 server.
              b) Updating the access_token field in the json file stored at self.token_path.
    """
    
    @abstractmethod
    def authorize(self):
        """
        Start oauth2.0 flow, so that resource owner grants permission to client.

        Return authorization_code.
        """

    @abstractmethod
    def swap_code(self, authorization_code):
        """
        Swap authorization_code for access and refresh tokens. The token should be stored in self.token.path.
        """

    @abstractmethod
    def get_token(self, token_path):
        """
        Return valid access token to user.
        """

    @abstractmethod
    def refresh_token(self, token_path):
        """
        Refreshes an expired access_token, and updates the access_token stored in a json file at self.token_path.
        """
