from keycloak import KeycloakOpenID

from config import ATLAS_AUTH_SERVER, ATLAS_AUTH_REALM


def client_authenticate(client_id, secret, server_url=ATLAS_AUTH_SERVER, realm_name=ATLAS_AUTH_REALM):
    oid = KeycloakOpenID(
        server_url=server_url,
        client_id=client_id,
        realm_name=realm_name,
        client_secret_key=secret
    )

    return oid.token(username=client_id, password=secret, grant_type=['client_credentials'])['access_token']