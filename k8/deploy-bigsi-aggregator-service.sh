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
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-aggregator-env" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI aggregator env config map status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI aggregator env config map"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-aggregator-env" \
    -X PATCH -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-env.json
else
  echo "Creating BIGSI aggregator env config map"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps" \
    -X POST -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-env.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-aggregator-api-deployment" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "BIGSI aggregator service deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI aggregator service deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-aggregator-api-deployment" \
    -X PATCH -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-api-deployment.json
else
  echo "Creating BIGSI aggregator service deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-api-deployment.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-aggregator-worker" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "BIGSI aggregator service worker deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI aggregator service worker deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-aggregator-worker" \
    -X PATCH -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-worker.json
else
  echo "Creating BIGSI aggregator service worker deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-worker.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/services/mykrobe-atlas-bigsi-aggregator-api-service" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI aggregator service status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI aggregator service"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/services/mykrobe-atlas-bigsi-aggregator-api-service" \
    -X PATCH -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-api-service.json
else
  echo "Creating BIGSI aggregator service"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/services" \
    -X POST -d @k8/bigsi/bigsi-aggregator-service/mykrobe-atlas-bigsi-aggregator-api-service.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/extensions/v1beta1/namespaces/$NAMESPACE/ingresses/bigsi-aggregator-ingress" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI aggregator ingress status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI ingress service"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/extensions/v1beta1/namespaces/$NAMESPACE/ingresses/bigsi-aggregator-ingress" \
    -X PATCH -d @k8/bigsi/bigsi-aggregator-service/bigsi-ingress.json
else
  echo "Creating BIGSI ingress service"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/extensions/v1beta1/namespaces/$NAMESPACE/services" \
    -X POST -d @k8/bigsi/bigsi-aggregator-service/bigsi-ingress.json
fi

echo