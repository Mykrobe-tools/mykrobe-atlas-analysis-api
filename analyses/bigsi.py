import requests
import time
from json import JSONDecodeError

MAX_POLL_COUNT = 30 * 10
POLL_INTERVAL_SECONDS = 1


class BigsiTaskManager:
    def __init__(self, bigsi_api_url, reference_filepath, genbank_filepath):
        self.bigsi_api_url = bigsi_api_url
        self.reference_filepath = reference_filepath
        self.genbank_filepath = genbank_filepath

    @property
    def sequence_search_url(self):
        return "/".join([self.bigsi_api_url, "searches/"])

    @property
    def variant_search_url(self):
        return "/".join([self.bigsi_api_url, "variant_searches/"])

    @property
    def prot_variant_search_url(self):
        return "/".join([self.bigsi_api_url, "variant_searches/"])

    def search_result_url(self, id):
        return "".join([self.search_url, id])

    def _query(self, query, search_url):
        r = requests.post(search_url, data=query).json()
        _id = r["id"]
        search_result_url = "".join([search_url, id])
        POLL = True
        counter = 0
        while POLL:
            r = requests.get(search_result_url(_id)).json()
            if r["status"] == "COMPLETE":
                POLL = False
                return r
            counter += 0
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
        search_url = self.sequence_search_url
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
        search_url = self.sequence_search_url
        query["reference"] = self.reference_filepath
        query["genbank"] = self.genbank_filepath
        # {"reference":"NC_000962.3.fasta", "ref": "S", "pos":450, "alt":"L", "genbank":"NC_000962.3.gb", "gene":"rpoB"}'
        return self._query(query, search_url)
