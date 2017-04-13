import os

# Ingress location
INGRESS_ENDPOINT_LABEL = os.environ.get('INGRESS_ENDPOINT_LABEL', "k8s-addon=ingress-nginx.addons.k8s.io")
INGRESS_STATUS_URL_TEMPLATE = os.environ.get('INGRESS_STATUS_URL_TEMPLATE', "http://{nginx_pod_ip}:18080/nginx_status")

# InfluxDB
INFLUXDB_HOST = os.environ.get('INFLUXDB_HOST', 'monitoring-influxdb.kube-system')
INFLUXDB_PORT = int(os.environ.get('INFLUXDB_PORT', 8086))
INFLUXDB_DB_NAME = os.environ.get('INFLUXDB_DB_NAME', 'k8s')

# Update interval
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 60))

try:
    from local_settings import *
except ImportError:
    pass
