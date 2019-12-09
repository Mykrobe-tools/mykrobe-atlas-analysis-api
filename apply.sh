#!/usr/bin/env bash

# DIR where the current script resides
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

kubectl create secret docker-registry \
dockerhub \
  --namespace default \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=msreadonly \
  --docker-password=nnzGTbYRry9Fwpra \
  --docker-email=readonly@makeandship.com

kubectl apply -k ${DIR}/mykrobe-atlas-api-k8/static-embassy
#kubectl apply -k ${DIR}/mykrobe-atlas-k8/static-embassy
#kubectl apply -k ${DIR}/mykrobe-atlas-analysis-api/k8

# Debug code
function applyall () {
  local _mfs=( "$@" )

  for file in "${_mfs[@]}"; do
    kubectl apply -f ${file}
  done
}
#applyall ${DIR}/mykrobe-atlas-api-k8/static-embassy/*.json

kubectl rollout status deployment.apps/atlas-api-deployment --timeout=60m

kubectl get pv
kubectl get all