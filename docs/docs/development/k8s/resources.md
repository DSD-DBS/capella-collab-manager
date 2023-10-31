<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

To find out which resources are used in the cluster, you can install a the tool
[`kube-capacity`](https://github.com/robscott/kube-capacity):

```zsh
kubectl krew install resource-capacity
```

When the installation is complete, you can see an overview over the resources
in your namespace:

```zsh
kubectl resource-capacity -n <NAMESPACE> --sort cpu.limit --util --pods
```

One example output looks like:

```zsh
NODE                          POD                                                    CPU REQUESTS   CPU LIMITS    CPU UTIL   MEMORY REQUESTS   MEMORY LIMITS   MEMORY UTIL

k3d-collab-cluster-server-0   *                                                      560m (4%)      2050m (17%)   18m (0%)   85Mi (0%)         1510Mi (5%)     750Mi (2%)
k3d-collab-cluster-server-0   dev-t4c-manager-guacamole-guacamole-84d7b5867d-f9dgj   50m (0%)       500m (4%)     2m (0%)    5Mi (0%)          500Mi (1%)      455Mi (1%)
k3d-collab-cluster-server-0   dev-t4c-manager-oauth-mock-5b94779957-qw2b9            50m (0%)       500m (4%)     1m (0%)    5Mi (0%)          500Mi (1%)      168Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-backend-postgres-76bbc8c6cb-wwmfm      100m (0%)      200m (1%)     6m (0%)    20Mi (0%)         100Mi (0%)      60Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-backend-759bc74f-fxptq                 50m (0%)       200m (1%)     0Mi (0%)   20Mi (0%)         100Mi (0%)      0Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-guacamole-guacd-6cc9b88885-2psq5       50m (0%)       100m (0%)     1m (0%)    5Mi (0%)          50Mi (0%)       11Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-guacamole-postgres-767c4b8b87-2464m    50m (0%)       100m (0%)     10m (0%)   5Mi (0%)          50Mi (0%)       34Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-prometheus-nginx-f5c469d66-mdm5x       50m (0%)       100m (0%)     0m (0%)    5Mi (0%)          50Mi (0%)       2Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-nginx-c6f6557bb-82tpj                  50m (0%)       100m (0%)     0m (0%)    5Mi (0%)          50Mi (0%)       2Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-prometheus-server-64d9bcccb4-ggsj2     50m (0%)       100m (0%)     1m (0%)    5Mi (0%)          50Mi (0%)       18Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-frontend-6bd5977d4b-4zjbr              50m (0%)       100m (0%)     1m (0%)    5Mi (0%)          50Mi (0%)       2Mi (0%)
k3d-collab-cluster-server-0   dev-t4c-manager-docs-fb565dbc7-w8tdg                   10m (0%)       50m (0%)      1m (0%)    5Mi (0%)          10Mi (0%)       2Mi (0%)
```
