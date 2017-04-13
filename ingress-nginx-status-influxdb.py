import datetime
import os
import re
import time
import logging
import requests
from influxdb import InfluxDBClient
from kubernetes import client, config

from settings import UPDATE_INTERVAL, INGRESS_ENDPOINT_LABEL, INGRESS_STATUS_URL_TEMPLATE, INFLUXDB_HOST, INFLUXDB_PORT, \
    INFLUXDB_DB_NAME

# Kubernetes API init
if os.environ.get('DEVELOPMENT_MODE'):
    config.load_kube_config()
else:
    config.load_incluster_config()

kubeapi = client.CoreV1Api()

# InfluxDB init
db = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=INFLUXDB_DB_NAME)


def get_status_urls():
    eps = kubeapi.list_endpoints_for_all_namespaces(label_selector=INGRESS_ENDPOINT_LABEL).items
    if not eps:
        raise BaseException('Ingress Endpoint not found by label %s' % INGRESS_ENDPOINT_LABEL)

    try:
        addresses = eps[0].subsets[0].addresses
    except:
        raise BaseException('Unable to get nginx-ingress endpoints addresses')

    urls = []
    for address in addresses:
        urls.append(INGRESS_STATUS_URL_TEMPLATE.format(nginx_pod_ip=address.ip))

    return urls


def get_nginx_status(url):
    status = {
        'active_connections': None,
        'accepts': None,
        'handled': None,
        'requests': None,
        'reading': None,
        'writing': None,
        'waiting': None,
    }
    try:
        resp = requests.get(url)
    except:
        logging.error('Error getting nginx status by url: %s' % url)
        return None
    text = resp.text

    status['active_connections'] = re.search('^Active connections: (\d+)', text).group(1)
    status['accepts'], status['requests'], status['handled'] = re.search('(\d+) (\d+) (\d+)', text).groups()
    status['reading'], status['writing'], status['waiting'] = re.search('Reading: (\d+) Writing: (\d+) Waiting: (\d+) ',
                                                                        text).groups()

    return status


def get_aggregated_nginx_status():
    aggregated_nginx = {
        'active_connections': 0,
        'accepts': 0,
        'handled': 0,
        'requests': 0,
        'reading': 0,
        'writing': 0,
        'waiting': 0,
    }

    for url in get_status_urls():
        status = get_nginx_status(url)
        aggregated_nginx['active_connections'] += int(status['active_connections'])
        aggregated_nginx['accepts'] += int(status['accepts'])
        aggregated_nginx['handled'] += int(status['handled'])
        aggregated_nginx['requests'] += int(status['requests'])
        aggregated_nginx['reading'] += int(status['reading'])
        aggregated_nginx['writing'] += int(status['writing'])
        aggregated_nginx['waiting'] += int(status['waiting'])

    return aggregated_nginx


def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def send_stats_to_db(db, status):
    json_body = [
        {
            "measurement": "nginx_aggregated_status",
            "tags": {
                "host": "all",
            },
            "time": get_timestamp(),
            "fields": status
        }
    ]
    db.write_points(json_body)


def main():
    try:
        while not time.sleep(UPDATE_INTERVAL):
            aggregated_nginx_status = get_aggregated_nginx_status()
            send_stats_to_db(db, aggregated_nginx_status)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
