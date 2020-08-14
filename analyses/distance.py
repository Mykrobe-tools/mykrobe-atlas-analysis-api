import os
from collections import OrderedDict

import distance_client
from distance_client.rest import ApiException
from distance_client.configuration import Configuration

NUM_API_CLIENT_THREADS = 10

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_DISTANCE_API", "http://0.0.0.0:8080/api/v1")
api_client = distance_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
neighbours_get_api_instance = distance_client.NeighboursGetApi(api_client)
leaf_get_api_instance = distance_client.LeafGetApi(api_client)


def _sort_and_filter_distance_results(results, max_distance, limit):
    if max_distance is not None:
        results = [r for r in results if r.distance <= max_distance]
    results.sort(key=lambda x: x.distance)
    if limit is not None:
        results = results[:limit]
    return results


class DistanceTaskManager:
    @classmethod
    def get_all(
            cls, sample_id, max_distance=None, limit=None, sort=True
    ):
        return DistanceTaskManager.get_nearest_neighbours(sample_id, max_distance, limit, sort)

    @classmethod
    def get_nearest_leaf(cls, sample_id):
        try:
            results = leaf_get_api_instance.samples_id_nearest_leaf_node_get(sample_id)
        except ApiException:
            results = []
        return OrderedDict({r.leaf_id: r.distance for r in results})

    @classmethod
    def get_nearest_neighbours(
            cls, sample_id, max_distance=None, limit=None, sort=True
    ):
        if limit is not None:
            sort = True
        try:
            results = neighbours_get_api_instance.samples_id_nearest_neighbours_get(sample_id)
        except ApiException:
            results = []
        if sort:
            results = _sort_and_filter_distance_results(results, max_distance, limit)
        distances = OrderedDict({r.sample_id: r.distance for r in results})
        return distances
