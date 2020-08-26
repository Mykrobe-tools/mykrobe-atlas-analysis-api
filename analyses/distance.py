import os

import distance_client
from distance_client.rest import ApiException
from distance_client.configuration import Configuration

NUM_API_CLIENT_THREADS = 10

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_DISTANCE_API", "http://distance-api-service/api/v1")
api_client = distance_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
samples_get_api_instance = distance_client.SamplesGetApi(api_client)


def _sort_and_filter_distance_results(results, max_distance, limit):
    if max_distance is not None:
        results = [r for r in results if r.distance <= max_distance]
    results.sort(key=lambda x: x.distance)
    if limit is not None:
        results = results[:limit]
    return results


class DistanceTaskManager:
    @classmethod
    def get_nearest_neighbours(
            cls, sample_id, max_distance=None, limit=None, sort=True
    ):
        if limit is not None:
            sort = True
        try:
            sample = samples_get_api_instance.samples_id_get(sample_id)
        except ApiException:
            sample = None

        if not sample:
            return {
                "type": "distance",
                "status": "error",
                "leafId": "",
                "result": []
            }

        neighbours = sample.nearest_neighbours
        if sort:
            neighbours = _sort_and_filter_distance_results(neighbours, max_distance, limit)

        nearest_neighbours = [{
            'sampleId': neighbour.experiment_id,
            'leafId': neighbour.leaf_id,
            'distance': neighbour.distance
        } for neighbour in neighbours]

        results = {
            'type': 'distance',
            'leafId': sample.nearest_leaf_node.leaf_id,
            'result': nearest_neighbours
        }
        return results
