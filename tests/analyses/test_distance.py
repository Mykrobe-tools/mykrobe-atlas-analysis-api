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

    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get') as mock_neighbours_get, \
            patch('analyses.distance.samples_get_ids_api_instance.samples_get') as mock_samples_get:
        samples_iter1, samples_iter2, samples_iter3 = tee(sample_name_suffixes, 3)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_neighbours_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]
        mock_samples_get.return_value = [Sample(experiment_id="s"+str(s), nearest_leaf_node=NearestLeaf("l"+str(l), 0))
                                         for s, l in zip(samples_iter2, cycle(leaves_iter1))]
        mock_samples_get.return_value.append(Sample(experiment_id=query_sample, nearest_leaf_node=NearestLeaf('ln', 0)))

        expected_neighbours = [{
            'sampleId': "s"+str(s),
            'leafId': 'l'+str(l),
            'distance': d
        } for s, l, d in zip(samples_iter3, cycle(leaves_iter2), cycle(distances_iter2))]
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

    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get') as mock_neighbours_get, \
            patch('analyses.distance.samples_get_ids_api_instance.samples_get') as mock_samples_get:
        samples_iter1, samples_iter2, samples_iter3 = tee(sample_name_suffixes, 3)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_neighbours_get.return_value = [Neighbour("s" + str(s), d) for s, d in
                                            zip(samples_iter1, cycle(distances_iter1))]
        mock_samples_get.return_value = [
            Sample(experiment_id="s" + str(s), nearest_leaf_node=NearestLeaf("l" + str(l), 0))
            for s, l in zip(samples_iter2, cycle(leaves_iter1))]
        mock_samples_get.return_value.append(Sample(experiment_id=query_sample, nearest_leaf_node=NearestLeaf('ln', 0)))

        expected_neighbours = [{
            'sampleId': "s" + str(s),
            'leafId': 'l' + str(l),
            'distance': d
        } for s, l, d in zip(samples_iter3, cycle(leaves_iter2), cycle(distances_iter2))]
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

    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get') as mock_neighbours_get, \
            patch('analyses.distance.samples_get_ids_api_instance.samples_get') as mock_samples_get:
        samples_iter1, samples_iter2, samples_iter3 = tee(sample_name_suffixes, 3)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_neighbours_get.return_value = [Neighbour("s" + str(s), d) for s, d in
                                            zip(samples_iter1, cycle(distances_iter1))]
        mock_samples_get.return_value = [
            Sample(experiment_id="s" + str(s), nearest_leaf_node=NearestLeaf("l" + str(l), 0))
            for s, l in zip(samples_iter2, cycle(leaves_iter1))]
        mock_samples_get.return_value.append(Sample(experiment_id=query_sample, nearest_leaf_node=NearestLeaf('ln', 0)))

        expected_neighbours = [{
            'sampleId': "s" + str(s),
            'leafId': 'l' + str(l),
            'distance': d
        } for s, l, d in zip(samples_iter3, cycle(leaves_iter2), cycle(distances_iter2)) if d <= max_distance]
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

    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get') as mock_neighbours_get, \
            patch('analyses.distance.samples_get_ids_api_instance.samples_get') as mock_samples_get:
        samples_iter1, samples_iter2, samples_iter3 = tee(sample_name_suffixes, 3)
        leaves_iter1, leaves_iter2 = tee(leaf_node_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_neighbours_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]
        mock_samples_get.return_value = [Sample(experiment_id="s"+str(s), nearest_leaf_node=NearestLeaf("l"+str(l), 0))
                                         for s, l in zip(samples_iter2, cycle(leaves_iter1))]
        mock_samples_get.return_value.append(Sample(experiment_id=query_sample, nearest_leaf_node=NearestLeaf('ln', 0)))

        expected_neighbours = [{
            'sampleId': "s"+str(s),
            'leafId': 'l'+str(l),
            'distance': d
        } for s, l, d in zip(samples_iter3, cycle(leaves_iter2), cycle(distances_iter2))]
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
    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get', side_effect=ApiException),\
         patch('analyses.distance.samples_get_ids_api_instance.samples_get', side_effect=ApiException):
        actual = DistanceTaskManager.get_nearest_neighbours('query sample')
        assert actual == {}
    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get') as mock,\
         patch('analyses.distance.samples_get_ids_api_instance.samples_get', side_effect=ApiException):
        mock.return_value = [Neighbour("s1", 0)]
        actual = DistanceTaskManager.get_nearest_neighbours('query sample')
        assert actual == {}
    with patch('analyses.distance.neighbours_get_api_instance.samples_id_nearest_neighbours_get', side_effect=ApiException),\
         patch('analyses.distance.samples_get_ids_api_instance.samples_get') as mock:
        mock.return_value = [Sample(experiment_id="query sample", nearest_leaf_node=NearestLeaf("l1", 2))]
        actual = DistanceTaskManager.get_nearest_neighbours('query sample')
        assert actual == {
            'type': 'distance',
            'leafId': 'l1',
            'result': []
        }
