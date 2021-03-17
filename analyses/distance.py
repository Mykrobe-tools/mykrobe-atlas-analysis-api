import os
import pickle
import distance_client
import redis
import logging
import time

from analyses.tracking import record_event, EventName
from distance_client.rest import ApiException
from distance_client.configuration import Configuration
from bitarray import bitarray

logger = logging.getLogger(__name__)

NUM_API_CLIENT_THREADS = 10
KMER_SIZE = 31
BLOOMFILTER_SIZE = 28000000
KEY_EXPIRES_IN = 300
NEAREST_NEIGHBOUR_DISTANCE_THRESHOLD = 10
GENOTYPE_KEY = "genotype"
GENOTYPE_TREE_LEAVE_KEY = "genotype-tree-leaves"
GENOTYPE_SAMPLES_KEY = "genotype-samples"
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=4)

configuration = Configuration()
configuration.host = os.environ.get("ATLAS_DISTANCE_API", "http://distance-api-service/api/v1")
api_client = distance_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
samples_get_api_instance = distance_client.SamplesGetApi(api_client)
samples_post_api_instance = distance_client.SamplesPostApi(api_client)


def _sort_and_filter_distance_results(results, max_distance, limit):
    if max_distance is not None:
        results = [r for r in results if r.distance <= max_distance]
    results.sort(key=lambda x: x.distance)
    if limit is not None:
        results = results[:limit]
    return results


def _match_kmers(bloomfilters, kmers_hashes):
    for index in kmers_hashes:
        if bloomfilters[index] == 0:
            return False
    return True


def _genoypte_single_site(bloomfilters, kmers_hashes):
    genotype_code = 0
    if _match_kmers(bloomfilters, kmers_hashes[0:KMER_SIZE]):
        genotype_code += 1
    if _match_kmers(bloomfilters, kmers_hashes[KMER_SIZE:]):
        genotype_code += 2
    if genotype_code == 3:
        return 0
    return genotype_code


def _genotype_with_bloomfilter_and_probes(bloomfilters, probes_hashes):
    num_of_probes = int(len(probes_hashes) / (KMER_SIZE * 2))
    genotypes = [0] * num_of_probes
    for index in range(num_of_probes):
        genotypes[index] = _genoypte_single_site(bloomfilters, probes_hashes[index*KMER_SIZE*2 : (index+1)*KMER_SIZE*2])
    return genotypes


def _get_homozygous_genotype_key(sample_name):
    return f"{GENOTYPE_KEY}-homozygous-{sample_name}"


def _get_alternate_genotype_key(sample_name):
    return f"{GENOTYPE_KEY}-alternate-{sample_name}"


def _insert_genotypes_to_redis(sample_name, genotypes):
    # store every sample's genotype calls as two bitarrays in redis
    # first one is whether the call is homozygous
    # second one is whether the call is hom alternate
    num_calls = len(genotypes)
    homozygous = bitarray(num_calls)
    homozygous.setall(0)
    alternate = bitarray(num_calls)
    alternate.setall(0)
    for index, genotype_call in enumerate(genotypes):
        if genotype_call == "1":
            homozygous[index] = 1
        if genotype_call == "2":
            homozygous[index] = 1
            alternate[index] = 1
    print(homozygous)
    print(alternate)
    key1 = f"{GENOTYPE_KEY}-homozygous-{sample_name}"
    key2 = f"{GENOTYPE_KEY}-alternate-{sample_name}"
    pipe = REDIS.pipeline()
    for index, bit in enumerate(homozygous):
        if bit:
            print(f"setting bit for {key1} at {index}")
            pipe.setbit(key1, index, 1)
    for index, bit in enumerate(alternate):
        if bit:
            print(f"setting bit for {key2} at {index}")
            pipe.setbit(key2, index, 1)
    pipe.sadd(GENOTYPE_SAMPLES_KEY, sample_name)
    pipe.execute()


def _decode(byte):
    return byte.decode("utf-8")


def _get_nearest_leaf(sample_name):
    primary_sample = sample_name
    secondary_samples = list(map(_decode, REDIS.smembers(GENOTYPE_TREE_LEAVE_KEY)))
    results_distance = _calculate_distance(primary_sample, secondary_samples)

    nearest_leaf = ""
    nearest_distance = 10000000
    for leaf, distance in zip(secondary_samples, results_distance):
        if distance < nearest_distance:
            nearest_leaf = leaf
            nearest_distance = distance
    return nearest_leaf, nearest_distance


