import os
from flask import Flask
from flask import request
from Bio import Phylo

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
## Celery setup
from analyses import PredictorTaskManager
from analyses import BigsiTaskManager
from analyses import DistanceTaskManager
from analyses import MappingsManager

from celery import Celery


REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://%s:6379" % REDIS_HOST)
DEFAULT_OUTDIR = os.environ.get("DEFAULT_OUTDIR", "./")
ATLAS_API = os.environ.get("ATLAS_API", "https://api-dev.mykro.be")
TB_TREE_PATH_V1 = os.environ.get("TB_TREE_PATH_V1", "data/tb_newick.txt")
MAPPER = MappingsManager()
BIGSI_URL = os.environ.get("BIGSI_URL", "mykrobe-atlas-bigsi-aggregator-api-service/api/v1")
BIGSI_BUILD_URL = os.environ.get("BIGSI_BUILD_URL", "http://bigsi-api-service-small")
BIGSI_BUILD_CONFIG = os.environ.get("BIGSI_BUILD_CONFIG", "/etc/bigsi/conf/config.yaml")
REFERENCE_FILEPATH = os.environ.get("REFERENCE_FILEPATH", "/data/NC_000962.3.fasta")
GENBANK_FILEPATH = os.environ.get("GENBANK_FILEPATH", "/data/NC_000962.3.gb")


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=CELERY_BROKER_URL, CELERY_RESULT_BACKEND=CELERY_BROKER_URL
)
celery = make_celery(app)


import json
import requests
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def send_results(type, results, url, sub_type=None, request_type="POST"):
    ## POST /isolates/:id/result { type: "…", result: { … } }
    d = {"type": type, "result": results}
    if sub_type:
        d["subType"] = sub_type
    if request_type == "PUT":
        r = requests.put(url, json=d)
    else:
        r = requests.post(url, json=d)


## Analysis


@celery.task()
def bigsi_build_task(file, sample_id):
    bigsi_tm = BigsiTaskManager(BIGSI_URL, REFERENCE_FILEPATH, GENBANK_FILEPATH, DEFAULT_OUTDIR, BIGSI_BUILD_URL, BIGSI_BUILD_CONFIG)
    bigsi_tm.build_bigsi(file, sample_id)


@celery.task()
def predictor_task(file, sample_id, callback_url):
    results = PredictorTaskManager(DEFAULT_OUTDIR).run_predictor(file, sample_id)
    url = os.path.join(ATLAS_API, callback_url)
    send_results("predictor", results, url)


@celery.task()
def genotype_task(file, sample_id, callback_url):
    results = PredictorTaskManager(DEFAULT_OUTDIR).run_genotype(file, sample_id)
    url = os.path.join(ATLAS_API, callback_url)
    # send_results("genotype", results, url)


@app.route("/analyses", methods=["POST"])
def analyse_new_sample():
    data = request.get_json()
    file = data.get("file", "")
    sample_id = data.get("sample_id", "")
    callback_url = data.get("callback_url", "")
    res = predictor_task.delay(file, sample_id, callback_url)
    res = genotype_task.delay(file, sample_id)
    res = bigsi_build_task.delay(file, sample_id)
    MAPPER.create_mapping(sample_id, sample_id)
    return json.dumps({"result": "success", "task_id": str(res)}), 200


## BIGSI


import hashlib


def _hash(w):
    w = w.encode("utf-8")
    h = hashlib.md5(w)
    return h.hexdigest()[:24]


def filter_bigsi_results(d):
    d["results"] = [x for x in d["results"] if x["genotype"] != "0/0"]
    return d


@celery.task()
def bigsi_query_task(query_type, query, user_id, search_id):
    bigsi_tm = BigsiTaskManager(BIGSI_URL, REFERENCE_FILEPATH, GENBANK_FILEPATH)
    out = {}
    results = {
        "sequence": bigsi_tm.seq_query,
        "dna-variant": bigsi_tm.dna_variant_query,
        "protein-variant": bigsi_tm.protein_variant_query,
    }[query_type](query)
    out = results
    if query_type in ["dna-variant", "protein-variant"]:
        out = filter_bigsi_results(out)
    query_id = _hash(json.dumps(query))
    url = os.path.join(ATLAS_API, "searches", search_id, "results")
    ## TODO filter for non 0/0 before sending!
    send_results(query_type, out, url, request_type="PUT")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    t = data.get("type", "")
    query = data.get("query", "")
    user_id = data.get("user_id", "")
    search_id = data.get("search_id", "")
    res = bigsi_query_task.delay(t, query, user_id, search_id)
    return json.dumps({"result": "success", "task_id": str(res)}), 200


## nearest-neighbour neighbour distance

## Tree
def load_tree(version):
    if version == "latest":
        float_versions = [float(x) for x in sorted(TREE_PATH.keys())]
        version_float_max = max(float_versions)
        float_versions_index = [
            i for i, x in enumerate(float_versions) if x == version_float_max
        ]
        version = list(sorted(TREE_PATH.keys()))[float_versions_index[0]]
        tree_path = TREE_PATH[version]
    with open(tree_path, "r") as infile:
        data = infile.read().replace("\n", "")
    return data


@celery.task()
def tree_task(version):
    assert version == "latest"
    data = load_tree(version)
    url = os.path.join(ATLAS_API, "trees")
    results = {"tree": data, "version": version}
    send_results("tree", results, url)
    return results


@app.route("/tree/<version>", methods=["GET"])
def tree(version):
    results = tree_task(version)
    response = json.dumps({"result": results, "type": "tree"}), 200
    return response


TREE_PATH = {"1.0": TB_TREE_PATH_V1}


def get_tree_isolates():
    newick = load_tree("latest")
    tree = Phylo.read(StringIO(newick), "newick")
    tree_isolates = [c.name for c in tree.get_terminals()]
    return tree_isolates


TREE_ISOLATES = get_tree_isolates()
DEFAULT_MAX_NN_DISTANCE = 100
DEFAULT_MAX_NN_EXPERIMENTS = 1000


@celery.task()
def distance_task(sample_id, callback_url, max_distance=None, limit=None):
    if max_distance is None:
        max_distance = DEFAULT_MAX_NN_DISTANCE
    if limit is None:
        limit = DEFAULT_MAX_NN_EXPERIMENTS
    results = DistanceTaskManager.get_nearest_neighbours(
        sample_id, max_distance=max_distance, limit=limit, sort=True
    )
    requests.post(callback_url, json=results)


@app.route("/distance", methods=["POST"])
def distance():
    data = request.get_json()
    sample_id = data.get("sample_id", "")
    callback_url = data.get("callback_url", "")
    kwargs = data.get("params", {})

    callback_url = os.path.join(ATLAS_API, callback_url)
    res = distance_task.delay(sample_id,  callback_url, **kwargs)
    response = json.dumps({"result": "success", "task_id": str(res)}), 200
    return response


## Mappings from experiment_id to isolate_id
@app.route("/mappings", methods=["GET"])
def mappings():
    mappings = MAPPER.experiment_ids_to_isolate_ids()
    return json.dumps(mappings)


@app.route("/reverse_mappings", methods=["GET"])
def reverse_mappings():
    mappings = MAPPER.isolate_ids_to_experiment_ids()
    return json.dumps(mappings)


## testing experiments requests /experiments/:experiment_id/results
@app.route("/experiments/<experiment_id>/results", methods=["POST"])
def results(experiment_id):
    return request.data, 200


@app.route("/queries/<query_id>/results", methods=["POST"])
def query_results(query_id):
    return request.data, 200


@app.route("/trees", methods=["POST"])
def tree_results():
    return request.data, 200
