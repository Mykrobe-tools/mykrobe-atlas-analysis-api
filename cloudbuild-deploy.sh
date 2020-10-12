#!/bin/bash

TOKEN=$(cat /workspace/ehk-token.txt)
API_VERSION=$(cat /workspace/api_version.txt)
WORKER_VERSION=$(cat /workspace/worker_version.txt)
curl -XPATCH 'https://45.86.170.176:6443/apis/apps/v1beta2/namespaces/mykrobe-dev/deployments/analysis-api' \
-H "Authorization: Bearer $TOKEN" \
-H 'Content-type: application/json-patch+json' \
-d "[{ \"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/image\", \"value\": \"$API_VERSION\" }]" \
--insecure
curl -XPATCH 'https://45.86.170.176:6443/apis/apps/v1beta2/namespaces/mykrobe-dev/deployments/analysis-api-worker' \
-H "Authorization: Bearer $TOKEN" \
-H 'Content-type: application/json-patch+json' \
-d "[{ \"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/image\", \"value\": \"$WORKER_VERSION\" }]" \
--insecure
