# File upload

### Trigger initial analysis
```
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/exemplar_seqeuence_data/MDR.fastq.gz", "experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/analyses
```

Response
The analysis engine will 1) Run predictor and post results, 2) Run genotype 3) Run nearest neighbour and tree distance search and POST the results

# Distance queries 

### Standard distance query (against all)
```
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/distance
```

### Tree distance
```
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"tree-distance"}' mykrobe-atlas-analysis-api/distance
```

### Nearest Neighbour
```
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"nearest-neighbour"}' mykrobe-atlas-analysis-api/distance
```



# Search queries


### Sequence search
Query
```
curl -H "Content-Type: application/json" -X POST -d '{"type":"sequence","query":{"seq":"CGGTCAGTCCGTTTGTTCTTGTGGCGAGTGTTGCCGTTTTCTTG"},  "user_id": "1234567", "result_id": "2345678"  }' mykrobe-atlas-analysis-api/search
```
Response
```
{"type": "sequence", "result": {"id": "9ecbe21751913c0788b2e13a", "seq": "CGGTCAGTCCGTTTGTTCTTGTGGCGAGTGTTGCCGTTTTCTTG", "threshold": 100, "score": false, "completed_bigsi_queries": 1, "total_bigsi_queries": 1, "results": [{"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/RIF_monoresistant.bloom", "percent_kmers_found": 100, "num_kmers_found": "14", "num_kmers": "14", "score": null, "mismatches": null, "nident": null, "pident": null, "length": null, "evalue": null, "pvalue": null, "log_evalue": null, "log_pvalue": null, "kmer-presence": null}], "status": "COMPLETE", "citation": "http://dx.doi.org/10.1038/s41587-018-0010-1"}}'
```

### DNA variant query
Query
```
curl -H "Content-Type: application/json" -X POST -d '{"type":"dna-variant","query":{ "ref": "C", "pos":32, "alt":"T"}, "user_id": "1234567", "result_id": "2345678" }' mykrobe-atlas-analysis-api/search
```

Response
```
{"type": "dna-variant", "result": {"id": "f8198c6b19d99197e7a091e8", "reference": "/data/NC_000962.3.fasta", "ref": "C", "pos": 32, "alt": "T", "genbank": null, "gene": null, "completed_bigsi_queries": 3, "total_bigsi_queries": 1, "results": [{"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/XDR.bloom", "genotype": "0/0"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/RIF_monoresistant.bloom", "genotype": "0/0"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR_1.bloom", "genotype": "0/0"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR.bloom", "genotype": "0/0"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/INH_monoresistant.bloom", "genotype": "0/0"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR_2.bloom", "genotype": "0/0"}], "status": "COMPLETE", "citation": "http://dx.doi.org/10.1038/s41587-018-0010-1"}}
```

### Prot variant query

Query
```
curl -H "Content-Type: application/json" -X POST -d '{"type":"protein-variant","query":{ "ref": "S", "pos":450, "alt":"L",  "gene":"rpoB"}, "user_id": "1234567", "result_id": "2345678"  }' mykrobe-atlas-analysis-api/search
```

Reponse
```
{"type": "protein-variant", "result": {"id": "0602c248018836fb157cdeef", "reference": "/data/NC_000962.3.fasta", "ref": "S", "pos": 450, "alt": "L", "genbank": "/data/NC_000962.3.gb", "gene": "rpoB", "completed_bigsi_queries": 2, "total_bigsi_queries": 1, "results": [{"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/XDR.bloom", "genotype": "1/1"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/RIF_monoresistant.bloom", "genotype": "0/1"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR_1.bloom", "genotype": "1/1"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR.bloom", "genotype": "1/1"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/INH_monoresistant.bloom", "genotype": "0/1"}, {"sample_name": "/Users/phelimb/Dropbox/Atlas/test_data/bigsi/bloom/MDR_2.bloom", "genotype": "1/1"}], "status": "COMPLETE", "citation": "http://dx.doi.org/10.1038/s41587-018-0010-1"}}
```
