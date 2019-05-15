# Setup with minikube

```
minikube start --memory 3500
```

Mount some test data
```
minikube mount /local/path/to/atlas_test_data/:/data/atlas/
# minikube mount ~/Dropbox/Atlas/test_data/exemplar_seqeuence_data/:/data/atlas/
```

```
kubectl create -f k8/redis-deployment.yaml
kubectl create -f k8/atlas

eval $(minikube docker-env)
COMMIT=`git log --pretty=oneline | head -n 1 | cut -f 1 -d ' '`
echo ${COMMIT:0:7} 
docker build -t phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7} . 
# docker push phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7}

kubectl set image deployment/mykrobe-atlas-analysis-api mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7};
kubectl set image deployment/mykrobe-atlas-analysis-worker mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7};
```

## Setup the BIGSI service

Start minikube
```
minikube start
minikube mount /local/path/to/bigis_test_data/bigsi/:/data/bigsi/
# minikube mount ~/Dropbox/Atlas/test_data/bigsi/:/data/bigsi/
```

In this example, the index file is called "test-bigsi-bdb" and will now be available via local filesystem at `/data/bigsi/test-bigsi-bdb` within the minikube VM. 

In order to make this available from within a k8 pod, we first need a volume and volume claim. 

```
## Volume mounts
kubectl create -f k8/bigsi/bigsi-service/pv-volume.yaml
kubectl create -f k8/bigsi/bigsi-service/pv-claim.yaml
```

Now, we can create the deployments and services

```
kubectl create -f k8/bigsi/bigsi-service/bigsi-deployment.yaml
```


## You can test these are working by running 
```
kubectl exec -it mykrobe-atlas-bigsi-deployment-7b77cc49d6-xd2sg /bin/bash
apt-get update -y && apt-get install curl -y
curl localhost/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG 
curl mykrobe-atlas-bigsi-service/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG 
```

BIGSI aggregator requires a redis instance to cache the results from a query and as a celery broker.

```
kubectl create -f k8/redis-deployment.yaml
```

Then create the aggregator service

```
kubectl create -f k8/bigsi/bigsi-aggregator-service/bigsi-aggregator-api-deployment.yaml
```

## Test it's working by running from one of the pods
```
$ curl -X POST  -H "Content-Type: application/json"  -d '{"seq":"CGGCGAGGAAGCGTTAAATCTCTTTCTGACG"}' mykrobe-atlas-bigsi-aggregator-api-service/api/v1/searches/
{"id": "7cddc4de43abdfab233a4a17", "seq": "CGGCGAGGAAGCGTTAAATCTCTTTCTGACG", "threshold": 100, "score": false, "completed_bigsi_queries": 0, "total_bigsi_queries": 1, "results": [], "status": "INPROGRESS"}

$ curl mykrobe-atlas-bigsi-aggregator-api-service/api/v1/searches/7cddc4de43abdfab233a4a17
{"id": "7cddc4de43abdfab233a4a17", "seq": "CGGCGAGGAAGCGTTAAATCTCTTTCTGACG", "threshold": 100, "score": false, "completed_bigsi_queries": 1, "total_bigsi_queries": 1, "results": [{"percent_kmers_found": 100, "num_kmers": "1", "num_kmers_found": "1", "sample_name": "s2", "score": null, "mismatches": null, "nident": null, "pident": null, "length": null, "evalue": null, "pvalue": null, "log_evalue": null, "log_pvalue": null, "kmer-presence": null}, {"percent_kmers_found": 100, "num_kmers": "1", "num_kmers_found": "1", "sample_name": "s1", "score": null, "mismatches": null, "nident": null, "pident": null, "length": null, "evalue": null, "pvalue": null, "log_evalue": null, "log_pvalue": null, "kmer-presence": null}], "status": "COMPLETE"}

## Test variant search
curl -X POST  -H "Content-Type: application/json"  -d '{"reference":"/data/NC_000962.3.fasta", "ref": "G", "pos":100, "alt":"T"}' mykrobe-atlas-bigsi-aggregator-api-service/api/v1/variant_searches/

curl mykrobe-atlas-bigsi-aggregator-api-service/api/v1/variant_searches/f07f794ee9ab1bbc3018a539

## Test Amino Acid variant search
curl -X POST  -H "Content-Type: application/json"  -d '{"reference":"/data/NC_000962.3.fasta", "ref": "S", "pos":450, "alt":"L", "genbank":"/data/NC_000962.3.gb", "gene":"rpoB"}' mykrobe-atlas-bigsi-aggregator-api-service/api/v1/variant_searches/

curl mykrobe-atlas-bigsi-aggregator-api-service/api/v1/variant_searches/0602c248018836fb157cdeef

```

## Test queries 

```
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/MDR.fastq.gz", "experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/analyses
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/INH_monoresistant.fastq.gz", "experiment_id": "INH_monoresistant_test"}' mykrobe-atlas-analysis-api/analyses
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/Mycobacterium_kansasii.bam", "experiment_id": "Mycobacterium_kansasii_test"}' mykrobe-atlas-analysis-api/analyses
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/RIF_monoresistant.fastq.gz", "experiment_id": "RIF_monoresistant_test"}' mykrobe-atlas-analysis-api/analyses
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/XDR.fastq.gz", "experiment_id": "XDR_test"}' mykrobe-atlas-analysis-api/analyses
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/non-mycobacterium_saur.fastq.gz", "experiment_id": "non-mycobacterium_saur_test"}' mykrobe-atlas-analysis-api/analyses
```

## Test distance queries

```
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/distance
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"tree-distance"}' mykrobe-atlas-analysis-api/distance
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"nearest-neighbour"}' mykrobe-atlas-analysis-api/distance

curl mykrobe-atlas-analysis-api/tree/latest
```

## Test BIGSI queries

```

curl -H "Content-Type: application/json" -X POST -d '{"type":"sequence","query":{"seq":"CGGTCAGTCCGTTTGTTCTTGTGGCGAGTGTTGCCGTTTTCTTG",  "user_id": "1234567", "result_id": "2345678" } }' mykrobe-atlas-analysis-api/search

curl -H "Content-Type: application/json" -X POST -d '{"type":"dna-variant","query":{ "ref": "C", "pos":32, "alt":"T"}, "user_id": "1234567"}' mykrobe-atlas-analysis-api/search

curl -H "Content-Type: application/json" -X POST -d '{"type":"protein-variant","query":{ "ref": "S", "pos":450, "alt":"L",  "gene":"rpoB"}, "user_id": "1234567" }' mykrobe-atlas-analysis-api/search

```
