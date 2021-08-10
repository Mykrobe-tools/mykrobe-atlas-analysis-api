import ast
import os
import logging
from bsddb3 import db
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

logger = logging.getLogger(__name__)

DB_KEY_PREFIX_NEIGHBOURS = "n"
DB_KEY_PREFIX_DISTANCES = "d"
CLUSTER_DB_PATH = os.environ.get("CLUSTER_DB_PATH", "/database/cluster_cache.berkeleydb")


def _convert_key_to_bytes(key):
    return key.encode("utf-8")


def _query_db(berkeley_db_file, sample_id):
    storage = db.DB()
    storage.open(berkeley_db_file, None, db.DB_HASH, db.DB_CREATE)
    neighbours = storage[_convert_key_to_bytes(DB_KEY_PREFIX_NEIGHBOURS + sample_id)].decode("utf-8")
    distances = storage[_convert_key_to_bytes(DB_KEY_PREFIX_DISTANCES + sample_id)].decode("utf-8")
    storage.close()
    return neighbours, distances


def _extract_minimum_spanning_tree(samples, mst):
    num_samples = len(samples)
    matrix = mst.toarray()

    # first iteration looks at the 0-distance samples and group them
    grouped_sets = []
    for row in range(num_samples - 1):
        for col in range(row + 1, num_samples):
            if matrix[row][col] == 1:
                row_in_set = -1
                col_in_set = -1
                for index, s in enumerate(grouped_sets):
                    if samples[row] in s:
                        row_in_set = index
                    if samples[col] in s:
                        col_in_set = index
                if row_in_set == -1 and col_in_set == -1:
                    grouped_sets.append({samples[row], samples[col]})
                elif row_in_set >= 0 and col_in_set >= 0:
                    if row_in_set != col_in_set:
                        grouped_sets.append(grouped_sets[row_in_set].union(grouped_sets[col_in_set]))
                        if row_in_set > col_in_set:
                            grouped_sets.pop(row_in_set)
                            grouped_sets.pop(col_in_set)
                        else:
                            grouped_sets.pop(col_in_set)
                            grouped_sets.pop(row_in_set)
                elif row_in_set >= 0:
                    grouped_sets[row_in_set].add(samples[col])
                else:
                    grouped_sets[col_in_set].add(samples[row])
                matrix[row][col] = 0

    # second iteration connects those grouped sets and other singletons
    nodes = []
    relationships = []
    sample_to_node_id = {}
    for index, grouped_samples in enumerate(grouped_sets):
        nodes.append({
            "id": index,
            "samples": list(grouped_samples)
        })
        for sample in grouped_samples:
            sample_to_node_id[sample] = index
    node_count = len(nodes)
    for row in range(num_samples - 1):
        for col in range(row + 1, num_samples):
            if matrix[row][col] > 1:
                start_index = 0
                if samples[row] in sample_to_node_id:
                    start_index = sample_to_node_id[samples[row]]
                else:
                    start_index = node_count
                    node_count = node_count + 1
                    sample_to_node_id[samples[row]] = start_index
                    nodes.append({
                        "id": start_index,
                        "samples": [samples[row]]
                    })

                end_index = 0
                if samples[col] in sample_to_node_id:
                    end_index = sample_to_node_id[samples[col]]
                else:
                    end_index = node_count
                    node_count = node_count + 1
                    sample_to_node_id[samples[col]] = end_index
                    nodes.append({
                        "id": end_index,
                        "samples": [samples[col]]
                    })

                relationships.append({
                    "start": start_index,
                    "end": end_index,
                    "distance": int(matrix[row][col] - 1)
                })
    return {
        "nodes": nodes,
        "distance": relationships
    }


def _query_for_mst(sample_id, berkeley_db_file):
    try:
        neighbours, distances = _query_db(berkeley_db_file, sample_id)
    except:
        return {}
    samples = neighbours.split(',')
    num_samples = len(samples)
    input_matrix = csr_matrix(
        np.frombuffer(ast.literal_eval(distances), dtype=np.uint8).reshape(num_samples, num_samples))
    mst = minimum_spanning_tree(input_matrix)
    tree = _extract_minimum_spanning_tree(samples, mst)
    return tree


