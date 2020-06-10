from collections import OrderedDict
from itertools import cycle, tee
from operator import itemgetter
from unittest.mock import patch
from hypothesis import assume, given, strategies as st

from analyses.distance import DistanceTaskManager
from distance_client.models import Neighbour, NearestLeaf
from distance_client import ApiException


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)))
def test_get_nearest_neighbours(sample_name_suffixes, distances):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    assume(sample_input_size == 0 or distance_input_size > 0)

    with patch('analyses.distance.api_instance.samples_id_nearest_neighbours_get') as mock_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]

        expected_data = {"s"+str(s): d for s, d in zip(samples_iter2, cycle(distances_iter2))}
        expected = OrderedDict(sorted(expected_data.items(), key=itemgetter(1)))

        actual = DistanceTaskManager.get_nearest_neighbours('query sample')

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       limit=st.integers(min_value=1, max_value=10),
       sort=st.one_of(st.none(), st.booleans()))
def test_get_nearest_neighbours_with_limit(sample_name_suffixes, distances, limit, sort):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    assume(sample_input_size == 0 or distance_input_size > 0)
    print(sort)
    with patch('analyses.distance.api_instance.samples_id_nearest_neighbours_get') as mock_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]

        expected_data = {"s"+str(s): d for s, d in zip(samples_iter2, cycle(distances_iter2))}
        expected = OrderedDict(sorted(expected_data.items(), key=itemgetter(1))[:limit])

        actual = DistanceTaskManager.get_nearest_neighbours('query sample', limit=limit, sort=sort)

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       max_distance=st.integers(min_value=0, max_value=10))
def test_get_nearest_neighbours_with_max_distance(sample_name_suffixes, distances, max_distance):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    assume(sample_input_size == 0 or distance_input_size > 0)

    with patch('analyses.distance.api_instance.samples_id_nearest_neighbours_get') as mock_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]

        expected_data = {"s"+str(s): d for s, d in zip(samples_iter2, cycle(distances_iter2)) if d <= max_distance}
        expected = OrderedDict(sorted(expected_data.items(), key=itemgetter(1)))

        actual = DistanceTaskManager.get_nearest_neighbours('query sample', max_distance=max_distance)

        assert actual == expected


@given(sample_name_suffixes=st.sets(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=100)),
       distances=st.lists(min_size=0, max_size=10, elements=st.integers(min_value=0, max_value=10)),
       sort=st.booleans())
def test_get_nearest_neighbours_with_sort(sample_name_suffixes, distances, sort):
    sample_input_size = len(sample_name_suffixes)
    distance_input_size = len(distances)
    assume(sample_input_size == 0 or distance_input_size > 0)

    with patch('analyses.distance.api_instance.samples_id_nearest_neighbours_get') as mock_get:
        samples_iter1, samples_iter2 = tee(sample_name_suffixes)
        distances_iter1, distances_iter2 = tee(distances)
        mock_get.return_value = [Neighbour("s"+str(s), d) for s, d in zip(samples_iter1, cycle(distances_iter1))]

        expected_data = {"s"+str(s): d for s, d in zip(samples_iter2, cycle(distances_iter2))}
        if sort:
            expected_data = sorted(expected_data.items(), key=itemgetter(1))
        expected = OrderedDict(expected_data)

        actual = DistanceTaskManager.get_nearest_neighbours('query sample', sort=sort)

        assert actual == expected


def test_get_nearest_neighbours_handle_api_exception():
    with patch('analyses.distance.api_instance.samples_id_nearest_neighbours_get', side_effect=ApiException):
        expected = OrderedDict({})

        actual = DistanceTaskManager.get_nearest_neighbours('query sample')

        assert actual == expected


@given(leaf_name_suffix=st.integers(), distance=st.integers(min_value=0, max_value=10))
def test_get_nearest_leaf(leaf_name_suffix, distance):
    with patch('analyses.distance.api_instance.samples_id_nearest_leaf_node_get') as mock_get:
        mock_get.return_value = [NearestLeaf("l"+str(leaf_name_suffix), distance)]

        expected = OrderedDict({"l"+str(leaf_name_suffix): distance})

        actual = DistanceTaskManager.get_nearest_leaf('query sample')

        assert actual == expected


def test_get_nearest_leaf_handle_api_exception():
    with patch('analyses.distance.api_instance.samples_id_nearest_leaf_node_get', side_effect=ApiException):
        expected = OrderedDict({})

        actual = DistanceTaskManager.get_nearest_leaf('query sample')

        assert actual == expected
