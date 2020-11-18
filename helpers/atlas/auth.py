from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from config import ATLAS_AUTH_SERVER, ATLAS_AUTH_REALM


class AuthClient:

    def __init__(self, client_id, secret, server_url=ATLAS_AUTH_SERVER, realm_name=ATLAS_AUTH_REALM):
        self.token_url = f'{server_url}/realms/{realm_name}/protocol/openid-connect/token'
        self.secret = secret

        client = BackendApplicationClient(client_id)
        self.oauth = OAuth2Session(
            client=client,
            auto_refresh_url=token_url,
            auto_refresh_kwargs={
                'client_id': client_id,
                'client_secret': secret,
            },
            token_updater=self.update_token
        )

    def authenticate(self):
        token = self.oauth.fetch_token(self.token_url, client_secret=self.secret)
        self.update_token(token)

    def update_token(self, token):
        self.oauth.token = token
