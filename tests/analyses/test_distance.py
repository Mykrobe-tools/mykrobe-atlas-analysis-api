from collections import OrderedDict
from itertools import cycle, tee
from unittest.mock import patch
from hypothesis import assume, given, strategies as st

from analyses.distance import DistanceTaskManager
from distance_client.models import Neighbour, Sample, NearestLeaf
from distance_client import ApiException


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       leaf_node_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)))
def test_get_nearest_neighbours(sample_name_suffixes, leaf_node_suffixes, distances):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    leaf_input_size = len(leaf_node_suffixes)
    assume(sample_input_size == 0 or (distance_input_size > 0 and leaf_input_size > 0))
    query_sample = 'query sample'

    with patch('analyses.distance.samples_get_api_instance.samples_id_get') as mock_samples_id_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        nearest_neighbours = [Neighbour(experiment_id="s"+str(s), distance=d, leaf_id="l"+str(l))
                              for s, d, l in zip(samples_iter1, cycle(distances_iter1), cycle(leaves_iter1))]
        nearest_leaf_node = NearestLeaf(leaf_id="ln", distance=1)
        mock_samples_id_get.return_value = Sample(experiment_id=query_sample, nearest_leaf_node=nearest_leaf_node,
                                                  nearest_neighbours=nearest_neighbours)

        expected_neighbours = [{
            'sampleId': "s"+str(s),
            'leafId': 'l'+str(l),
            'distance': d
        } for s, l, d in zip(samples_iter2, cycle(leaves_iter2), cycle(distances_iter2))]
        expected_neighbours.sort(key=lambda x: x['distance'])
        expected = {
            'type': 'distance',
            'leafId': 'ln',
            'result': expected_neighbours
        }

        actual = DistanceTaskManager.get_nearest_neighbours(query_sample)

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       leaf_node_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       limit=st.integers(min_value=1, max_value=10),
       sort=st.one_of(st.none(), st.booleans()))
def test_get_nearest_neighbours_with_limit(sample_name_suffixes, leaf_node_suffixes, distances, limit, sort):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    leaf_input_size = len(leaf_node_suffixes)
    assume(sample_input_size == 0 or (distance_input_size > 0 and leaf_input_size > 0))
    query_sample = 'query sample'

    with patch('analyses.distance.samples_get_api_instance.samples_id_get') as mock_samples_id_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        nearest_neighbours = [Neighbour(experiment_id="s"+str(s), distance=d, leaf_id="l"+str(l))
                              for s, d, l in zip(samples_iter1, cycle(distances_iter1), cycle(leaves_iter1))]
        nearest_leaf_node = NearestLeaf(leaf_id="ln", distance=1)
        mock_samples_id_get.return_value = Sample(experiment_id=query_sample, nearest_leaf_node=nearest_leaf_node,
                                                  nearest_neighbours=nearest_neighbours)
        expected_neighbours = [{
            'sampleId': "s" + str(s),
            'leafId': 'l' + str(l),
            'distance': d
        } for s, l, d in zip(samples_iter2, cycle(leaves_iter2), cycle(distances_iter2))]
        expected_neighbours.sort(key=lambda x: x['distance'])
        expected_neighbours = expected_neighbours[:limit]
        expected = {
            'type': 'distance',
            'leafId': 'ln',
            'result': expected_neighbours
        }

        actual = DistanceTaskManager.get_nearest_neighbours(query_sample, limit=limit, sort=sort)

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       leaf_node_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       max_distance=st.integers(min_value=0, max_value=10))
def test_get_nearest_neighbours_with_max_distance(sample_name_suffixes, leaf_node_suffixes, distances, max_distance):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    leaf_input_size = len(leaf_node_suffixes)
    assume(sample_input_size == 0 or (distance_input_size > 0 and leaf_input_size > 0))
    query_sample = 'query sample'

    with patch('analyses.distance.samples_get_api_instance.samples_id_get') as mock_samples_id_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        nearest_neighbours = [Neighbour(experiment_id="s"+str(s), distance=d, leaf_id="l"+str(l))
                              for s, d, l in zip(samples_iter1, cycle(distances_iter1), cycle(leaves_iter1))]
        nearest_leaf_node = NearestLeaf(leaf_id="ln", distance=1)
        mock_samples_id_get.return_value = Sample(experiment_id=query_sample, nearest_leaf_node=nearest_leaf_node,
                                                  nearest_neighbours=nearest_neighbours)

        expected_neighbours = [{
            'sampleId': "s" + str(s),
            'leafId': 'l' + str(l),
            'distance': d
        } for s, l, d in zip(samples_iter2, cycle(leaves_iter2), cycle(distances_iter2)) if d <= max_distance]
        expected_neighbours.sort(key=lambda x: x['distance'])
        expected = {
            'type': 'distance',
            'leafId': 'ln',
            'result': expected_neighbours
        }

        actual = DistanceTaskManager.get_nearest_neighbours(query_sample, max_distance=max_distance)

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       leaf_node_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       sort=st.booleans())
def test_get_nearest_neighbours_with_sort(sample_name_suffixes, leaf_node_suffixes, distances, sort):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    leaf_input_size = len(leaf_node_suffixes)
    assume(sample_input_size == 0 or (distance_input_size > 0 and leaf_input_size > 0))
    query_sample = 'query sample'

    with patch('analyses.distance.samples_get_api_instance.samples_id_get') as mock_samples_id_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        nearest_neighbours = [Neighbour(experiment_id="s"+str(s), distance=d, leaf_id="l"+str(l))
                              for s, d, l in zip(samples_iter1, cycle(distances_iter1), cycle(leaves_iter1))]
        nearest_leaf_node = NearestLeaf(leaf_id="ln", distance=1)
        mock_samples_id_get.return_value = Sample(experiment_id=query_sample, nearest_leaf_node=nearest_leaf_node,
                                                  nearest_neighbours=nearest_neighbours)

        expected_neighbours = [{
            'sampleId': "s"+str(s),
            'leafId': 'l'+str(l),
            'distance': d
        } for s, l, d in zip(samples_iter2, cycle(leaves_iter2), cycle(distances_iter2))]
        if sort:
            expected_neighbours.sort(key=lambda x: x['distance'])
        expected = {
            'type': 'distance',
            'leafId': 'ln',
            'result': expected_neighbours
        }

        actual = DistanceTaskManager.get_nearest_neighbours(query_sample, sort=sort)

        assert actual == expected


def test_get_nearest_neighbours_handle_api_exception():
    with patch('analyses.distance.samples_get_api_instance.samples_id_get', side_effect=ApiException):
        actual = DistanceTaskManager.get_nearest_neighbours('query sample')
        assert actual == {
            "type": "distance",
            "status": "error",
            "leafId": "",
            "result": []
        }