class ClusterTaskManager:
    @classmethod
    def get_cluster(cls, sample_id, max_distance=None):
        tree = _query_for_mst(sample_id, CLUSTER_DB_PATH)
        if not tree:
            return {
                'type': 'cluster',
                'status': 'error',
                'result': []
            }
        results = {
            'type': 'cluster',
            'result': tree
        }
        return results

    @classmethod
    def build_cluster(cls, sample_id, nearest_neighbours, callback_url):
        logger.debug('Building cluster for %s', sample_id)

        # first prepare the distance matrix for new sample's neighbours
        neighbours_of_new_sample = [sample_id] + list(nearest_neighbours)
        num_neighbours_of_new_sample = len(neighbours_of_new_sample)
        neighbours_of_new_sample_index_map = {}
        for index, neighbour_of_new_sample in enumerate(neighbours_of_new_sample):
            neighbours_of_new_sample_index_map[neighbour_of_new_sample] = index
        distance_matrix_of_new_sample = np.zeros((num_neighbours_of_new_sample, num_neighbours_of_new_sample), dtype=np.uint8)
        for neighbour_of_new_sample in nearest_neighbours:
            # fill in the distances between new sample and its neighbours first
            distance_matrix_of_new_sample[0][neighbours_of_new_sample_index_map[neighbour_of_new_sample]] = nearest_neighbours[neighbour_of_new_sample] + 1

        storage = db.DB()
        storage.open(CLUSTER_DB_PATH, None, db.DB_HASH, db.DB_CREATE)

        # second update all neighbours with this new sample
        for the_neighbour in nearest_neighbours:
            neighbours_of_the_neighbour = ''
            distances_of_the_neighbour = ''
            try:
                neighbours_of_the_neighbour, distances_of_the_neighbour = _query_db(CLUSTER_DB_PATH, the_neighbour)
            except:
                pass
            if not neighbours_of_the_neighbour or not distances_of_the_neighbour:
                continue
            old_neighbours = neighbours_of_the_neighbour.split(',')
            num_old_neighbours = len(old_neighbours)
            old_distance_matrix = np.frombuffer(ast.literal_eval(distances_of_the_neighbour), dtype=np.uint8).reshape(num_old_neighbours, num_old_neighbours)
            new_neighbours = old_neighbours + [sample_id]
            num_new_neighbours = len(new_neighbours)
            new_distance_matrix = np.zeros((num_new_neighbours, num_new_neighbours), dtype=np.uint8)
            # copy from old matrix
            for row in range(num_old_neighbours-1):
                for col in range(row, num_old_neighbours):
                    new_distance_matrix[row][col] = old_distance_matrix[row][col]
            # fill last column for distances with new sample
            for row, old_neighbour in enumerate(old_neighbours):
                if old_neighbour in nearest_neighbours:
                    new_distance_matrix[row][num_new_neighbours-1] = nearest_neighbours[old_neighbour] + 1
            # update records
            storage[_convert_key_to_bytes(DB_KEY_PREFIX_NEIGHBOURS + the_neighbour)] = ','.join(new_neighbours).encode("utf-8")
            storage[_convert_key_to_bytes(DB_KEY_PREFIX_DISTANCES + the_neighbour)] = new_distance_matrix.tostring()

            # third update the new sample's distance matrix with the distances between one of its neighbours and another
            the_neighbour_index_in_old_neighbours = old_neighbours.index(the_neighbour)
            the_neighbour_index_in_neighbours_of_new_sample = neighbours_of_new_sample_index_map[the_neighbour]
            for old_neighbour_index_in_old_neighbours, old_neighbour in enumerate(old_neighbours):
                if old_neighbour in neighbours_of_new_sample_index_map:
                    old_neighbour_index_in_neighbours_of_new_sample = neighbours_of_new_sample_index_map[old_neighbour]
                    if the_neighbour_index_in_neighbours_of_new_sample < old_neighbour_index_in_neighbours_of_new_sample:
                        if the_neighbour_index_in_old_neighbours < old_neighbour_index_in_old_neighbours:
                            distance_matrix_of_new_sample[the_neighbour_index_in_neighbours_of_new_sample][old_neighbour_index_in_neighbours_of_new_sample] = old_distance_matrix[the_neighbour_index_in_old_neighbours][old_neighbour_index_in_old_neighbours]
                        else:
                            distance_matrix_of_new_sample[the_neighbour_index_in_neighbours_of_new_sample][old_neighbour_index_in_neighbours_of_new_sample] = old_distance_matrix[old_neighbour_index_in_old_neighbours][the_neighbour_index_in_old_neighbours]

        # fourth store the records for the new sample
        storage[_convert_key_to_bytes(DB_KEY_PREFIX_NEIGHBOURS + sample_id)] = ','.join(neighbours_of_new_sample).encode("utf-8")
        storage[_convert_key_to_bytes(DB_KEY_PREFIX_DISTANCES + sample_id)] = distance_matrix_of_new_sample.tostring()

        storage.sync()
        storage.close()

        logger.debug('Updating Atlas API with new cluster results')
        cls._update_atlas_api_with_new_cluster_results(sample_id, callback_url)

    @classmethod
    def _update_atlas_api_with_new_cluster_results(cls, sample_id, callback_url):
        from app import cluster_query_task # TODO: refactor this to remove cyclic dependency
        cluster_query_task.delay(sample_id, callback_url)