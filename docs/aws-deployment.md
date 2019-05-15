# Setup with minikube

```

sudo adduser atlas
sudo usermod -aG sudo atlas

sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
sudo apt-get update && sudo apt-get install docker.io -y
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/

grep -E "^nameserver" /run/systemd/resolve/resolv.conf |head -n 3 > /tmp/resolv.conf
sudo minikube start --vm-driver=none --extra-config=kubelet.resolv-conf=/tmp/resolv.conf

```

Mount some test data. Minikube doesn't work on AWS with --vm-driver=none. 
```
## minikube mount /ssd0/:/data/atlas/
Update k8/atlas/persistent-volume.yaml to /ssd0/atlas
Update k8/atlas/persistent-volume.yaml to /ssd0/bigsi
```

```
kubectl create -f k8/redis-deployment.yaml
kubectl create -f k8/atlas
```

## Setup the BIGSI service

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
kubectl exec -it mykrobe-atlas-bigsi-deployment-546888c6bd-tcz9s /bin/bash
apt-get update -y && apt-get install curl -y
curl localhost/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG 
curl bigsi-1-service/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG 
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
sudo kubectl exec -it redis-0 /bin/bash

$ curl -X POST  -H "Content-Type: application/json"  -d '{"seq":"CGGCGAGGAAGCGTTAAATCTCTTTCTGACG"}' mykrobe-atlas-bigsi-aggregator-api-service/api/v1/searches/
{"id": "7cddc4de43abdfab233a4a17", "seq": "CGGCGAGGAAGCGTTAAATCTCTTTCTGACG", "threshold": 100, "score": false, "completed_bigsi_queries": 0, "total_bigsi_queries": 1, "results": [], "status": "INPROGRESS"}

$ curl mykrobe-atlas-bigsi-aggregator-api-service/api/v1/searches/7cddc4de43abdfab233a4a17
{"id": "7cddc4de43abdfab233a4a17", "seq": "CGGCGAGGAAGCGTTAAATCTCTTTCTGACG", "threshold": 100, "score": false, "completed_bigsi_queries": 1, "total_bigsi_queries": 1, "results": [{"percent_kmers_found": 100, "num_kmers": "1", "num_kmers_found": "1", "sample_name": "s2", "score": null, "mismatches": null, "nident": null, "pident": null, "length": null, "evalue": null, "pvalue": null, "log_evalue": null, "log_pvalue": null, "kmer-presence": null}, {"percent_kmers_found": 100, "num_kmers": "1", "num_kmers_found": "1", "sample_name": "s1", "score": null, "mismatches": null, "nident": null, "pident": null, "length": null, "evalue": null, "pvalue": null, "log_evalue": null, "log_pvalue": null, "kmer-presence": null}], "status": "COMPLETE"}
```

## Test queries 

```
curl -H "Content-Type: application/json" -X POST -d '{"file":"/data/exemplar_seqeuence_data/MDR.fastq.gz", "experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/analyses
```

### Distance queries 
```
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test"}' mykrobe-atlas-analysis-api/distance
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"tree-distance"}' mykrobe-atlas-analysis-api/distance
curl -H "Content-Type: application/json" -X POST -d '{"experiment_id": "MDR_test", "distance_type":"nearest-neighbour"}' mykrobe-atlas-analysis-api/distance

curl mykrobe-atlas-analysis-api/tree/latest


```

## Update image
sudo kubectl set image deployment/mykrobe-atlas-analysis-api mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:c53ab32;
sudo kubectl set image deployment/mykrobe-atlas-analysis-worker mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:c53ab32;

