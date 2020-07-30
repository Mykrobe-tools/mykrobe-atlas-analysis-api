import requests
import time
import json
import subprocess
import os
import logging

MAX_POLL_COUNT = 30
POLL_INTERVAL_SECONDS = 1


class BigsiTaskManager:
    def __init__(self, bigsi_api_url, reference_filepath, genbank_filepath, outdir="", bigsi_build_url=""):
        self.bigsi_api_url = bigsi_api_url
        self.bigsi_build_url = bigsi_build_url
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
    def insert_url(self):
        return "/".join([self.bigsi_build_url, "insert"])

    def _query(self, query, search_url):
        r = requests.post(search_url, data=query).json()
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
                return {}
            else:
                time.sleep(POLL_INTERVAL_SECONDS)
        if r["status"] == "COMPLETE":
            return r
        else:
            return {"error": "failed to complete bigsi query"}

    def seq_query(self, query):
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

    def build_bigsi(self, file, sample_id):
        uncleaned_ctx = os.path.join(self.outdir, "{sample_id}_uncleaned.ctx".format(sample_id=sample_id))
        cleaned_ctx = os.path.join(self.outdir, "{sample_id}.ctx".format(sample_id=sample_id))
        bloom = os.path.join(self.outdir, "{sample_id}".format(sample_id=sample_id))
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
                "-1",
                file,
                uncleaned_ctx,
            ]
        logging.log(level=logging.DEBUG, msg="Running: "+" ".join(build_ctx_cmd))
        out = subprocess.check_output(build_ctx_cmd)
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
        try:
            out = requests.post(self.bloom_url, data=bloom_query)
        except requests.exceptions.ConnectionError as e:
            logging.log(level=logging.DEBUG, msg=json.dumps(e))
        insert_query = {
            "bloomfilter": bloom,
            "sample": sample_id,
        }
        logging.log(level=logging.DEBUG, msg="POSTing to {} with {}".format(self.insert_url, json.dumps(insert_query)))
        out = requests.post(self.insert_url, data=insert_query)

