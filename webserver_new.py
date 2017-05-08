import http
import string
import random
import socketserver
import requests
import time
import urllib

from multiprocessing import Process, Pipe
from http.server import SimpleHTTPRequestHandler

class WebServer:
    """
    The source for the SimpleHTTPRequestHandler is at:
        /usr/lib/python3.5/http/server.py
    The source for the socketserver module is at:
        /usr/lib/python3.5/socketserver.py
    """
    def __init__(self, handler=None, port=None):
        if port:
            self._port = port
        else:
            self._port = int(random.uniform(3000, 4000))
        self.redirect_uri = 'http://127.0.0.1:' + str(self._port)
        if handler:
            self.handler = handler
        else:
            self.handler = Handler
        self.auth_code = None
        self.nonce = self._Nonce()
        # for testing:
        self._nonce_sent = False
        self.path = None

    # method to generate nonce:
    def _Nonce(self, size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def catch_response(self):
        """
        A method that intercepts the path component (which is where the auth_code is stored to exchange for an access token) of an HTTP GET request.
        """
        PORT = self._port
        httpd = socketserver.TCPServer(("", PORT), self.handler)
        httpd.handle_request()
        self.path = Handler.path
        print('self.path has been set to: ', self.path)
        print('setting the code to None')
        code = None
        print('the code after setting it to None is: ', code)
        response = urllib.parse.urlparse(self.path)
        print('this is the response to be parsed: ', response)
        print('this is response.query, that is to be split: ', response.query)
        for element in response.query.split(sep='&'):
            print('entered "for element." loop...')
            if element.startswith('code'):
                code = element.split(sep='=')[1] 
                print('there was a match with code, and it is: ', code)
                break
            else:
                print('nothing starting with "code" was found...')
        return code

class Handler(SimpleHTTPRequestHandler):
    path = ''
    def set_path(data):
        Handler.path = data

    def get_path():
        return Handler.path

    def do_GET(self):
        Handler.path = self.path
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        print('Handler.path is: ', Handler.path)


class Testing:
    """
    This test class tests that the following operations work:
        - create a webserver that listens on a random port.
        - the webserver should intercept the "path" component of a received HTTP GET request, and return it.
    The way this object performs the test is by creating a listening webserver on one thread, and creating a requests object that sends an http get request, on a second concurrent thread.
    So if the webserver returns the url requested in the get request as a string, the webserver class works, else it doesn't...
    """

    def __init__(self, params = None):
        self.params = params
        self.test_webserver = WebServer()
        self.port1 = self.test_webserver._port
        print('the port is: ', self.port1)
        # a pipe has an "IN" end, and an "OUT" end:
        self.conn_in, self.conn_out = Pipe()
        # create a test webserver that to parse HTTP GET request, as the first concurrent process:
        #self.p1 = Process(target=self.test_webserver.catch_response)
        self.p1 = Process(target=self.catch_code, args=(self.conn_out,))
        # call self.request, with the port and conn_in as args, as the second concurrent process:
        if params:
            self.p2 = Process(target=self.request, args=(self.port1, self.conn_in, self.params) )
        else:
            self.p2 = Process(target=self.request, args=(self.port1, self.conn_in) )

    def catch_code(self, conn):
        """
        Test if the params sent to test_webserver match the code returned.
        """
        server = self.test_webserver
        # store the would-be code:
        code = self.test_webserver.catch_response()
        # send the would-be code to the pipe:
        conn.send(code)

    def request(self, port, conn, PARAMS):
        """
        Send a get request to the test webserver.
        PARAMS (dict) = key, values to be used in the request string
        """
        test_target_url = 'http://127.0.0.1:' + str(port)
        if not PARAMS:
            r = requests.get(test_target_url)
        else:
            r = requests.get(test_target_url, params = PARAMS)
        print('this is the status_code: ', r.status_code)
        #conn.send(r.text)
        conn.send(r.status_code)
        if r.status_code == 200:
            return True
        else:
            return False

    def test(self):
        self.p1.start()
        x = 0
        while x < 3:
            try:
                print('in loop ', x)
                time.sleep(3)
                self.p2.start()
                self.p2.join()
                print('p2 has started')
                #if 'INDEX.HTML FILE' in self.conn_out.recv():
                #if 'INDEX.HTML FILE' in self.conn_out.recv():
                if self.conn_out.recv() == 200:
                    print("PASS: Oauth.Webserver works!")
                    self.p1.terminate()
                    #print('this is the pipe output: ', self.conn_out.recv())
                    code_returned = self.conn_in.recv()
                    #print('the code returned from self.conn_in.recv() is: ', code_returned)
                    #break
                    return code_returned
                if t.exitcode is None:
                    break
            except Exception:
                print('there was an error')
            x += 1
        print('loop finished')

if __name__ == '__main__':
    param_sent = { 'code' : 'THIS_IS_THE_PARAMS_SENT_FROM_Testing_CLASS' }
    print('the param sent was: ', param_sent)
    t1 = Testing(params = param_sent)
    param_received = t1.test()
    print('the param received was: ', param_received)
    if param_received == param_sent['code']:
        print('everything works!')
        # TODO: create a main() method from above code.
