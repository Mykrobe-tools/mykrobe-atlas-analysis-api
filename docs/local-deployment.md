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