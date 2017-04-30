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

### NEW SERVE_HTML

    #def serve_html(self, use_nonce=False):
    def catch_response(self):
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
                print('there was a mathch with code, and it is: ', code)
            else:
                print('nothing starting with "code" was found...')
        return code

### NEW SERVE_HTML

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
    For testing if this module works..
    """

    def __init__(self):
        self.wl = WebServer()
        self.port1 = self.wl._port
        print('the port is: ', self.port1)
        self.p1 = Process(target=self.wl.serve_html)
        self.conn_in, self.conn_out = Pipe()
        self.p2 = Process(target=self.request, args=(self.port1, self.conn_in,))

    def request(self, port, conn):
        s = 'http://127.0.0.1:' + str(port)
        r = requests.get(s)
        print('this is the status_code: ', r.status_code)
        conn.send(r.text)
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
                if 'INDEX.HTML FILE' in self.conn_out.recv():
                    print("PASS: Oauth.Webserver works!")
                    break
                print('this is the pipe output: ', self.conn_out.recv())
                if t.exitcode is None:
                    break
            except Exception:
                print('there was an error')
            x += 1
        print('loop finished')

if __name__ == '__main__':
    t = Testing()
    t.test()
