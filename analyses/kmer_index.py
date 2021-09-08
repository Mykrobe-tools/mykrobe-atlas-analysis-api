import itertools

import requests
import time
import json
import subprocess
import os
import logging

from analyses.tracking import record_event, EventName
from config import MCCORTEX_VERSION


logger = logging.getLogger(__name__)


class KmerIndexTaskManager:
    def __init__(self, kmer_search_api_url, reference_filepath, genbank_filepath, outdir="", kmer_index_build_url=""):
        self.kmer_search_api_url = kmer_search_api_url
        self.kmer_index_build_url = kmer_index_build_url
        self.reference_filepath = reference_filepath
        self.genbank_filepath = genbank_filepath
        self.outdir = outdir

    @property
    def sequence_search_url(self):
        return "/".join([self.kmer_search_api_url, "search"])

    @property
    def variant_search_url(self):
        return "/".join([self.kmer_search_api_url, "variant_search"])

    @property
    def prot_variant_search_url(self):
        return "/".join([self.kmer_search_api_url, "variant_search"])

    @property
    def build_url(self):
        return "/".join([self.kmer_index_build_url, "build"])

    def _query(self, query, search_url):
        return requests.post(search_url, json=query, headers={'Content-type': 'application/json'}).json()


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

    def build_kmer_index(self, files, sample_id, callback_url, kwargs):
        uncleaned_ctx = os.path.join(self.outdir, "{sample_id}_uncleaned.ctx".format(sample_id=sample_id))
        cleaned_ctx = os.path.join(self.outdir, "{sample_id}.ctx".format(sample_id=sample_id))

        files_with_flags = list(itertools.chain.from_iterable([("-1", f) for f in files]))

        build_ctx_cmd = [
                            "mccortex31",
                            "build",
                            "-f",
                            "-k",
                            str(31),
                            "-m",
                            "1GB",
                            "-s",
                            sample_id,
                            "--fq-cutoff",
                            str(5),
                        ] + files_with_flags + [
                            uncleaned_ctx,
                        ]
        logging.log(level=logging.DEBUG, msg="Running: " + " ".join(build_ctx_cmd))

        start_time = time.time()
        out = subprocess.check_output(build_ctx_cmd)
        duration = int((time.time() - start_time) * 1000)

        record_event(sample_id, EventName.BIGSI_BUILDING, software='mccortex31', software_version=MCCORTEX_VERSION,
                     start_timestamp=start_time, duration=duration, command=' '.join(build_ctx_cmd))

        clean_ctx_cmd = [
            "mccortex31",
            "clean",
            "--fallback",
            str(5),
            "-m",
            "1GB",
            "--out",
            cleaned_ctx,
            uncleaned_ctx,
        ]
        logging.log(level=logging.DEBUG, msg="Running: {}".format(" ".join(clean_ctx_cmd)))
        out = subprocess.check_output(clean_ctx_cmd)

        # self._trigger_distance_build_task(bloom, sample_id, callback_url, kwargs)

        build_query = {
            "bloomfilters": [bloom],
            "samples": [sample_id],
            "config": bigsi_config_path
        }
        logging.log(level=logging.DEBUG, msg="POSTing to {} with {}".format(self.build_url, json.dumps(build_query)))
        self._requests_post(self.build_url, build_query)
        self._wait_until_available(bigsi_db_path)

        logging.log(level=logging.DEBUG, msg="build_kmer_index cleaning up")
        # We can not remove the new bigsi db and config file because the merge can be still
        # ongoing at this point. We can not remove the bloom filters either as that will be
        # used for calculating distance
        os.remove(uncleaned_ctx)
        os.remove(cleaned_ctx)

        logging.log(level=logging.DEBUG, msg="build_bigsi complete")

    def _trigger_distance_build_task(self, bloom, sample_id, callback_url, kwargs):
        from app import distance_build_task  # TODO: refactor this to remove cyclic dependency
        distance_build_task.delay(bloom, sample_id, callback_url, kwargs)

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
