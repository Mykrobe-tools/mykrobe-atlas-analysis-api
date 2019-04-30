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
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumes/pv-volume-for-mykrobe-atlas-bigsi" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI service pv volume: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI service pv volume"
  echo

  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumes/pv-volume-for-mykrobe-atlas-bigsi" \
    -X PATCH -d @k8/bigsi/bigsi-service/pv-volume.json
else
  echo "Creating BIGSI service pv volume"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumes" \
    -X POST -d @k8/bigsi/bigsi-service/pv-volume.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/pv-claim-for-mykrobe-atlas-bigsi" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI service pv claim: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI service pv claim"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/pv-claim-for-mykrobe-atlas-bigsi" \
    -X PATCH -d @k8/bigsi/bigsi-service/pv-claim.json
else
  echo "Creating BIGSI service pv claim"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/persistentvolumeclaims/" \
    -X POST -d @k8/bigsi/bigsi-service/pv-claim.json
fi

echo

# --------------------------------------------------------------

status_code=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-env" \
    -X GET -o /dev/null -w "%{http_code}")

echo
echo "BIGSI env config map status: $status_code"

if [ $status_code == 200 ]; then
  echo "Updating BIGSI env config map"
  echo
  curl -H 'Content-Type: application/strategic-merge-patch+json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps/mykrobe-atlas-bigsi-env" \
    -X PATCH -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-env.json
else
  echo "Creating BIGSI env config map"
  echo

  curl -H 'Content-Type: application/json' -sSk -H "Authorization: Bearer $KUBE_TOKEN" \
    "https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/$NAMESPACE/configmaps" \
    -X POST -d @k8/bigsi/bigsi-service/mykrobe-atlas-bigsi-env.json
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