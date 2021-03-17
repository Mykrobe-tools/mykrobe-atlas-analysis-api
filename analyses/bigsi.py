import itertools

import requests
import time
import json
import subprocess
import os
import logging

from analyses.tracking import record_event, EventName
from config import MCCORTEX_VERSION
from app import distance_build_task

MAX_POLL_COUNT = 50
POLL_INTERVAL_SECONDS = 3

logger = logging.getLogger(__name__)


class BigsiTaskManager:
    def __init__(self, bigsi_api_url, reference_filepath, genbank_filepath, outdir="", bigsi_build_url="", bigsi_build_config=""):
        self.bigsi_api_url = bigsi_api_url
        self.bigsi_build_url = bigsi_build_url
        self.bigsi_build_config = bigsi_build_config
        self.reference_filepath = reference_filepath
        self.genbank_filepath = genbank_filepath
        self.outdir = outdir

    @property
    def sequence_search_url(self):
        return "/".join([self.bigsi_api_url, "searches/"])

    @property
    def variant_search_url(self):
        return "/".join([self.bigsi_api_url, "variant_searches/"])

    @property
    def prot_variant_search_url(self):
        return "/".join([self.bigsi_api_url, "variant_searches/"])

    @property
    def bloom_url(self):
        return "/".join([self.bigsi_build_url, "bloom"])

    @property
    def build_url(self):
        return "/".join([self.bigsi_build_url, "build"])

    @property
    def merge_url(self):
        return "/".join([self.bigsi_build_url, "merge"])

    def _query(self, query, search_url):
        r = requests.post(search_url, data=query).json()
        if "id" not in r:
            return {"error": "failed to complete bigsi query"}
        _id = r["id"]
        search_result_url = "".join([search_url, _id])
        POLL = True
        counter = 0
        while POLL:
            r = requests.get(search_result_url).json()
            if r["status"] == "COMPLETE":
                POLL = False
                return r
            counter += 1
            if counter > MAX_POLL_COUNT:
                POLL = False
                return {"error": "failed to complete bigsi query"}
            else:
                time.sleep(POLL_INTERVAL_SECONDS)
        if r["status"] == "COMPLETE":
            return r
        else:
            return {"error": "failed to complete bigsi query"}

    def seq_query(self, query):
        logger.info(self.seq_query.__name__)
        logger.debug('query: %s', query)

        search_url = self.sequence_search_url
        # query: {
        #   seq: "GTCAGTCCGTTTGTTCTTGTGGCGAGTGTAGTA",
        #   threshold: 0.9
        # }
        return self._query(query, search_url)

    def dna_variant_query(self, query):
        search_url = self.variant_search_url
        # query: {
        #     ref: "A",
        #     alt: "T",
        #     pos: 450,
        # }
        query["reference"] = self.reference_filepath
        # {"reference":"NC_000962.3.fasta", "ref": "S", "pos":450, "alt":"L"}'
        return self._query(query, search_url)

    def protein_variant_query(self, query):
        # query: {
        #     ref: "S",
        #     alt: "L",
        #     pos: 450,
        #     gene: "rpoB"
        # }
        search_url = self.prot_variant_search_url
        query["reference"] = self.reference_filepath
        query["genbank"] = self.genbank_filepath
        # {"reference":"NC_000962.3.fasta", "ref": "S", "pos":450, "alt":"L", "genbank":"NC_000962.3.gb", "gene":"rpoB"}'
        return self._query(query, search_url)

    def build_bigsi(self, files, sample_id):
        uncleaned_ctx = os.path.join(self.outdir, "{sample_id}_uncleaned.ctx".format(sample_id=sample_id))
        cleaned_ctx = os.path.join(self.outdir, "{sample_id}.ctx".format(sample_id=sample_id))
        bloom = os.path.join(self.outdir, "{sample_id}.bloom".format(sample_id=sample_id))
        bigsi_config_path = os.path.join(self.outdir, "{sample_id}_bigsi.config".format(sample_id=sample_id))
        bigsi_db_path = os.path.join(self.outdir, "{sample_id}_bigsi.db".format(sample_id=sample_id))

        files_with_flags = list(itertools.chain.from_iterable([("-1", f) for f in files]))

        build_ctx_cmd = [
                "mccortex31",
                "build",
                "-f",
                "-k",
                str(31),
                "-s",
                sample_id,
                "--fq-cutoff",
                str(5),
            ] + files_with_flags + [
                uncleaned_ctx,
            ]
        logging.log(level=logging.DEBUG, msg="Running: "+" ".join(build_ctx_cmd))

        start_time = time.time_ns()
        out = subprocess.check_output(build_ctx_cmd)
        duration = int((time.time_ns() - start_time) / 1000)

        record_event(sample_id, EventName.BIGSI_BUILDING, software='mccortex31', software_version=MCCORTEX_VERSION,
                     start_timestamp=start_time, duration=duration, command=' '.join(build_ctx_cmd))

        clean_ctx_cmd = [
                "mccortex31",
                "clean",
                "--fallback",
                str(5),
                "--out",
                cleaned_ctx,
                uncleaned_ctx,
            ]
        logging.log(level=logging.DEBUG, msg="Running: {}".format(" ".join(clean_ctx_cmd)))
        out = subprocess.check_output(clean_ctx_cmd)

        bloom_query = {
            "ctx": cleaned_ctx,
            "outfile": bloom,
        }
        logging.log(level=logging.DEBUG, msg="POSTing to {} with {}".format(self.bloom_url, json.dumps(bloom_query)))
        self._requests_post(self.bloom_url, bloom_query)
        self._wait_until_available(bloom)

        distance_build_task.delay(bloom, sample_id)

        with open(bigsi_config_path, "w") as conf:
            conf.write("h: 1\n")
            conf.write("k: 31\n")
            conf.write("m: 28000000\n")
            conf.write("nproc: 1\n")
            conf.write("storage-engine: berkeleydb\n")
            conf.write("storage-config:\n")
            conf.write("  filename: {}\n".format(bigsi_db_path))
            conf.write("  flag: \"c\"")
        self._wait_until_available(bigsi_config_path)
        build_query = {
            "bloomfilters": [bloom],
            "samples": [sample_id],
            "config": bigsi_config_path
        }
        logging.log(level=logging.DEBUG, msg="POSTing to {} with {}".format(self.build_url, json.dumps(build_query)))
        self._requests_post(self.build_url, build_query)
        self._wait_until_available(bigsi_db_path)

        merge_query = {
            "config": self.bigsi_build_config,
            "merge_config": bigsi_config_path
        }
        logging.log(level=logging.DEBUG, msg="POSTing to {} with {}".format(self.merge_url, json.dumps(merge_query)))
        self._requests_post(self.merge_url, merge_query)

        logging.log(level=logging.DEBUG, msg="build_bigsi complete")

    def _wait_until_available(self, file_path, max_wait_time=128):
        # temporary hack, due to slow disk, the file may take some time to appear
        wait_time = 1
        while not os.path.exists(file_path) and \
                wait_time <= max_wait_time:
            time.sleep(wait_time)
            wait_time = wait_time * 2
        wait_time = 10
        while os.path.getmtime(file_path) + 100 > time.time():
            time.sleep(wait_time)

    def _requests_post(self, url, data):
        # Some of the call takes longer than 1 minute due to slow disk. Bigsi disconnects the call after 1 minute (todo)
        # Temporary hack
        try:
            requests.post(url, data)
        except requests.exceptions.ConnectionError as e:
            logging.log(level=logging.DEBUG, msg="Exception thrown when calling {} with data {}: {}".format(
                url, json.dumps(data), str(e)))

