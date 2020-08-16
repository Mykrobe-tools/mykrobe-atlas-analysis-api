import os
from collections import OrderedDict

import distance_client
from distance_client.rest import ApiException
from distance_client.configuration import Configuration

NUM_API_CLIENT_THREADS = 10

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_DISTANCE_API", "http://distance-api-service/")
api_client = distance_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
samples_get_ids_api_instance = distance_client.SamplesGetIdsApi(api_client)
neighbours_get_api_instance = distance_client.NeighboursGetApi(api_client)


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
            neighbours = neighbours_get_api_instance.samples_id_nearest_neighbours_get(sample_id)
        except ApiException:
            neighbours = []
        if sort:
            neighbours = _sort_and_filter_distance_results(neighbours, max_distance, limit)
        sample_ids = [neighbour.experiment_id for neighbour in neighbours]
        sample_ids.append(sample_id)
        try:
            samples = samples_get_ids_api_instance.samples_get(ids=sample_ids)
        except ApiException:
            samples = []

        if not samples:
            return {}

        leaves = {s.experiment_id: s.nearest_leaf_node.leaf_id for s in samples}
        nearest_neighbours = [{
            'sampleId': neighbour.experiment_id,
            'leafId': leaves[neighbour.experiment_id],
            'distance': neighbour.distance
        } for neighbour in neighbours]

        results = {
            'type': 'distance',
            'leafId': leaves[sample_id],
            'result': nearest_neighbours
        }
        return results
