import sys
import os

sys.path.append("../src/api/")

import json
import redis
import operator
from collections import OrderedDict
import bitarray

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

REDIS = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=2)
SAMPLES_KEY = "samples"
INTERMEDIATE_RESULT_EXPIRY = 300


def sort_and_filter_distance_dict(d, max_distance, limit):
    sorted_d = sorted(d.items(), key=operator.itemgetter(1))
    if max_distance:
        sorted_d = [x for x in sorted_d if x[1] <= max_distance]
    if limit:
        sorted_d = sorted_d[:limit]
    return OrderedDict(sorted_d)


class DistanceTaskManager:
    def __init__(self, redis=REDIS, expiry=INTERMEDIATE_RESULT_EXPIRY):
        self.redis = redis
        self.expiry = expiry
        self.samples = self.get_samples()

    def get_samples(self):
        return {s.decode("utf-8") for s in self.redis.smembers(SAMPLES_KEY)}

    def __intermediate_key(self, s1, s2):
        return "_".join([str(s1), "xor", str(s2)])

    def __distance_result_key(self, s1, s2):
        return "_".join(["filtered", str(s1), "xor", str(s2)])

    def __genotype_bitarray_key(self, sample_id):
        return "_".join([sample_id, "genotypes"])

    def __passed_bitarray_key(self, sample_id):
        return "_".join([sample_id, "passed_filter"])

    def _build_xor(self, primary_sample, samples):
        primary_sample_key = self.__genotype_bitarray_key(primary_sample)
        pipe = self.redis.pipeline()
        print(primary_sample_key, self.redis.bitcount(primary_sample_key))
        for secondary_sample in samples:
            secondary_sample_key = self.__genotype_bitarray_key(secondary_sample)
            k = self.__intermediate_key(primary_sample, secondary_sample)
            if (
                secondary_sample != primary_sample
            ):  # and (self.redis.bitcount(secondary_sample_key) > 100) and (self.redis.bitcount(primary_sample_key) > 100)
                pipe.bitop("xor", k, primary_sample_key, secondary_sample_key)
                pipe.expire(k, self.expiry)
                ## Filter
                primary_passed_filter_key = self.__passed_bitarray_key(primary_sample)
                secondary_passed_filter_key = self.__passed_bitarray_key(
                    secondary_sample
                )
                distance_result_key = self.__distance_result_key(
                    primary_sample, secondary_sample
                )
                pipe.bitop(
                    "and",
                    distance_result_key,
                    k,
                    primary_passed_filter_key,
                    secondary_passed_filter_key,
                )
                pipe.expire(distance_result_key, self.expiry)
        pipe.execute()

    def _count_xor(self, primary_sample, samples):
        samples = [s for s in samples if s != primary_sample]
        pipe = self.redis.pipeline()
        for secondary_sample in samples:
            k = self.__distance_result_key(primary_sample, secondary_sample)
            if secondary_sample != primary_sample and self.redis.exists(k):
                pipe.bitcount(
                    self.__distance_result_key(primary_sample, secondary_sample)
                )
        res = pipe.execute()
        d = {}
        for q, diff in zip(samples, res):
            d[q] = diff
        return d

    def distance(
        self, primary_sample, max_distance=None, samples=None, limit=None, sort=True
    ):
        if samples is None:
            samples = self.get_samples()
        if limit is not None:
            sort = True
        self._build_xor(primary_sample, samples)
        distances = self._count_xor(primary_sample, samples)
        if sort:
            distances = sort_and_filter_distance_dict(distances, max_distance, limit)
        return distances

    ## Insert
    def _add_sample(self, sample_id):
        self.redis.sadd(SAMPLES_KEY, sample_id)

    def insert_from_json(json_path):
        with open(json_path, "r") as inf:
            res = json.load(inf)
        return self.insert(res)

    def insert(self, res):
        for sample_id, data in res.items():
            self._add_sample(sample_id)
            genotypes = self._create_genotype_bitarray(data["genotypes"])
            passed_filter = self._create_filtered_bitarray(data["filtered"])
            self._insert_genotype_bitarray(genotypes, sample_id=sample_id)
            self._insert_passed_bitarray(passed_filter, sample_id=sample_id)

    def _insert_genotype_bitarray(self, ba, sample_id):
        self.redis.set(self.__genotype_bitarray_key(sample_id), ba.tobytes())

    def _insert_passed_bitarray(self, ba, sample_id):
        self.redis.set(self.__passed_bitarray_key(sample_id), ba.tobytes())

    def _create_genotype_bitarray(self, sorted_calls):
        int_array = [int(call > 1) for call in sorted_calls]
        ba = bitarray.bitarray(int_array)
        return ba

    def _create_filtered_bitarray(self, int_array):
        ba = bitarray.bitarray(int_array)
        return ba
