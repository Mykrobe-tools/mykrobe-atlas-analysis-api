from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session

from config import ATLAS_AUTH_SERVER, ATLAS_AUTH_REALM


class AtlasClient:

    def __init__(self, client_id, secret, server_url=ATLAS_AUTH_SERVER, realm_name=ATLAS_AUTH_REALM):
        self.token_url = f'{server_url}/realms/{realm_name}/protocol/openid-connect/token'
        self.secret = secret

        client = BackendApplicationClient(client_id)
        self.session = OAuth2Session(
            client=client,
            token_updater=self.set_token
        )

        self.session.token = self.session.fetch_token(self.token_url, client_secret=self.secret)

    def set_token(self, value):
        self.session.token = value

    def request(self, method, url, data=None, json=None):
        try:
            return self.session.request(method, url, data=data, json=json)
        except TokenExpiredError:
            self.session.token = self.session.fetch_token(self.token_url, client_secret=self.secret)
            return self.session.request(method, url, data=data, json=json)
