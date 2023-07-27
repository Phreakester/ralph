from http.server import BaseHTTPRequestHandler, HTTPServer
import requests,re, base64

class http_server:
    def __init__(self,address,outer):
        def handler(*args):
            krogerAPI.GetHandler(outer,*args)
        self.server = HTTPServer(address,handler)

class krogerAPI:
  def __init__(self, secret, location_id):
    self.CLIENT_ID = 'hello-5d41402abc4b2a76b9719d911017c5921674708490345864538'
    self.CLIENT_SECRET = secret
    self.API_BASE_URL = "https://api.kroger.com/v1"
    self.OAUTH2_BASE_URL = "https://api.kroger.com/v1/connect/oauth2"
    self.PRODUCTS = "/products"
    self.location_id = location_id
    auth_bytes = bytes((self.CLIENT_ID +":"+ self.CLIENT_SECRET), 'utf-8')
    self.AUTH_HEADER = bytes("Basic ", 'utf-8') + base64.b64encode(auth_bytes)
    del(auth_bytes)
    self.token = None
    self.currentScope = None
    self.userToken = None

  def getToken(self):
    header = {
      "Content-Type" : "application/x-www-form-urlencoded",
      "Authorization" : self.AUTH_HEADER
    }
    data = "grant_type=client_credentials&scope=product.compact"
    self.currentScope = "product.compact"

    returned = requests.post(url=self.OAUTH2_BASE_URL + "/token", headers=header, data=data)
    returned.raise_for_status()
    self.token = returned.json()["access_token"]

  def getProductDetails(self, upc):
    if not self.token: self.getToken()
    param = {
      "filter.locationId" : self.location_id
    }
    header = {
      "Accept" : "application/json",
      "Authorization" : ("Bearer " + self.token)
    }

    returned = requests.get(url=self.API_BASE_URL + self.PRODUCTS + "/" + upc, headers=header, params=param)
    returned.raise_for_status()

    return returned.json()["data"]

  def getUserAuthToken(self):
        port = 8080
        server_address = ('', port)
        server = http_server(server_address, self)
        server.server.handle_request()
  class GetHandler(BaseHTTPRequestHandler):
    def __init__(self,outer,*args):
        self.outer = outer
        BaseHTTPRequestHandler.__init__(self,*args)
    def do_GET(self):
        self.send_response_only(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write('\n'.encode('utf-8'))
        result = re.search(r'callback\?code=(.+)',self.path)
        self.outer.userToken = result.group(1)
    
def putInCart(self, upc, quantity):
    if not self.userToken: self.getUserAuthToken()
    header = {
      "Content-Type" : "application/json",
      "Authorization" : "Bearer " + self.userToken
    }

    data = """{{
      "items": [
        {{
          "upc": "{0}",
          "quantity": {1}
        }}
      ]
    }}"""

    data = data.format(upc, quantity)

    returned = requests.put(url=self.API_BASE_URL + "/cart/add", headers=header, data=data)
    returned.raise_for_status()