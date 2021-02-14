#!/bin/bash

kubectl create namespace hw9
kubectl config set-context --current --namespace=hw9
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install rabbitmq -f ./rabbitmq/values.yaml bitnami/rabbitmq --atomic
helm install --timeout 60s billing ./billing\ service/billing-chart --atomic
helm install --timeout 60s warehouse ./warehouse\ service/warehouse-chart --atomic
helm install --timeout 60s shipping ./shipping\ service/shipping-chart --atomic
helm install --timeout 60s order ./order\ service/order-chart --atomic
