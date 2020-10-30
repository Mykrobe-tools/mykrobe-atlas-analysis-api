import os
import pickle
import sys

import tracking_client
from tracking_client import Configuration, SampleApi

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_TRACKING_API", "http://localhost:8080/api/v1")
api_client = tracking_client.ApiClient(configuration=configuration)

sample_api = SampleApi(api_client)

mapping = {}

with open(sys.argv[1], 'r') as inf:
    for iid in inf:
        from_tracking_api = sample_api.samples_get(isolate_id=iid)

        if not from_tracking_api:
            mapping[iid] = iid
            continue

        mapping[iid] = from_tracking_api[0].id

print(pickle.dumps(mapping))