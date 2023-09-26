<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Install the Collaboration Manager

This guide will help you set up the Capella Collaboration Manager on a
Kubernetes cluster. The setup of the basic installation is straightforward, but
we'll also delve into the more complex TeamForCapella support that requires
building custom Docker images.

During development, we also took into account that the application can be
installed in highly restricted environments. An internet connection is not
necessarily required.

## Step 1: Set up a Kubernetes cluster

Kubernetes allows us to make operations as simple as possible later on. Updates
can be fully automated. In addition, Kubernetes allows us to ensure a secure
operation through standardized security hardening.

You can use an existing cloud service to create a Kubernetes cluster. We have
running production deployments on Microsoft AKS and Amazon EKS. The application
is designed in such a way that no cluster scope is necessary. All operations
run at the namespace level, so it even runs in shared OpenShift clusters. But
even if you simply have a Linux server at your disposal, this is no obstacle.
Setting up a cluster is easier than you think.

If you already have a running cluster, have `kubectl` up and running and can
reach the cluster, then you can skip this step.

We provide instructions for some environments. If you set up the application in
a different environment, we would be happy to receive a PR to help other users
in the future.

=== "microK8s"

    !!! info
        We have tested the instructions with Ubuntu Server 22.04.

    1. Run steps 1-4 of the official microK8s [`Getting started`](https://microk8s.io/docs/getting-started) guide.

    2. Enable all required add-ons:
        ```zsh
        microk8s enable hostpath-storage # For workspace storage
        microk8s enable rbac # For role-based access control
        microk8s enable ingress # For load balancing
        ```
    3. If you don't have any external registry available and TeamForCapella support is required, enable the registry:
        ```zsh
        microk8s enable registry
        ```
    4. Copy the `kubectl` configuration to the host, so that `helm` can pick it up:
        ```zsh
        mkdir -p $HOME/.kube
        microk8s config > $HOME/.kube/config
        chmod 600 $HOME/.kube/config # Nobody else should be able to read the configuration
        ```

=== "k3d"

    We are constantly working on expanding our documentation. This installation method is currently not documented. If it is relevant, please feel free to contact us at set@deutschebahn.com.

=== "OpenShift"

    We are constantly working on expanding our documentation. This installation method is currently not documented. If it is relevant, please feel free to contact us at set@deutschebahn.com.

## Step 2: Validate the available resources

The minimum required resources are 3
[Kubernetes CPU cores](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu)
and around 2,5GiB of memory for the management platform. Depending on the load,
the instance can scale up and is limited to 10 Kubernetes CPU cores cores and
~8GiB of memory.

Each session requires a minimum of 0.4 Kubernetes CPU cores and 1.6Gi of
memory. A session can scale up until it reaches 2 Kubernetes CPU cores and 6Gi
of memory.

## Step 2: Set up the required namespaces (optional)

The Collaboration Manager requires two different namespaces. For security and
overview reasons, they are separated:

<!-- prettier-ignore -->
- Capella Collaboration Manager control namespace: In this namespace, we run
  the core application. It has full control over the sessions namespace and  consists of the following services:
    - Frontend
    - Backend
    - Documentation
    - Guacamole
    - Prometheus
    - Grafana (Loki), can be disabled in the `values.yaml`

- Sessions namespace. The namespace is controlled by the control namespace and you won't need to touch it. In the session namespace, the following services run:
    - Storage for persistent workspaces
    - Storage for Juypter file-shares
    - Pipeline jobs for nightly TeamForCapella to Git synchronisation
    - Session containers (Capella, Papyrus, Juypter, pure::variants)

<!-- prettier-ignore -->
1. Create the two required namespaces:

    ```zsh
    kubectl create namespace collab-manager # If you use another name, please update the following commands and use your namespace name.
    kubectl create namespace collab-sessions # If you use another name, please update the `values.yaml` accordingly.
    ```

2. Set the `collab-manager` as default namespace in the default context (optional):

    ```zsh
    kubectl config set-context --current --namespace=collab-manager
    ```

## Step 3: Install helm

Follow the official instructions to install Helm:
[Installing helm](https://helm.sh/docs/intro/install/)

Verify that `helm` is working by executing the command:

```zsh
helm version
```

## Step 4: Clone the Github repository

Navigate to a persistent location on your server, e.g. `/opt`. Then clone the
Github repository by running:

```zsh
git clone https://github.com/DSD-DBS/capella-collab-manager.git
```

## Step 5: Configure the environment / Create the `values.yaml`

Copy the
[`values.yaml`](https://github.com/DSD-DBS/capella-collab-manager/blob/main/helm/values.yaml)
to a persistent and secure location on your server or deploment environment.
The `local` directory in the Collaboration Manager is gitignored. We recommend
to put the custom `values.yaml` in this directory.

Adjust all values according to your needs.

## Step 6: Install the application in the cluster

Run the following commands in the root directory of the repository:

```zsh
helm dependency update ./helm
helm upgrade --install \
    --namespace collab-manager \
    --values <path-to-your-custom-values.yaml> \
    <release-name> \
    ./helm
```

## Step 7: Initialize the Guacamole database

The Guacamole database is not initialized per default, it has do be done
manually. Run the following command to initialize the PostgreSQL database:

```zsh
kubectl exec --container prod-guacamole-guacamole deployment/prod-guacamole-guacamole -- /opt/guacamole/bin/initdb.sh --postgresql | \
    kubectl exec -i deployment/prod-guacamole-postgres -- psql -U guacamole guacamole
```

## Step 8: Check the application status

Run `kubectl get pods` to see the status of all components. Once all containers
are running, verify the installation state by running:

```zsh
curl http://localhost/api/v1/health/general
```

It should return the following JSON:

```json
{ "guacamole": true, "database": true, "operator": true }
```

If a value is false, check the backend logs for more information.
