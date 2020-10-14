import os

import tracking_client
from tracking_client.configuration import Configuration

NUM_API_CLIENT_THREADS = 10

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_TRACKING_API", "http://tracking-api-service/api/v1")
api_client = tracking_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
qc_result_api_instance = tracking_client.QcResultApi(api_client)
