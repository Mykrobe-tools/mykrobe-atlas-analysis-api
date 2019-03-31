# Setup with minikube

```
minikube start
kubectl create -f kubs/


eval $(minikube docker-env)
COMMIT=`git log --pretty=oneline | head -n 1 | cut -f 1 -d ' '`

docker build -t phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7} . 

kubectl set image deployment/analysis-api mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7};
kubectl set image deployment/analysis-worker mykrobe-atlas-analysis=phelimb/mykrobe-atlas-analysis-api:${COMMIT:0:7};
```

Setup the BIGSI service
```
## BIGSI config
kubectl create -f kubs/bigsi/bigsi-service/bigsi-config.yaml
kubectl create -f kubs/bigsi/bigsi-service/env.yaml
## Volume mounts
kubectl create -f kubs/bigsi/bigsi-service/pv-volume.yaml ## This needs to be updated to use a local path! 
kubectl create -f kubs/bigsi/bigsi-service/pv-claim.yaml
## BIGSI API services
kubectl create -f kubs/bigsi/bigsi-service/bigsi-service.yaml
kubectl create -f kubs/bigsi/bigsi-service/bigsi-deployment.yaml
## You can test these are working by running 

kubectl exec -it bigsi-1-deployment-f6c8c9c5-76nzt 
curl localhost:8001/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG 
###(after installing curl if required)

## nginx reverse proxy config + service (this is the where the bigsi-aggregator service will send requests)
kubectl create configmap bigsi-1-nginx-configmap --from-file kubs/bigsi/bigsi-service/nginx/nginx.conf
kubectl create -f kubs/bigsi/bigsi-service/nginx/nginx-service.yaml
kubectl create -f kubs/bigsi/bigsi-service/nginx/nginx-deployment.yaml

## kubectl exec -it bigsi-1-nginx-deployment-7dd488b66c-52kkv
## curl localhost/search?seq=CGGCGAGGAAGCGTTAAATCTCTTTCTGACG
## (after installing curl if required)

kubectl create -f kubs/bigsi/bigsi-aggregator-service/env.yaml
kubectl create -f kubs/bigsi/bigsi-aggregator-service/bigsi-aggregator-service.yaml
kubectl create -f kubs/bigsi/bigsi-aggregator-service/bigsi-aggregator-api-deployment.yaml
kubectl create -f kubs/bigsi/bigsi-aggregator-service/bigsi-aggregator-worker-deployment.yaml
kubectl create configmap bigsi-aggregator-nginxconfigmap --from-file kubs/bigsi/bigsi-aggregator-service/nginx/nginx.conf
kubectl create -f kubs/bigsi/bigsi-aggregator-service/nginx/nginx-service.yaml
kubectl create -f kubs/bigsi/bigsi-aggregator-service/nginx/nginx-deployment.yaml





```