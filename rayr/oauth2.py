import pickle

from http.server import HTTPServer, BaseHTTPRequestHandler
from oauthlib.oauth2 import TokenExpiredError
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session


class OAuth2Service(object):
    def __init__(self, clazz):
        super(OAuth2Service, self).__init__()
        self.clazz = clazz

        try:
            with open(self.clazz.token_file, 'rb') as f:
                self.token = pickle.load(f)
        except:
            self.token = None

        self.oauth = OAuth2Session(self.clazz.client,
                                   token=self.token,
                                   redirect_uri=self.clazz.redir_url,
                                   scope=self.clazz.scope)
        if self.token is None:
            self.auth()

    def serialize(self, token):
        self.token = token
        with open(self.clazz.token_file, 'wb') as f:
            pickle.dump(token, f)

    def auth(self):
        url, state = self.oauth.authorization_url(self.clazz.autho_url,
                                                  access_type='offline')
        print('Please go to {} and authorize access.'.format(url))

        class OAuth2ResponseHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                global authorization_response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write('Authentication success'.encode('utf-8'))
                self.server.response_url = 'https://localhost' + self.path

        server = HTTPServer(('localhost', 8080), OAuth2ResponseHandler)
        server.handle_request()
        server.server_close()
        response_url = server.response_url

        token = self.oauth.fetch_token(self.clazz.token_url,
                                       authorization_response=response_url,
                                       username=self.clazz.client,
                                       password=self.clazz.secret)
        self.serialize(token)

    def request(self, execute):
        try:
            response = execute()
        except TokenExpiredError as e:
            auth = HTTPBasicAuth(self.clazz.client, self.clazz.secret)
            token = self.oauth.refresh_token(self.clazz.token_url, auth=auth)
            self.serialize(token)
            response = execute()

        if response.status_code == 401:
            self.auth()
            response = execute()
        elif response.status_code >= 400:
            raise Exception(response.status_code, response.content)

        return response

    def get(self, url, **kwargs):
        return self.request(lambda: self.oauth.get(url, **kwargs))

    def post(self, url, **kwargs):
        return self.request(lambda: self.oauth.post(url, **kwargs))

    def put(self, url, **kwargs):
        return self.request(lambda: self.oauth.put(url, **kwargs))

    def delete(self, url, **kwargs):
        return self.request(lambda: self.oauth.delete(url, **kwargs))