def _get_nearest_neighbours(sample_name):
    primary_sample = sample_name
    secondary_samples = list(map(_decode, REDIS.smembers(GENOTYPE_SAMPLES_KEY)))
    results_distance = _calculate_distance(primary_sample, secondary_samples)

    nearest_neighbours = {}
    for neighbour, distance in zip(secondary_samples, results_distance):
        if distance <= NEAREST_NEIGHBOUR_DISTANCE_THRESHOLD and neighbour != primary_sample:
            nearest_neighbours[neighbour] = distance

    return nearest_neighbours


def _calculate_distance(primary_sample, secondary_samples):
    key1_primary_sample = f"{GENOTYPE_KEY}-homozygous-{primary_sample}"
    key2_primary_sample = f"{GENOTYPE_KEY}-alternate-{primary_sample}"
    pipe = REDIS.pipeline()
    for secondary_sample in secondary_samples:
        key1_secondary_sample = f"{GENOTYPE_KEY}-homozygous-{secondary_sample}"
        key2_secondary_sample = f"{GENOTYPE_KEY}-alternate-{secondary_sample}"
        key_step1 = f"step1-{primary_sample}-{secondary_sample}"
        key_step2 = f"step2-{primary_sample}-{secondary_sample}"
        key_step3 = f"step3-{primary_sample}-{secondary_sample}"
        pipe.bitop("and", key_step1, key1_primary_sample, key1_secondary_sample)
        pipe.bitop("xor", key_step2, key2_primary_sample, key2_secondary_sample)
        pipe.bitop("and", key_step3, key_step1, key_step2)
        pipe.expire(key_step1, KEY_EXPIRES_IN)
        pipe.expire(key_step2, KEY_EXPIRES_IN)
        pipe.expire(key_step3, KEY_EXPIRES_IN)
    pipe.execute()
    pipe = REDIS.pipeline()
    for secondary_sample in secondary_samples:
        key_step3 = f"step3-{primary_sample}-{secondary_sample}"
        pipe.bitcount(key_step3)
    results_distance = pipe.execute()
    return results_distance


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

    @classmethod
    def build_distance(cls, bloomfilter, sample_id, callback_url, kwargs):
        start_time = time.time()
        logger.debug('Building distance for %s', sample_id)
        bloom_filters = bitarray()
        with open(bloomfilter, "rb") as bf:
            bloom_filters.fromfile(bf)
        probes_hashes = pickle.load(open("/usr/src/app/data/probes.hashes.pickle", "rb"))

        logger.debug('Genotyping with bloomfilter and probes')
        genotypes = _genotype_with_bloomfilter_and_probes(bloom_filters, probes_hashes)
        print(genotypes)

        logger.debug('Inserting new sample genotypes into redis')
        _insert_genotypes_to_redis(sample_id, genotypes)

        logger.debug('Calculating nearest leaf and nearest neighbours')
        nearest_leaf, nearest_leaf_distance = _get_nearest_leaf(sample_id)
        nearest_neighbours = _get_nearest_neighbours(sample_id)

        logger.debug('Updating distance API with new sample')
        leaf_node = distance_client.NearestLeaf(nearest_leaf, nearest_leaf_distance)
        neighbours = [distance_client.Neighbour(n, d) for n, d in nearest_neighbours.items()]
        sample_to_update = distance_client.Sample(experiment_id=sample_id, nearest_leaf_node=leaf_node,
                                                  nearest_neighbours=neighbours)
        try:
            samples_post_api_instance.samples_post(sample_to_update)
        except ApiException:
            logger.debug('ApiException when updating distance API')

        logger.debug('Updating Atlas API with new distance results')
        cls._update_atlas_api_with_new_distance_results(callback_url, kwargs, sample_id)

        duration = int((time.time() - start_time) * 1000)
        record_event(sample_id, EventName.DISTANCE_CALCULATION, software='analysis-api-worker',
                     software_version='unknown', start_timestamp=start_time,
                     duration=duration, command='build_distance')

    @classmethod
    def _update_atlas_api_with_new_distance_results(cls, callback_url, kwargs, sample_id):
        from app import distance_query_task # TODO: refactor this to remove cyclic dependency
        distance_query_task.delay(sample_id, callback_url, **kwargs)
