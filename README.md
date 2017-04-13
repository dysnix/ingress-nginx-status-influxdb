## Kubernetes Ingress-Nginx status watcher with sending status to InfluxDB

Simple service for sending aggregated ingress-nginx status from all pods to InfluxDB from
Kubernetes Heapster install (https://github.com/kubernetes/heapster/blob/master/docs/influxdb.md)

### Install

#### Clone repo

    git clone https://github.com/kuberstack/ingress-nginx-status-influxdb.git
  
#### Deploy events monitoring

    kubectl create -f ingress-nginx-status-influxdb/manifestos/