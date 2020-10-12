import sys
import os

sys.path.append("../src/api/")
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

REDIS = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=3)
MAPPINGS_HKEY = "mappings"


def decode_dict(d):
    dd = {}
    for i, j in d.items():
        dd[i.decode("utf-8")] = j.decode("utf-8")
    return dd


class MappingsManager:
    def __init__(self, redis=REDIS, hkey=MAPPINGS_HKEY):
        self.hkey = hkey
        self.rhkey = "reverse" + self.hkey
        self.redis = redis

    def create_mapping(self, sample_id, isolate_id):
        self.redis.hset(self.hkey, sample_id, isolate_id)
        self.redis.hset(self.rhkey, isolate_id, sample_id)

    def experiment_ids_to_isolate_ids(self):
        return decode_dict(self.redis.hgetall(self.hkey))

    def isolate_ids_to_experiment_ids(self):
        return decode_dict(self.redis.hgetall(self.rhkey))

    def isolate_id_to_experiment_id(self, isolate_id):
        return self.redis.hget(self.rhkey, isolate_id).decode("utf-8")

    def experiment_id_to_isolate_id(self, experiment_id_to_isolate_id):
        return self.redis.hget(self.hkey, experiment_id_to_isolate_id).decode("utf-8")
