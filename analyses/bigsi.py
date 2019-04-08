import requests
import time
from json import JSONDecodeError

class BigsiTaskManager:
    def __init__(self, bigsi_api_url):
        self.bigsi_api_url=bigsi_api_url

    @property
    def search_url(self):
        return "/".join([self.bigsi_api_url, 'searches/'])
    
    def search_result_url(self, id):
        return "".join([self.search_url, id]) 

    def seq_query(self, query):
        r = requests.post(self.search_url, data = query).json()
        _id=r["id"]
        POLL=True
        counter=0
        while POLL:
            r=requests.get(self.search_result_url(_id)).json()
            if r["status"] == "COMPLETE":
                POLL=False
                return r
            counter+=0
            if counter > 30*10:
                POLL=False
                return {}
            else:
                time.sleep(1)
            

    def dna_variant_query(self, query):
        raise NotImplementedError

    def protein_variant_query(self, query):
        raise NotImplementedError