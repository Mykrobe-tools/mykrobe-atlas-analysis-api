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
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-config" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI config config map status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI config config map"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-config" \
    -X PATCH -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-config.json
else
  echo "Creating BIGSI config config map"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps" \
    -X POST -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-config.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-deployment" \
    -X GET -o /dev/null -w "%{http_code}")
echo

echo "BIGSI service deployment status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI service deployment"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments/mykrobe-atlas-bigsi-deployment" \
    -X PATCH -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-deployment.json
else
  echo "Creating BIGSI service deployment"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/apis/apps/v1beta1/namespaces/$NAMESPACE/deployments" \
    -X POST -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-deployment.json
fi