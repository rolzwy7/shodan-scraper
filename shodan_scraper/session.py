from requests import Request, Session
from urllib.parse import urlencode
import re

headers = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
}

data = {
    "csrf_token": "",
    "grant_type": "password",
    "continue": "https://account.shodan.io/",
    "login_submit": "Login",
}


# Takes response object from requests library
# Returns array of ip:port elements
def parse_search_query(response):
    mat = re.finditer(
        b"(?:[0-9]{1,3}\\.){3}[0-9]{1,3}(:[0-9]+){1}",
        response.content
    )
    filtered_ = list(set([str(_[0], "utf8") for _ in mat]))
    return filtered_


class ShodanSession():
    def __init__(self, username, password, verbose=False):
        self.url = "https://account.shodan.io/login"
        self.url_search = "https://www.shodan.io/search"
        self.headers = headers
        self.data = data
        self.verbose = verbose

        self.client_username = username
        self.data["username"] = username
        self.client_password = password
        self.data["password"] = password

        self.init_session()

    def init_session(self):
        # Logging in
        self.client = Session()
        self.client.headers.update(headers)

        login_get = Request('GET',  self.url, data={})
        resp = self.client.send(
               self.client.prepare_request(login_get), timeout=10)
        if self.verbose:
            print("[*] Login GET :", resp.status_code)

        csrf_token = resp.content.split(b'e="csrf_token" value="')[1]
        csrf_token = csrf_token.split(b'"')[0]
        csrf_token = str(csrf_token, "utf8")
        if self.verbose:
            print("[*] CSRF TOKEN :", csrf_token)

        data["csrf_token"] = csrf_token
        login_post = Request('POST', self.url, data=self.data)
        resp = self.client.send(
               self.client.prepare_request(login_post), timeout=10)
        if self.verbose:
            print("[*] Login POST :", resp.status_code)

    def scrape(self, query_dict, page=1):
        # Scraping
        search_query = query_dict
        search_query["page"] = page
        search_query = "%s?%s" % (self.url_search, urlencode(search_query))
        if self.verbose:
            print("[*] Scraping URL :", search_query)
        scrape = Request('GET',  search_query)
        resp = self.client.send(
               self.client.prepare_request(scrape), timeout=10)
        if self.verbose:
            print("[*] Scrape GET :", resp.status_code)
        return resp
