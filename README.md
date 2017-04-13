## Kubernetes Ingress-Nginx status watcher with sending status to InfluxDB

Light. Simple. Fast.

### Notification transports support

* Slack

### Install

#### Clone repo

    git clone https://github.com/kuberstack/ingress-nginx-status-influxdb.git
  
#### Deploy events monitoring

    kubectl create -f ingress-nginx-status-influxdb/manifestos/