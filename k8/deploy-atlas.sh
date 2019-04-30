if [ -z $KUBE_TOKEN ]; then
  echo "FATAL: Environment Variable KUBE_TOKEN must be specified."
  exit ${2:-1}
fi

if [ -z $NAMESPACE ]; then
  echo "FATAL: Environment Variable NAMESPACE must be specified."
  exit ${2:-1}
fi

if [ -z $KUBERNETES_SERVICE_HOST ]; then
  echo "FATAL: Environment Variable KUBERNETES_SERVICE_HOST must be specified."
  exit ${2:-1}
fi

if [ -z $KUBERNETES_PORT_443_TCP_PORT ]; then
  echo "FATAL: Environment Variable KUBERNETES_PORT_443_TCP_PORT must be specified."
  exit ${2:-1}
fi

# --------------------------------------------------------------

echo
echo "Namespace: $NAMESPACE"
echo "Service host: $KUBERNETES_SERVICE_HOST"
echo "Service port: $KUBERNETES_PORT_443_TCP_PORT"

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/persistentvolumes/pv-volume-for-atlas" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "Atlas persistent volume: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating Atlas persistent volume"
  echo

  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/persistentvolumes/pv-volume-for-atlas" \
    -X PATCH -d @k8/atlas/persistent-volume.json
else
  echo "Creating Atlas persistent volume"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/persistentvolumes" \
    -X POST -d @k8/atlas/persistent-volume.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/pv-claim-for-atlas" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "Atlas persistent volume claim: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating Atlas persistent volume claim"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/pv-claim-for-atlas" \
    -X PATCH -d @k8/atlas/persistent-volume-claim.json
else
  echo "Creating Atlas persistent volume claim"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/" \
    -X POST -d @k8/atlas/persistent-volume-claim.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/env" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "Atlas env config map status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating Atlas env config map"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/env" \
    -X PATCH -d @k8/atlas/env.json
else
  echo "Creating Atlas env config map"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps" \
    -X POST -d @k8/atlas/env.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-api" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "BIGSI aggregator service worker deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI aggregator service worker deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-api" \
    -X PATCH -d @k8/atlas/mykrobe-atlas-analysis-api.json
else
  echo "Creating BIGSI aggregator service worker deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/atlas/mykrobe-atlas-analysis-api.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-api" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "Analysis API deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating Analysis API deployment deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-api" \
    -X PATCH -d @k8/atlas/mykrobe-atlas-analysis-api.json
else
  echo "Creating Analysis API deployment deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/atlas/mykrobe-atlas-analysis-api.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-worker" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "Analysis worker deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating Analysis worker deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-analysis-worker" \
    -X PATCH -d @k8/atlas/mykrobe-atlas-analysis-worker.json
else
  echo "Creating Analysis worker deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/atlas/mykrobe-atlas-analysis-worker.json
fi

echo